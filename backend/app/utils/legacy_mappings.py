"""Legacy mappings for backward compatibility with concept ID formats.

Note: The legacy level system has been removed. These functions are kept for minimal
backward compatibility to extract level numbers from c_concept_### IDs where needed.
"""

from __future__ import annotations

import re


def extract_legacy_level_from_concept_id(concept_id: str | None) -> int | None:
    """Extract level number from c_concept_### format concept ID.
    
    Supports:
    - Format: c_concept_001 -> 1
    - Descriptive format: c_add_1s -> None (no level mapping)
    
    Args:
        concept_id: The concept ID to parse
        
    Returns:
        The level number if found, None otherwise
    """
    if not concept_id:
        return None
    
    # Format: c_concept_001, c_concept_002, etc.
    match = re.match(r'^c_concept_(\d+)$', concept_id)
    if match:
        return int(match.group(1))
    
    # Descriptive format (c_add_1s, c_sub_2s, etc.) - no level mapping
    return None


def concept_id_from_legacy_level(level: int) -> str:
    """Build a concept ID from a level number.
    
    Args:
        level: The level number
        
    Returns:
        A concept ID in the format c_concept_XXX (e.g., c_concept_001)
    """
    return f"c_concept_{level:03d}"

