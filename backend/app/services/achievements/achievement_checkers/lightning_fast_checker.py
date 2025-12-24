"""Lightning fast achievement checker.

Awards concept-specific speed achievements based on average speed for a specific concept.
These are awarded per concept with metadata {"concept_id": "c_add_1s"}.
"""

from __future__ import annotations

import json
from typing import Any

from ....config.concepts_config import get_concept_speed_multiplier
from ....models import Achievement, PracticeSession, Response, User, db
from ....utils.tier_utils import get_tier_value
from .base_checker import AchievementChecker


class LightningFastChecker(AchievementChecker):
    """Checker for lightning-fast achievements (concept-specific speed)."""
    
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
        """Check and award lightning-fast achievements.
        
        Args:
            user: The user to check achievements for
            metrics: Optional pre-computed user metrics (not used)
            session_id: Required session ID to check
        
        Returns:
            List of newly created Achievement objects
        """
        from ....services.achievement_service import AchievementService
        
        new_achievements = []
        
        if not session_id:
            return new_achievements
        
        # Get session
        session = db.session.get(PracticeSession, session_id)
        if not session or not session.completed_at:
            return new_achievements
        
        # Determine concept_id: use session.concept_id if available, otherwise derive from level
        concept_id = session.concept_id
        if not concept_id and session.level:
            # For legacy level-based sessions, derive concept_id from level
            concept_id = f"c_concept_{session.level:03d}"
        
        if not concept_id:
            return new_achievements
        
        # Get lightning-fast achievements from config
        lightning_fast_achievements = [
            (code, config) for code, config in self.achievement_configs.items()
            if code.startswith("lightning-fast-")
        ]
        
        if not lightning_fast_achievements:
            return new_achievements
        
        # Get user's existing achievements
        user_achievement_codes = AchievementService.get_achievement_codes(user.id)
        
        # Calculate average speed for this concept from user's responses
        # Filter by concept_id
        concept_responses = (
            Response.query.filter_by(user_id=user.id, is_correct=True)
            .join(PracticeSession, Response.session_id == PracticeSession.id)
            .filter(PracticeSession.concept_id == concept_id)
            .all()
        )
        
        if not concept_responses:
            return new_achievements
        
        # Calculate average time per question for this concept
        total_duration = sum(r.duration_ms or 0 for r in concept_responses)
        total_questions = len(concept_responses)
        avg_speed_seconds = (total_duration / 1000.0 / total_questions) if total_questions > 0 else None
        
        if not avg_speed_seconds:
            return new_achievements
        
        # Get speed multiplier for this concept
        speed_multiplier = get_concept_speed_multiplier(concept_id)
        
        # Find all qualifying tiers for this concept
        # Note: We don't check for existing achievements here - create_achievement() handles constraints
        qualifying_tiers = []
        # Exclude champion from initial qualifying_tiers - it requires server record check
        champion_code = "lightning-fast-champion"
        champion_config = None
        
        for achievement_code, config in lightning_fast_achievements:
            # Skip champion tier - we'll check it separately after determining highest tier
            if achievement_code == champion_code:
                champion_config = config
                continue
                
            requirements = config.get("requirements", {})
            max_speed = requirements.get("max_speed_seconds", 999)
            # Apply speed multiplier to threshold
            adjusted_max_speed = max_speed * speed_multiplier
            min_questions = requirements.get("min_questions", 50)
            
            if avg_speed_seconds <= adjusted_max_speed and total_questions >= min_questions:
                tier = config.get("tier", "bronze")
                qualifying_tiers.append((tier, achievement_code, config))
        
        if qualifying_tiers:
            # Sort by tier value (highest first) and award the highest tier
            qualifying_tiers.sort(key=lambda x: get_tier_value(x[0]), reverse=True)
            highest_tier, achievement_code, config = qualifying_tiers[0]
            
            # Check for Champion tier if this is Divine
            # Champion tier requires both meeting the speed threshold AND setting/breaking a server record
            if highest_tier == "divine" and champion_config:
                champion_req = champion_config.get("requirements", {})
                champion_max_speed = champion_req.get("max_speed_seconds", 999)
                # Apply speed multiplier to champion threshold
                adjusted_champion_max_speed = champion_max_speed * speed_multiplier
                if avg_speed_seconds <= adjusted_champion_max_speed:
                    # Champion tier qualifies by speed, now check if server record is set/broken
                    if session_id:
                        from ....services.achievements.achievement_validators.champion_validator import ChampionValidator
                        champion_awarded = ChampionValidator.check_eligibility(
                            champion_code,
                            session,
                            "champion"
                        )
                        if champion_awarded:
                            # Server record was set/broken, award champion tier
                            achievement_code = champion_code
                            config = champion_config
                        # else: award divine (record not set/broken)

            # Create metadata used by unlock requirements (concept-specific).
            metadata = {"concept_id": concept_id}

            achievement = AchievementService.create_achievement(
                user_id=user.id,
                code=achievement_code,
                title=config["title"],
                description=config["description"],
                icon=config["icon"],
                category=config["category"],
                session_id=session_id,
                metadata=metadata,
            )
            new_achievements.append(achievement)
        
        if new_achievements:
            from ....database import flush_or_commit
            flush_or_commit()
        
        return new_achievements




