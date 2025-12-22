"""Service for checking concept unlock status."""

from __future__ import annotations

from typing import Any

from ..config.concept_unlock_requirements import CONCEPT_UNLOCK_REQUIREMENTS
from ..config.concepts_config import CONCEPTS_CONFIG
from ..services.achievement_service import AchievementService
from ..services.level_config_service import LevelConfigService


class ConceptUnlockService:
    """Service for checking concept unlock status."""
    
    @staticmethod
    def is_concept_unlocked(user_id: int, concept_id: str) -> bool:
        """Check if a concept is unlocked for a user.
        
        Args:
            user_id: The user ID to check
            concept_id: The concept ID to check
            
        Returns:
            True if the concept is unlocked, False otherwise
        """
        # Get unlock requirements for this concept
        requirements = ConceptUnlockService.get_concept_requirements(concept_id)
        
        # If no requirements, concept is unlocked by default
        if not requirements:
            return True
        
        # Check if all requirements are met
        for req in requirements:
            achievement_code = req.get("achievement_code", "")
            quantity = req.get("quantity", 1)
            metadata_filter = req.get("metadata_filter")
            
            count = AchievementService.count_achievements_by_code_with_filters(
                user_id=user_id,
                achievement_code=achievement_code,
                metadata_filter=metadata_filter,
            )
            
            if count < quantity:
                return False
        
        return True
    
    @staticmethod
    def get_concept_requirements(concept_id: str) -> list[dict[str, Any]]:
        """Get unlock requirements for a concept.
        
        Args:
            concept_id: The concept ID
            
        Returns:
            List of requirement dictionaries
        """
        # Prefer explicit concept unlock requirements
        if concept_id in CONCEPT_UNLOCK_REQUIREMENTS:
            return list(CONCEPT_UNLOCK_REQUIREMENTS.get(concept_id, []))
        
        # Fallback: legacy concepts use level progression configs
        if concept_id.startswith("c_concept_"):
            try:
                level_num = int(concept_id.split("_")[-1])
            except ValueError:
                level_num = None
            
            if level_num is not None:
                return list(LevelConfigService.get_level_progression_config(level_num) or [])
        
        return []
    
    @staticmethod
    def get_unlocked_concepts(user_id: int) -> list[str]:
        """Get all unlocked concept IDs for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            List of unlocked concept IDs
        """
        unlocked = []
        for concept_id in CONCEPTS_CONFIG.keys():
            if ConceptUnlockService.is_concept_unlocked(user_id, concept_id):
                unlocked.append(concept_id)
        return unlocked


