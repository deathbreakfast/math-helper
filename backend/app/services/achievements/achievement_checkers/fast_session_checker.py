"""Fast session achievement checker.

Awards achievements for completing sessions with fast average time per question.
"""

from __future__ import annotations

from typing import Any

from ....models import Achievement, PracticeSession, User, db
from .base_checker import AchievementChecker


class FastSessionChecker(AchievementChecker):
    """Checker for fast session achievements."""
    
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
        """Check and award fast session achievements.
        
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
        
        # Get session
        session = PracticeSession.query.get(session_id)
        if not session or not session.completed_at:
            return new_achievements
        
        # Get fast_session achievements from config
        fast_session_achievements = [
            (code, config) for code, config in self.achievement_configs.items()
            if config.get("requirements", {}).get("type") == "fast_session"
        ]
        
        if not fast_session_achievements:
            return new_achievements
        
        # Check if session meets minimum questions requirement
        if session.total_questions < 10:
            return new_achievements
        
        # Calculate average time per question
        total_duration_ms = session.total_duration_ms or 0
        avg_time = (total_duration_ms / 1000.0 / session.total_questions) if session.total_questions > 0 else None
        
        if not avg_time:
            return new_achievements
        
        # Find all qualifying tiers
        qualifying_tiers = []
        for achievement_code, config in fast_session_achievements:
            max_avg_time = config.get("requirements", {}).get("max_avg_time", 5.0)
            min_questions = config.get("requirements", {}).get("min_questions", 10)
            
            if session.total_questions >= min_questions and avg_time < max_avg_time:
                qualifying_tiers.append((achievement_code, config, max_avg_time))
        
        # Award only the highest tier (lowest max_avg_time = best performance)
        if qualifying_tiers:
            # Sort by max_avg_time ascending (lowest = best)
            qualifying_tiers.sort(key=lambda x: x[2])
            highest_tier_code, highest_tier_config, _ = qualifying_tiers[0]
            
            # Check if already awarded (fast_session can be awarded per session)
            # For now, we allow multiple awards per session type
            
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
        """Create an achievement (helper method).
        
        This is a simplified version - in the full refactor, this would use
        a shared achievement creation service.
        """
        from datetime import datetime
        
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


