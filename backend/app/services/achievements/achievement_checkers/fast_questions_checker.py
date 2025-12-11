"""Fast questions achievement checker.

Awards achievements for answering consecutive questions quickly.
"""

from __future__ import annotations

from typing import Any

from ....models import Achievement, Response, User, db
from .base_checker import AchievementChecker


class FastQuestionsChecker(AchievementChecker):
    """Checker for fast questions achievements."""
    
    def __init__(self, achievement_configs: dict[str, Any]):
        """Initialize checker with achievement configs.
        
        Args:
            achievement_configs: Dictionary of achievement configurations
        """
        self.achievement_configs = achievement_configs
    
    def check(
        self,
        user: User,
        metrics: dict[str, Any] | None = None,
        session_id: int | None = None
    ) -> list[Achievement]:
        """Check and award fast questions achievements.
        
        Args:
            user: The user to check achievements for
            metrics: Optional pre-computed user metrics (not used)
            session_id: Required session ID to check
        
        Returns:
            List of newly created Achievement objects
        """
        new_achievements = []
        
        if not session_id:
            return new_achievements
        
        # Get fast_questions achievements from config
        fast_questions_achievements = [
            (code, config) for code, config in self.achievement_configs.items()
            if config.get("requirements", {}).get("type") == "fast_questions"
        ]
        
        if not fast_questions_achievements:
            return new_achievements
        
        # Build query - filter by session_id
        recent_responses_query = Response.query.filter_by(user_id=user.id, session_id=session_id)
        
        # Find all qualifying tiers
        qualifying_tiers = []
        for achievement_code, config in fast_questions_achievements:
            max_avg_time = config.get("requirements", {}).get("max_avg_time", 4.0)
            consecutive_count = config.get("requirements", {}).get("consecutive_count", 10)
            
            # Get most recent responses (limit to highest consecutive_count needed)
            max_consecutive = max(
                cfg.get("requirements", {}).get("consecutive_count", 10)
                for _, cfg in fast_questions_achievements
            )
            recent_responses = (
                recent_responses_query
                .order_by(Response.answered_at.desc())
                .limit(max_consecutive)
                .all()
            )
            
            # Require EXACT count match
            if len(recent_responses) >= consecutive_count:
                # Take exactly the required number
                responses_for_tier = recent_responses[:consecutive_count]
                total_time = sum(r.duration_ms or 0 for r in responses_for_tier)
                avg_time = (total_time / 1000.0 / len(responses_for_tier)) if responses_for_tier else None
                
                if avg_time and avg_time < max_avg_time:
                    qualifying_tiers.append((achievement_code, config, consecutive_count))
        
        # Award only the highest tier (highest consecutive_count = best performance)
        if qualifying_tiers:
            # Sort by consecutive_count descending (highest = best)
            qualifying_tiers.sort(key=lambda x: x[2], reverse=True)
            highest_tier_code, highest_tier_config, highest_count = qualifying_tiers[0]
            
            # Get responses for the highest tier
            recent_responses = (
                recent_responses_query
                .order_by(Response.answered_at.desc())
                .limit(highest_count)
                .all()
            )
            if len(recent_responses) == highest_count:
                achievement = self._create_achievement(
                    user_id=user.id,
                    code=highest_tier_code,
                    title=highest_tier_config["title"],
                    description=highest_tier_config["description"],
                    icon=highest_tier_config["icon"],
                    category=highest_tier_config["category"],
                    session_id=session_id,
                )
                new_achievements.append(achievement)
        
        return new_achievements
    
    def _create_achievement(
        self,
        user_id: int,
        code: str,
        title: str,
        description: str,
        icon: str,
        category: str,
        session_id: int | None = None
    ) -> Achievement:
        """Create an achievement (helper method)."""
        from datetime import datetime
        from ....models import Achievement
        
        # Check if achievement already exists
        existing = Achievement.query.filter_by(
            user_id=user_id,
            code=code,
            session_id=session_id
        ).first()
        
        if existing:
            return existing
        
        achievement = Achievement(
            user_id=user_id,
            code=code,
            title=title,
            description=description,
            icon=icon,
            category=category,
            earned_at=datetime.utcnow(),
            session_id=session_id,
        )
        db.session.add(achievement)
        db.session.flush()
        
        return achievement


