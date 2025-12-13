"""Streak calculation utilities for analytics."""

from __future__ import annotations

from datetime import date

from ...models import DailyStat, Response, db


class StreakCalculator:
    """Calculator for user streaks (current and best)."""
    
    @staticmethod
    def calculate_streaks(user_id: int) -> dict[str, int]:
        """Calculate current and best streaks for a user.
        
        Args:
            user_id: User ID to calculate streaks for
            
        Returns:
            Dictionary with 'current' and 'best' streak counts
        """
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

        best = StreakCalculator._longest_consecutive_run(unique_dates)
        current = StreakCalculator._current_run(unique_dates)

        return {"current": current, "best": best}
    
    @staticmethod
    def calculate_streaks_batch(user_ids: list[int]) -> dict[int, dict[str, int]]:
        """Calculate current and best streaks for multiple users in batch.
        
        Args:
            user_ids: List of user IDs
            
        Returns:
            Dictionary mapping user_id to streaks dict
        """
        if not user_ids:
            return {}
        
        # Batch query: daily stats dates per user
        daily_dates_query = (
            db.session.query(
                DailyStat.user_id,
                DailyStat.date
            )
            .filter(DailyStat.user_id.in_(user_ids))
            .distinct()
            .order_by(DailyStat.user_id, DailyStat.date.asc())
            .all()
        )
        
        # Group daily dates by user_id
        daily_dates_by_user: dict[int, list[date]] = {}
        for row in daily_dates_query:
            if row.user_id not in daily_dates_by_user:
                daily_dates_by_user[row.user_id] = []
            daily_dates_by_user[row.user_id].append(row.date)
        
        # Batch query: response dates for users without daily stats
        users_without_daily_stats = [uid for uid in user_ids if uid not in daily_dates_by_user]
        response_dates_query = (
            db.session.query(
                Response.user_id,
                Response.answered_at
            )
            .filter(Response.user_id.in_(users_without_daily_stats))
            .order_by(Response.user_id, Response.answered_at.asc())
            .all()
        )
        
        # Group response dates by user_id and convert to date objects
        response_dates_by_user: dict[int, list[date]] = {}
        for row in response_dates_query:
            if row.user_id not in response_dates_by_user:
                response_dates_by_user[row.user_id] = []
            if row.answered_at:
                response_dates_by_user[row.user_id].append(row.answered_at.date())
        
        # Calculate streaks for each user
        streaks_map = {}
        for user_id in user_ids:
            if user_id in daily_dates_by_user:
                unique_dates = sorted(set(daily_dates_by_user[user_id]))
            elif user_id in response_dates_by_user:
                unique_dates = sorted(set(response_dates_by_user[user_id]))
            else:
                unique_dates = []
            
            if not unique_dates:
                streaks_map[user_id] = {"current": 0, "best": 0}
            else:
                best = StreakCalculator._longest_consecutive_run(unique_dates)
                current = StreakCalculator._current_run(unique_dates)
                streaks_map[user_id] = {"current": current, "best": best}
        
        return streaks_map
    
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


