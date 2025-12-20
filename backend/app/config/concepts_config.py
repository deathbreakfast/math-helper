"""Concept configuration keyed by concept_id.

This is the backend source of truth for question generation per concept.

For now, legacy concepts `c_concept_###` map 1:1 to the existing `LEVELS_CONFIG`
entries (levels 1-45). This keeps behavior stable while enabling the system to
support descriptive concept IDs (e.g. `c_add_1s`) without depending on levels.
"""

from __future__ import annotations

from typing import Any

from .levels_config import LEVELS_CONFIG


CONCEPTS_CONFIG: dict[str, dict[str, Any]] = {
    f"c_concept_{level:03d}": {**config, "legacy_level": level}
    for level, config in LEVELS_CONFIG.items()
}

# Special cases / overrides not representable with the legacy level system.
# Division by 0 (Special Case): allow generating 0 ÷ 0 with answer "undefined".
CONCEPTS_CONFIG["c_concept_037"] = {
    "operation": "division",
    "operand1_range": {"min": 0, "max": 0},
    "operand2_range": {"min": 0, "max": 0},
    "constraints": {"fixed_operand2": 0, "no_remainder": True, "allow_division_by_zero": True},
    "layout_type": "longDivision",
    "answer_format": "integer",
    "legacy_level": 37,
}

