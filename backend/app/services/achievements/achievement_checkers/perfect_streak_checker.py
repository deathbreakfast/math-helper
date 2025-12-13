"""Perfect streak achievement checker.

Awards achievements for consecutive perfect sessions (100% accuracy).
Achievements are awarded once per uninterrupted perfect run and can be
re-awarded only after the run is broken by an imperfect session.
"""

from __future__ import annotations

import json
from typing import Any

from ....models import Achievement, PracticeSession, User, db
from .base_checker import AchievementChecker


class PerfectStreakChecker(AchievementChecker):
    """Checker for perfect streak achievements.
    
    Awards achievements once per uninterrupted perfect run. A run is defined
    as consecutive perfect sessions (100% accuracy) that ends when an imperfect
    session is encountered. Achievements can be re-awarded after a run is broken.
    """
    
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
        """Check and award perfect streak achievements.
        
        Awards achievements once per uninterrupted perfect run. A run is defined
        as consecutive perfect sessions (100% accuracy) that ends when an imperfect
        session is encountered. Achievements can be re-awarded after a run is broken.
        
        Args:
            user: The user to check achievements for
            metrics: Optional pre-computed user metrics (not used)
            session_id: Optional session ID to link achievements
        
        Returns:
            List of newly created Achievement objects (not existing ones)
        """
        new_achievements = []
        
        # Get perfect_streak achievements from config
        perfect_streak_achievements = [
            (code, config) for code, config in self.achievement_configs.items()
            if code.startswith("perfect-streak-")
        ]
        
        if not perfect_streak_achievements:
            return new_achievements
        
        # Get all completed sessions ordered by completion time (most recent first)
        all_sessions = (
            PracticeSession.query.filter_by(user_id=user.id)
            .filter(PracticeSession.completed_at.isnot(None))
            .order_by(PracticeSession.completed_at.desc())
            .all()
        )
        
        # Count consecutive perfect sessions (100% accuracy) and identify run
        # Note: Sessions are ordered by completed_at DESC (most recent first)
        # So we count from the most recent backwards
        consecutive_perfect = 0
        perfect_sessions_in_run = []
        for session in all_sessions:
            # Check if session has exactly 100.0 accuracy (stored as percentage)
            if session.accuracy == 100.0:
                consecutive_perfect += 1
                perfect_sessions_in_run.append(session)
            else:
                break  # Break on first non-perfect session
        
        if consecutive_perfect == 0:
            return new_achievements
        
        # Compute run key: use the first (oldest) session ID in the current perfect run
        # This provides a stable identifier for the uninterrupted run
        run_key = perfect_sessions_in_run[-1].id if perfect_sessions_in_run else None
        
        # Find all qualifying tiers
        qualifying_tiers = []
        for achievement_code, config in perfect_streak_achievements:
            requirements = config.get("requirements", {})
            min_sessions = requirements.get("min_sessions", 0)
            if consecutive_perfect >= min_sessions:
                tier = config.get("tier", "bronze")
                qualifying_tiers.append((tier, achievement_code, config))
        
        if qualifying_tiers:
            # Sort by tier value (highest first)
            from ....utils.tier_utils import get_tier_value
            qualifying_tiers.sort(key=lambda x: get_tier_value(x[0]), reverse=True)
            highest_tier, achievement_code, config = qualifying_tiers[0]
            
            # Check for Champion tier if this is Divine
            # Note: Champion eligibility check is handled at orchestrator level to avoid circular imports
            if highest_tier == "divine":
                champion_code = "perfect-streak-champion"
                champion_config = self.achievement_configs.get(champion_code)
                if champion_config:
                    champion_req = champion_config.get("requirements", {})
                    if consecutive_perfect >= champion_req.get("min_sessions", 0):
                        # Champion eligibility will be checked by orchestrator
                        # For now, award divine tier
                        pass
            
            # Check if this achievement already exists for this run key
            # We use metadata to store the run_key, making each run unique
            run_metadata = {"run_key": run_key} if run_key else None
            existing_for_run = self._check_existing_for_run(
                user_id=user.id,
                code=achievement_code,
                run_key=run_key
            )
            
            if not existing_for_run:
                # Only create if it doesn't exist for this run
                # The constraint check in create_achievement will now prioritize
                # metadata (run_key) for perfect-streak achievements
                achievement = self._create_achievement(
                    user_id=user.id,
                    code=achievement_code,
                    title=config["title"],
                    description=config["description"],
                    icon=config["icon"],
                    category=config["category"],
                    session_id=session_id,
                    metadata=run_metadata,
                )
                # Verify this is a newly created achievement (not an existing one)
                # by checking if it has the run_key we just passed
                if achievement.achievement_metadata:
                    try:
                        achievement_metadata = json.loads(achievement.achievement_metadata)
                        if achievement_metadata.get("run_key") == run_key:
                            # This is a new achievement for this run
                            new_achievements.append(achievement)
                    except (json.JSONDecodeError, TypeError):
                        # If metadata parsing fails, skip (shouldn't happen)
                        pass
                # If no metadata, it's likely an existing achievement that was returned
                # (shouldn't happen with our pre-check, but be safe)
        
        return new_achievements
    
    def _check_existing_for_run(
        self,
        user_id: int,
        code: str,
        run_key: int | None
    ) -> Achievement | None:
        """Check if an achievement already exists for a specific run key.
        
        Args:
            user_id: User ID
            code: Achievement code
            run_key: Run key (session ID of first session in the run)
        
        Returns:
            Existing Achievement if found, None otherwise
        """
        if run_key is None:
            return None
        
        # Check for existing achievement with this code and run_key in metadata
        run_metadata_json = json.dumps({"run_key": run_key}, sort_keys=True)
        existing = Achievement.query.filter_by(
            user_id=user_id,
            code=code,
            achievement_metadata=run_metadata_json
        ).first()
        
        return existing
    
    def _create_achievement(
        self,
        user_id: int,
        code: str,
        title: str,
        description: str,
        icon: str,
        category: str,
        session_id: int | None = None,
        metadata: dict[str, Any] | None = None
    ) -> Achievement:
        """Create an achievement using AchievementService for constraint handling.
        
        Args:
            user_id: User ID
            code: Achievement code
            title: Achievement title
            description: Achievement description
            icon: Achievement icon
            category: Achievement category
            session_id: Optional session ID to link achievement
            metadata: Optional metadata dict (e.g., run_key for perfect streak)
        
        Returns:
            Created or existing Achievement object
        """
        from ....services.achievement_service import AchievementService
        
        # Use AchievementService.create_achievement to maintain consistency and handle constraints
        return AchievementService.create_achievement(
            user_id=user_id,
            code=code,
            title=title,
            description=description,
            icon=icon,
            category=category,
            session_id=session_id,
            metadata=metadata,
        )

