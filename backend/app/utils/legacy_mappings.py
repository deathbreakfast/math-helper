"""Legacy mappings for backward compatibility with old concept ID and level formats."""

from __future__ import annotations

import re


def extract_legacy_level_from_concept_id(concept_id: str | None) -> int | None:
    """Extract legacy level number from concept ID.
    
    Supports:
    - Old format: c_level_1 -> 1
    - New format: c_concept_001 -> 1
    - Descriptive format: c_add_1s -> None (no legacy level mapping)
    
    Args:
        concept_id: The concept ID to parse
        
    Returns:
        The legacy level number if found, None otherwise
    """
    if not concept_id:
        return None
    
    # Old format: c_level_1, c_level_2, etc.
    old_format_match = re.match(r'^c_level_(\d+)$', concept_id)
    if old_format_match:
        return int(old_format_match.group(1))
    
    # New format: c_concept_001, c_concept_002, etc.
    new_format_match = re.match(r'^c_concept_(\d+)$', concept_id)
    if new_format_match:
        return int(new_format_match.group(1))
    
    # Descriptive format (c_add_1s, c_sub_2s, etc.) - no legacy level mapping
    return None


def concept_id_from_legacy_level(level: int) -> str:
    """Build a new-format concept ID from a legacy level number.
    
    Args:
        level: The legacy level number
        
    Returns:
        A concept ID in the format c_concept_XXX (e.g., c_concept_001)
    """
    return f"c_concept_{level:03d}"

