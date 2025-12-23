"""Service for selecting concepts for practice sessions."""

from __future__ import annotations

import random

from ..utils.legacy_mappings import extract_legacy_level_from_concept_id
from .concept_unlock_service import ConceptUnlockService


class ConceptSelectionService:
    """Service for concept selection logic."""

    @staticmethod
    def select_concept_for_practice(
        user_id: int,
        concept_id: str | None = None,
    ) -> tuple[str, int | None]:
        """Select a concept for practice, either the provided one or a random unlocked one.
        
        Args:
            user_id: The user ID
            concept_id: Optional concept identifier (if None, will select randomly from unlocked)
        
        Returns:
            Tuple of (selected_concept_id, extracted_legacy_level or None)
        
        Raises:
            ValueError: If no concept_id provided and no unlocked concepts available
        """
        if concept_id is None:
            # Get all unlocked concepts for the user
            unlocked_concepts = ConceptUnlockService.get_unlocked_concepts(user_id)
            
            if not unlocked_concepts:
                raise ValueError("No unlocked concepts available. Please unlock at least one concept to start practice.")
            
            # Randomly select from unlocked concepts
            concept_id = random.choice(unlocked_concepts)
        
        # Extract legacy level if available (for backward compatibility)
        extracted_level = extract_legacy_level_from_concept_id(concept_id)
        
        return concept_id, extracted_level

