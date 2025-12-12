"""Weekly gain calculation for analytics."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from sqlalchemy import func

from ...models import Question, Response, db


class WeeklyGainCalculator:
    """Calculator for weekly gain metrics."""
    
    @staticmethod
    def calculate(user_id: int) -> int:
        """Calculate weekly gain (questions answered this week vs last week).
        
        Args:
            user_id: User ID to calculate for
            
        Returns:
            Weekly gain (this week - last week)
        """
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
    
    @staticmethod
    def calculate_batch(user_ids: list[int]) -> dict[int, int]:
        """Calculate weekly gain for multiple users in batch.
        
        Args:
            user_ids: List of user IDs
            
        Returns:
            Dictionary mapping user_id to weekly gain
        """
        if not user_ids:
            return {}
        
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        last_week_start = week_start - timedelta(weeks=1)
        
        # Batch query: this week counts
        this_week_query = (
            db.session.query(
                Response.user_id,
                func.count().label("count")
            )
            .join(Question)
            .filter(
                Response.user_id.in_(user_ids),
                Response.answered_at >= datetime.combine(week_start, datetime.min.time()),
            )
            .group_by(Response.user_id)
        )
        this_week_map = {row.user_id: row.count for row in this_week_query.all()}
        
        # Batch query: last week counts
        last_week_query = (
            db.session.query(
                Response.user_id,
                func.count().label("count")
            )
            .join(Question)
            .filter(
                Response.user_id.in_(user_ids),
                Response.answered_at >= datetime.combine(last_week_start, datetime.min.time()),
                Response.answered_at < datetime.combine(week_start, datetime.min.time()),
            )
            .group_by(Response.user_id)
        )
        last_week_map = {row.user_id: row.count for row in last_week_query.all()}
        
        # Calculate weekly gain for each user
        weekly_gain_map = {}
        for user_id in user_ids:
            this_week = this_week_map.get(user_id, 0)
            last_week = last_week_map.get(user_id, 0)
            weekly_gain_map[user_id] = max(0, this_week - last_week)
        
        return weekly_gain_map
