"""Concept XP lookup (XP per correct answer)."""

from __future__ import annotations

from ..config.concept_xp import CONCEPT_XP_PER_CORRECT


class ConceptXPService:
    """Simple concept XP lookup.

    Eventually this should be driven by the backend concept catalog (descriptive IDs),
    but for now we support legacy `c_concept_###` concepts.
    """

    DEFAULT_XP_PER_CORRECT = 10

    @staticmethod
    def xp_per_correct(concept_id: str | None) -> int:
        if not concept_id:
            return ConceptXPService.DEFAULT_XP_PER_CORRECT
        return int(CONCEPT_XP_PER_CORRECT.get(concept_id, ConceptXPService.DEFAULT_XP_PER_CORRECT))

