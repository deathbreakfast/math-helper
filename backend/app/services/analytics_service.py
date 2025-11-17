"""Analytics service for dashboard metrics, time-series aggregation, and streak calculations."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from sqlalchemy import case, func

from ..database import log_query, transaction
from ..models import DailyStat, Question, Response, db


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

        operation_stats = AnalyticsService._build_operation_stats(operation_rows)
        streaks = AnalyticsService._calculate_streaks(user_id)

        return {
            "questions_answered": total_answers,
            "average_speed_seconds": AnalyticsService._format_speed(avg_duration_ms),
            "last_activity_at": last_activity_at,
            "operation_stats": {
                **operation_stats,
                "currentStreak": streaks["current"],
                "bestStreak": streaks["best"],
            },
        }

    @staticmethod
    def _build_operation_stats(rows: list[Any]) -> dict[str, Any]:
        """Build operation-specific statistics."""
        stats = {
            "additionAccuracy": 0,
            "subtractionAccuracy": 0,
            "multiplicationAccuracy": 0,
            "divisionAccuracy": 0,
            "additionSpeed": 0.0,
            "subtractionSpeed": 0.0,
            "multiplicationSpeed": 0.0,
            "divisionSpeed": 0.0,
        }

        key_map = {
            "addition": ("additionAccuracy", "additionSpeed"),
            "subtraction": ("subtractionAccuracy", "subtractionSpeed"),
            "multiplication": ("multiplicationAccuracy", "multiplicationSpeed"),
            "division": ("divisionAccuracy", "divisionSpeed"),
        }

        for row in rows:
            operation = (row.operation or "").lower()
            mapping = key_map.get(operation)
            if not mapping or row.attempts == 0:
                continue

            accuracy_key, speed_key = mapping
            correct = row.correct or 0
            stats[accuracy_key] = round((correct / row.attempts) * 100)
            stats[speed_key] = AnalyticsService._format_speed(row.avg_duration_ms)

        return stats

    @staticmethod
    def _format_speed(duration_ms: float | None) -> float:
        """Format duration in milliseconds to seconds."""
        if duration_ms is None:
            return 0.0
        return round(duration_ms / 1000, 1)

    @staticmethod
    @log_query
    def _calculate_streaks(user_id: int) -> dict[str, int]:
        """Calculate current and best streaks for a user."""
        # Use daily_stats if available, otherwise fall back to responses
        daily_dates = [
            row[0]
            for row in db.session.query(DailyStat.date)
            .filter_by(user_id=user_id)
            .distinct()
            .order_by(DailyStat.date.asc())
            .all()
        ]

        if not daily_dates:
            # Fall back to response dates
            response_dates = [
                row[0].date()
                for row in db.session.query(Response.answered_at)
                .filter_by(user_id=user_id)
                .order_by(Response.answered_at.asc())
                .all()
            ]
            unique_dates = sorted(set(response_dates))
        else:
            unique_dates = sorted(set(daily_dates))

        if not unique_dates:
            return {"current": 0, "best": 0}

        best = AnalyticsService._longest_consecutive_run(unique_dates)
        current = AnalyticsService._current_run(unique_dates)

        return {"current": current, "best": best}

    @staticmethod
    def _longest_consecutive_run(sorted_dates: list[date]) -> int:
        """Find the longest consecutive run of dates."""
        if not sorted_dates:
            return 0

        best = 1
        streak = 1
        for prev, curr in zip(sorted_dates, sorted_dates[1:]):
            if (curr - prev).days == 1:
                streak += 1
                best = max(best, streak)
            else:
                streak = 1
        return best

    @staticmethod
    def _current_run(sorted_dates: list[date]) -> int:
        """Find the current consecutive run ending today or yesterday."""
        if not sorted_dates:
            return 0

        streak = 1
        last = sorted_dates[-1]
        today = date.today()

        # If last activity was more than 1 day ago, streak is broken
        if (today - last).days > 1:
            return 0

        # Count backwards from the last date
        for curr in reversed(sorted_dates[:-1]):
            if (last - curr).days == 1:
                streak += 1
                last = curr
            else:
                break

        return streak

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
                        AnalyticsService._format_speed(avg_duration_ms) if avg_duration_ms else None
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
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        last_week_start = week_start - timedelta(weeks=1)
        last_week_end = week_start - timedelta(days=1)

        # This week
        this_week = (
            db.session.query(func.count())
            .select_from(Response)
            .join(Question)
            .filter(
                Response.user_id == user_id,
                Response.answered_at >= datetime.combine(week_start, datetime.min.time()),
            )
            .scalar()
            or 0
        )

        # Last week
        last_week = (
            db.session.query(func.count())
            .select_from(Response)
            .join(Question)
            .filter(
                Response.user_id == user_id,
                Response.answered_at >= datetime.combine(last_week_start, datetime.min.time()),
                Response.answered_at < datetime.combine(week_start, datetime.min.time()),
            )
            .scalar()
            or 0
        )

        return max(0, this_week - last_week)

