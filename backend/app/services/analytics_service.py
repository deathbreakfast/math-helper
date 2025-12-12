"""Analytics service for dashboard metrics, time-series aggregation, and streak calculations."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from sqlalchemy import case, func

from ..database import log_query, transaction
from ..models import DailyStat, Question, Response, db
from .analytics import OperationStatsBuilder, StreakCalculator, WeeklyGainCalculator


class AnalyticsService:
    """Service for analytics and dashboard metrics."""

    @staticmethod
    @log_query
    def compute_user_metrics(user_id: int) -> dict[str, Any]:
        """Compute comprehensive metrics for a user."""
        total_answers = (
            db.session.query(func.count())
            .select_from(Response)
            .filter_by(user_id=user_id)
            .scalar()
            or 0
        )

        avg_duration_ms = (
            db.session.query(func.avg(Response.duration_ms))
            .filter(Response.user_id == user_id, Response.duration_ms.isnot(None))
            .scalar()
        )

        last_activity_at = (
            db.session.query(func.max(Response.answered_at)).filter_by(user_id=user_id).scalar()
        )

        operation_rows = (
            db.session.query(
                Question.operation.label("operation"),
                func.count(Response.id).label("attempts"),
                func.sum(case((Response.is_correct.is_(True), 1), else_=0)).label("correct"),
                func.avg(Response.duration_ms).label("avg_duration_ms"),
            )
            .join(Response.question)
            .filter(Response.user_id == user_id)
            .group_by(Question.operation)
            .all()
        )

        operation_stats = OperationStatsBuilder.build(operation_rows)
        streaks = StreakCalculator.calculate_streaks(user_id)

        return {
            "questions_answered": total_answers,
            "average_speed_seconds": OperationStatsBuilder._format_speed(avg_duration_ms),
            "last_activity_at": last_activity_at,
            "operation_stats": {
                **operation_stats,
                "currentStreak": streaks["current"],
                "bestStreak": streaks["best"],
            },
        }

    @staticmethod
    @log_query
    def aggregate_daily_stats(user_id: int, target_date: date | None = None) -> None:
        """Aggregate responses into daily_stats for a specific date or all dates."""
        if target_date:
            dates = [target_date]
        else:
            # Get all unique dates from responses
            response_dates = [
                row[0].date()
                for row in db.session.query(Response.answered_at)
                .filter_by(user_id=user_id)
                .distinct()
                .all()
            ]
            dates = sorted(set(response_dates))

        for stat_date in dates:
            # Get all responses for this date
            start_datetime = datetime.combine(stat_date, datetime.min.time())
            end_datetime = datetime.combine(stat_date, datetime.max.time())

            responses = (
                db.session.query(Response)
                .join(Question)
                .filter(
                    Response.user_id == user_id,
                    Response.answered_at >= start_datetime,
                    Response.answered_at <= end_datetime,
                )
                .all()
            )

            # Group by operation
            operations = {}
            for response in responses:
                op = response.question.operation
                if op not in operations:
                    operations[op] = {
                        "responses": [],
                        "correct": 0,
                        "total_duration_ms": 0,
                        "count": 0,
                    }

                operations[op]["responses"].append(response)
                operations[op]["count"] += 1
                if response.is_correct:
                    operations[op]["correct"] += 1
                if response.duration_ms:
                    operations[op]["total_duration_ms"] += response.duration_ms

            # Create or update daily_stats entries
            with transaction():
                for operation, stats in operations.items():
                    count = stats["count"]
                    correct = stats["correct"]
                    accuracy = (correct / count * 100) if count > 0 else 0.0
                    avg_duration_ms = (
                        stats["total_duration_ms"] / count if count > 0 else None
                    )
                    avg_speed_seconds = (
                        OperationStatsBuilder._format_speed(avg_duration_ms) if avg_duration_ms else None
                    )

                    existing = DailyStat.query.filter_by(
                        user_id=user_id, date=stat_date, operation=operation
                    ).first()

                    if existing:
                        existing.questions_answered = count
                        existing.correct_count = correct
                        existing.accuracy = accuracy
                        existing.avg_duration_ms = avg_duration_ms
                        existing.avg_speed_seconds = avg_speed_seconds
                    else:
                        daily_stat = DailyStat(
                            user_id=user_id,
                            date=stat_date,
                            operation=operation,
                            questions_answered=count,
                            correct_count=correct,
                            accuracy=accuracy,
                            avg_duration_ms=avg_duration_ms,
                            avg_speed_seconds=avg_speed_seconds,
                        )
                        db.session.add(daily_stat)

    @staticmethod
    @log_query
    def get_time_series_data(
        user_id: int,
        start_date: date | None = None,
        end_date: date | None = None,
        operation: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get time-series data for charts (accuracy and speed by operation)."""
        if not start_date:
            # Default to last 7 weeks
            end_date = end_date or date.today()
            start_date = end_date - timedelta(weeks=7)

        query = DailyStat.query.filter_by(user_id=user_id).filter(
            DailyStat.date >= start_date
        )

        if end_date:
            query = query.filter(DailyStat.date <= end_date)

        if operation:
            query = query.filter_by(operation=operation)

        stats = query.order_by(DailyStat.date.asc()).all()

        # Group by date
        by_date: dict[date, dict[str, Any]] = {}
        for stat in stats:
            if stat.date not in by_date:
                by_date[stat.date] = {
                    "date": stat.date.isoformat(),
                    "addition": None,
                    "subtraction": None,
                    "multiplication": None,
                    "division": None,
                }

            by_date[stat.date][stat.operation] = {
                "accuracy": stat.accuracy,
                "speed": stat.avg_speed_seconds or 0.0,
            }

        return list(by_date.values())

    @staticmethod
    @log_query
    def get_weekly_gain(user_id: int) -> int:
        """Calculate weekly gain (questions answered this week vs last week)."""
        return WeeklyGainCalculator.calculate(user_id)

    @staticmethod
    @log_query
    def compute_user_metrics_batch(user_ids: list[int]) -> dict[int, dict[str, Any]]:
        """Compute comprehensive metrics for multiple users in batch.
        
        Returns:
            Dictionary mapping user_id to metrics dict
        """
        if not user_ids:
            return {}
        
        # Batch query: total answers per user
        total_answers_query = (
            db.session.query(
                Response.user_id,
                func.count().label("total")
            )
            .filter(Response.user_id.in_(user_ids))
            .group_by(Response.user_id)
        )
        total_answers_map = {row.user_id: row.total for row in total_answers_query.all()}
        
        # Batch query: average duration per user
        avg_duration_query = (
            db.session.query(
                Response.user_id,
                func.avg(Response.duration_ms).label("avg_duration")
            )
            .filter(
                Response.user_id.in_(user_ids),
                Response.duration_ms.isnot(None)
            )
            .group_by(Response.user_id)
        )
        avg_duration_map = {row.user_id: row.avg_duration for row in avg_duration_query.all()}
        
        # Batch query: last activity per user
        last_activity_query = (
            db.session.query(
                Response.user_id,
                func.max(Response.answered_at).label("last_activity")
            )
            .filter(Response.user_id.in_(user_ids))
            .group_by(Response.user_id)
        )
        last_activity_map = {row.user_id: row.last_activity for row in last_activity_query.all()}
        
        # Batch query: operation stats per user
        operation_stats_query = (
            db.session.query(
                Response.user_id,
                Question.operation.label("operation"),
                func.count(Response.id).label("attempts"),
                func.sum(case((Response.is_correct.is_(True), 1), else_=0)).label("correct"),
                func.avg(Response.duration_ms).label("avg_duration_ms"),
            )
            .join(Question)
            .filter(Response.user_id.in_(user_ids))
            .group_by(Response.user_id, Question.operation)
            .all()
        )
        
        # Group operation stats by user_id
        operation_stats_by_user: dict[int, list[Any]] = {}
        for row in operation_stats_query:
            if row.user_id not in operation_stats_by_user:
                operation_stats_by_user[row.user_id] = []
            operation_stats_by_user[row.user_id].append(row)
        
        # Batch calculate streaks for all users
        streaks_map = StreakCalculator.calculate_streaks_batch(user_ids)
        
        # Build metrics for each user
        metrics_map = {}
        for user_id in user_ids:
            operation_rows = operation_stats_by_user.get(user_id, [])
            operation_stats = OperationStatsBuilder.build(operation_rows)
            streaks = streaks_map.get(user_id, {"current": 0, "best": 0})
            
            metrics_map[user_id] = {
                "questions_answered": total_answers_map.get(user_id, 0),
                "average_speed_seconds": OperationStatsBuilder._format_speed(avg_duration_map.get(user_id)),
                "last_activity_at": last_activity_map.get(user_id),
                "operation_stats": {
                    **operation_stats,
                    "currentStreak": streaks["current"],
                    "bestStreak": streaks["best"],
                },
            }
        
        return metrics_map


    @staticmethod
    @log_query
    def get_weekly_gain_batch(user_ids: list[int]) -> dict[int, int]:
        """Calculate weekly gain for multiple users in batch.
        
        Returns:
            Dictionary mapping user_id to weekly gain
        """
        return WeeklyGainCalculator.calculate_batch(user_ids)

