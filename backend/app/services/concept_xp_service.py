"""Concept XP lookup (XP per correct answer)."""

from __future__ import annotations

from ..config.concept_xp import CONCEPT_XP_PER_CORRECT


class ConceptXPService:
    """Simple concept XP lookup.

    Backed by `CONCEPT_XP_PER_CORRECT` which includes both legacy `c_concept_###` and
    descriptive concept IDs (e.g. `c_add_1s`).
    """

    DEFAULT_XP_PER_CORRECT = 10

    @staticmethod
    def xp_per_correct(concept_id: str | None) -> int:
        if not concept_id:
            return ConceptXPService.DEFAULT_XP_PER_CORRECT
        return int(CONCEPT_XP_PER_CORRECT.get(concept_id, ConceptXPService.DEFAULT_XP_PER_CORRECT))

