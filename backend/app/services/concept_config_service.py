"""Concept configuration service (concept_id -> config).

Provides a single lookup path for concept-based session/question generation.
"""

from __future__ import annotations

import re
from typing import Any

from ..config.concepts_config import CONCEPTS_CONFIG


class ConceptConfigService:
    @staticmethod
    def normalize_concept_id(concept_id: str) -> str:
        """Normalize legacy concept ids to the canonical `c_concept_###` format."""
        if not concept_id:
            return concept_id

        old_match = re.match(r"^c_level_(\d+)$", concept_id)
        if old_match:
            return f"c_concept_{int(old_match.group(1)):03d}"

        new_match = re.match(r"^c_concept_(\d+)$", concept_id)
        if new_match:
            return f"c_concept_{int(new_match.group(1)):03d}"

        # Descriptive ids (c_add_1s, etc.) remain as-is.
        return concept_id

    @staticmethod
    def get_concept_config(concept_id: str) -> dict[str, Any] | None:
        concept_id = ConceptConfigService.normalize_concept_id(concept_id)
        return CONCEPTS_CONFIG.get(concept_id)

