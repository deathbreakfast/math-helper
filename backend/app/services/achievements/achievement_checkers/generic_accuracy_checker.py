"""Generic accuracy achievement checker.

Checks for operation-level specific accuracy achievements (e.g., "addition-basics-bronze").
"""

from __future__ import annotations

from typing import Any

from ....models import Achievement, PracticeSession, Question, Response
from ....config.achievements import ACCURACY_ACHIEVEMENTS
from ....utils.tier_utils import ALL_TIERS, get_tier_value
from ....services.achievement_service import AchievementService
from .... import db
from .base_checker import AchievementChecker


class GenericAccuracyChecker(AchievementChecker):
    """Checker for generic accuracy achievements (operation-level specific)."""
    
    def __init__(self, achievement_configs: dict[str, Any] | None = None):
        """Initialize checker with achievement configs.
        
        Args:
            achievement_configs: Dictionary of achievement configurations (optional, will use default if not provided)
        """
        self.achievement_configs = achievement_configs
        self.achievement_configs = achievement_configs
    
    def check(self, session: PracticeSession) -> list[Achievement]:
        """Check session for generic accuracy achievements and award highest tier achieved.
        
        Args:
            session: Completed practice session to check
            
        Returns:
            List of newly created achievements
        """
        if not session.completed_at:
            return []
        
        new_achievements = []
        user_achievement_codes = AchievementService.get_achievement_codes(session.user_id)
        
        # Get session metrics
        total_questions = session.total_questions
        accuracy = session.accuracy / 100.0 if session.accuracy else 0.0  # Convert to 0-1 range
        total_duration_ms = session.total_duration_ms or 0
        avg_time_per_question = (total_duration_ms / 1000.0 / total_questions) if total_questions > 0 and total_duration_ms else None
        
        # Get the operation and level for this session
        if not session.level:
            return []
        
        # Get operation from session's questions
        first_question = (
            Question.query.join(Response)
            .filter(Response.session_id == session.id)
            .first()
        )
        
        if not first_question:
            return []
        
        operation = first_question.operation
        level = session.level
        
        # Check all tiers for this operation-level combination
        tiers_achieved = []
        
        # Use achievement_configs if provided, otherwise fall back to ACCURACY_ACHIEVEMENTS
        configs_to_check = self.achievement_configs if self.achievement_configs else ACCURACY_ACHIEVEMENTS
        
        for tier in reversed(ALL_TIERS):  # Check from highest to lowest
            achievement_code = f"{operation}-basics-{tier}"
            
            if achievement_code not in configs_to_check:
                continue
            
            # Skip if already earned
            if achievement_code in user_achievement_codes:
                continue
            
            config = configs_to_check[achievement_code]
            requirements = config.get("requirements", {})
            
            # Check if this is for the correct level
            if requirements.get("level") != level:
                continue
            
            # Check if operation matches
            if requirements.get("operation") != operation:
                continue
            
            # Check tier requirements
            min_accuracy_req = requirements.get("min_accuracy", 0.0)
            min_questions_req = requirements.get("min_questions", 0)
            max_questions_req = requirements.get("max_questions")
            max_speed_req = requirements.get("max_speed")
            
            meets_requirements = True
            
            # Check accuracy
            if accuracy < min_accuracy_req:
                meets_requirements = False
            
            # Check question count
            if total_questions < min_questions_req:
                meets_requirements = False
            
            if max_questions_req and total_questions > max_questions_req:
                meets_requirements = False
            
            # Check speed
            if max_speed_req:
                if avg_time_per_question is None:
                    meets_requirements = False
                elif avg_time_per_question >= max_speed_req:
                    meets_requirements = False
            
            if meets_requirements:
                tiers_achieved.append((tier, achievement_code, config))
        
        # Award only the highest tier achieved
        if tiers_achieved:
            # Sort by tier value (highest first)
            tiers_achieved.sort(key=lambda x: get_tier_value(x[0]), reverse=True)
            highest_tier, achievement_code, config = tiers_achieved[0]
            
            # Check for Champion tier eligibility if this is Divine tier
            if highest_tier == "divine":
                # Check if Champion is also eligible
                champion_code = f"{operation}-basics-champion"
                if champion_code in ACCURACY_ACHIEVEMENTS:
                    champion_config = ACCURACY_ACHIEVEMENTS[champion_code]
                    champion_req = champion_config.get("requirements", {})
                    
                    # Check if Champion requirements are also met
                    champion_eligible = True
                    if accuracy < champion_req.get("min_accuracy", 0.0):
                        champion_eligible = False
                    if total_questions < champion_req.get("min_questions", 0):
                        champion_eligible = False
                    if champion_req.get("max_questions") and total_questions > champion_req.get("max_questions"):
                        champion_eligible = False
                    if champion_req.get("max_speed"):
                        if avg_time_per_question is None or avg_time_per_question >= champion_req.get("max_speed"):
                            champion_eligible = False
                    
                    # If Champion requirements met, check server record
                    if champion_eligible:
                        if AchievementService.checkChampionEligibility(champion_code, session, "champion"):
                            # Award Champion instead
                            achievement_code = champion_code
                            config = champion_config
            
            # Award the achievement
            achievement = AchievementService.create_achievement(
                user_id=session.user_id,
                code=achievement_code,
                title=config["title"],
                description=config["description"],
                icon=config["icon"],
                category=config["category"],
                session_id=session.id,
            )
            new_achievements.append(achievement)
        
        if new_achievements:
            from ....database import flush_or_commit
            flush_or_commit()
        
        return new_achievements

