"""Human Calculator achievement checker.

Checks if user has achieved Lightning Fast (Bronze or Silver) for ALL descriptive concepts.
Similar to Level Grandmaster, but for speed achievements.
Checks achievements with concept_id for descriptive concepts (c_add_*, c_sub_*, c_mul_*, etc.).
"""

from __future__ import annotations

import json
from typing import Any

from ....models import Achievement, Question, User, db
from ....services.achievement_service import AchievementService
from ....config.concepts_config import CONCEPTS_CONFIG
from .base_checker import AchievementChecker


class HumanCalculatorChecker(AchievementChecker):
    """Checker for Human Calculator achievement."""
    
    def __init__(self, achievement_configs: dict[str, Any] | None = None):
        """Initialize checker with achievement configs.
        
        Args:
            achievement_configs: Dictionary of achievement configurations (optional, will use default if not provided)
        """
        self.achievement_configs = achievement_configs
    
    def check(self, user: User, tier: str = "bronze") -> list[Achievement]:
        """Check and award Human Calculator milestone achievement.
        
        Requires having Lightning Fast (Bronze or Silver) achievement for ALL descriptive concepts.
        Checks achievements with concept_id metadata for descriptive concepts (c_add_*, c_sub_*, c_mul_*, etc.).
        
        Args:
            user: The user to check
            tier: The tier to check for ("bronze" or "silver")
        
        Returns:
            List of newly created achievements
        """
        new_achievements = []
        user_achievement_codes = AchievementService.get_achievement_codes(user.id)
        achievement_configs = self.achievement_configs
        
        # Get all descriptive concepts (not c_concept_###)
        descriptive_concepts = [
            concept_id for concept_id in CONCEPTS_CONFIG.keys()
            if not concept_id.startswith("c_concept_")
        ]
        
        if not descriptive_concepts:
            return new_achievements
        
        milestone_code = f"human-calculator-{tier}" if tier != "bronze" else "human-calculator"
        
        # Skip if already earned
        if milestone_code in user_achievement_codes:
            return new_achievements
        
        # Check if user has Lightning Fast (Bronze or Silver) at ALL descriptive concepts
        all_concepts_qualified = True
        required_achievement_code = f"lightning-fast-{tier}"
        
        for target_concept_id in descriptive_concepts:
            concept_achievements = Achievement.query.filter_by(
                user_id=user.id,
                code=required_achievement_code
            ).all()
            
            concept_qualified = False
            for achievement in concept_achievements:
                if achievement.achievement_metadata:
                    try:
                        metadata = json.loads(achievement.achievement_metadata)
                        if metadata.get("concept_id") == target_concept_id:
                            concept_qualified = True
                            break
                    except (json.JSONDecodeError, KeyError):
                        pass
            
            # If bronze tier, also check if user has silver (higher tier qualifies)
            if not concept_qualified and tier == "bronze":
                silver_achievements = Achievement.query.filter_by(
                    user_id=user.id,
                    code="lightning-fast-silver"
                ).all()
                for achievement in silver_achievements:
                    if achievement.achievement_metadata:
                        try:
                            metadata = json.loads(achievement.achievement_metadata)
                            if metadata.get("concept_id") == target_concept_id:
                                concept_qualified = True
                                break
                        except (json.JSONDecodeError, KeyError):
                            pass
            
            if not concept_qualified:
                all_concepts_qualified = False
                break
        
        if all_concepts_qualified:
            config = achievement_configs.get(milestone_code) or achievement_configs.get("human-calculator")
            if config:
                achievement = AchievementService.create_achievement(
                    user_id=user.id,
                    code=milestone_code,
                    title=config["title"],
                    description=config["description"],
                    icon=config["icon"],
                    category=config["category"],
                )
                new_achievements.append(achievement)
        
        if new_achievements:
            from ....database import flush_or_commit
            flush_or_commit()
        
        return new_achievements





