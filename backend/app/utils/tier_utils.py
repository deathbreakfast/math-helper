"""Tier system utilities for achievement tier hierarchy and mapping."""

from typing import Any

# Tier hierarchy with numeric values for comparison
TIER_HIERARCHY = {
    "bronze": 1,
    "silver": 2,
    "gold": 3,
    "platinum": 4,
    "diamond": 5,
    "master": 6,
    "grandmaster": 7,
    "legendary": 8,
    "mythic": 9,
    "divine": 10,
    "champion": 11,
}

# All tiers in order
ALL_TIERS = [
    "bronze",
    "silver",
    "gold",
    "platinum",
    "diamond",
    "master",
    "grandmaster",
    "legendary",
    "mythic",
    "divine",
    "champion",
]


def get_tier_hierarchy() -> dict[str, int]:
    """Get tier hierarchy dictionary mapping tier names to numeric values.
    
    Returns:
        Dictionary mapping tier names to their hierarchy values (higher = better tier)
    """
    return TIER_HIERARCHY.copy()


def get_all_tiers() -> list[str]:
    """Get list of all tiers in order from lowest to highest.
    
    Returns:
        List of tier names in ascending order
    """
    return ALL_TIERS.copy()


def is_tier_higher_than(tier1: str, tier2: str) -> bool:
    """Check if tier1 is higher than tier2 in the hierarchy.
    
    Args:
        tier1: First tier name
        tier2: Second tier name
        
    Returns:
        True if tier1 is higher than tier2, False otherwise
    """
    tier1_value = TIER_HIERARCHY.get(tier1.lower(), 0)
    tier2_value = TIER_HIERARCHY.get(tier2.lower(), 0)
    return tier1_value > tier2_value


def get_tier_value(tier: str) -> int:
    """Get the numeric value for a tier.
    
    Args:
        tier: Tier name
        
    Returns:
        Numeric value for the tier (0 if tier not found)
    """
    return TIER_HIERARCHY.get(tier.lower(), 0)


def get_highest_tier(tiers: list[str]) -> str | None:
    """Get the highest tier from a list of tiers.
    
    Args:
        tiers: List of tier names
    
    Returns:
        Highest tier name, or None if list is empty
    """
    if not tiers:
        return None
    
    return max(tiers, key=lambda t: TIER_HIERARCHY.get(t.lower(), 0))


def convert_tier_to_base_units(tier: str, count: int) -> int:
    """Convert a tier count to base bronze units.
    
    Conversion rates: 4 bronze = 2 silver = 1 gold, etc.
    Each tier is worth 2x the previous tier in bronze units.
    
    Args:
        tier: Tier name (bronze, silver, gold, etc.)
        count: Number of achievements at this tier
    
    Returns:
        Equivalent number of bronze units
    """
    tier_value = TIER_HIERARCHY.get(tier.lower(), 1)
    if tier_value <= 1:  # bronze or unknown
        return count
    
    # Each tier is worth 2^(tier_value - 1) bronze units
    # bronze (1) = 1, silver (2) = 2, gold (3) = 4, etc.
    # This means: 4 bronze = 2 silver = 1 gold
    bronze_units_per_achievement = 2 ** (tier_value - 1)
    return count * bronze_units_per_achievement


def convert_base_units_to_tier_count(bronze_units: int, target_tier: str) -> int:
    """Convert bronze units to a count at a specific tier.
    
    Args:
        bronze_units: Number of bronze units
        target_tier: Target tier name
    
    Returns:
        Number of achievements at target tier that bronze_units can provide
    """
    tier_value = TIER_HIERARCHY.get(target_tier.lower(), 1)
    if tier_value <= 1:  # bronze or unknown
        return bronze_units
    
    # Each tier is worth 2^(tier_value - 1) bronze units
    bronze_units_per_achievement = 2 ** (tier_value - 1)
    return bronze_units // bronze_units_per_achievement


def extract_base_code_and_tier(achievement_code: str) -> tuple[str, str | None]:
    """Extract base achievement code and tier from a full achievement code.
    
    Args:
        achievement_code: Full achievement code (e.g., "speed-demon-bronze", "math-master-gold")
    
    Returns:
        Tuple of (base_code, tier) where tier is None if no tier found
    """
    # Check for tier suffixes in reverse order (longest first)
    for tier in reversed(ALL_TIERS):
        if achievement_code.endswith(f"-{tier}"):
            base_code = achievement_code[:-len(f"-{tier}")]
            return base_code, tier
    
    return achievement_code, None


def count_achievements_with_tier_substitution(
    user_achievements: list[dict[str, Any]],
    target_code: str,
    required_quantity: int,
    metadata_filter: dict[str, Any] | None = None,
) -> tuple[int, int]:
    """Count achievements with tier substitution support.
    
    Higher tier achievements can substitute for lower tier requirements.
    Conversion: 4 bronze = 2 silver = 1 gold, etc.
    
    Args:
        user_achievements: List of user achievement dicts with 'code' and 'achievement_metadata' keys
        target_code: Target achievement code (e.g., "speed-demon-bronze")
        required_quantity: Required quantity at target tier
        metadata_filter: Optional metadata filter dict
    
    Returns:
        Tuple of (equivalent_count, actual_count) where:
        - equivalent_count: Total bronze-equivalent units
        - actual_count: Number of achievements matching exactly (for display)
    """
    base_code, target_tier = extract_base_code_and_tier(target_code)
    if target_tier is None:
        # No tier in target code, just count exact matches
        matching = [
            ach for ach in user_achievements
            if ach.get("code") == target_code
            and (metadata_filter is None or ach.get("achievement_metadata") == metadata_filter)
        ]
        return len(matching), len(matching)
    
    # Find all achievements with same base code
    matching_achievements = []
    for ach in user_achievements:
        ach_code = ach.get("code", "")
        ach_base, ach_tier = extract_base_code_and_tier(ach_code)
        
        if ach_base != base_code:
            continue
        
        # Check metadata filter
        if metadata_filter is not None:
            ach_metadata = ach.get("achievement_metadata")
            if isinstance(ach_metadata, str):
                import json
                try:
                    ach_metadata = json.loads(ach_metadata)
                except (json.JSONDecodeError, TypeError):
                    ach_metadata = {}
            if ach_metadata != metadata_filter:
                continue
        
        matching_achievements.append((ach_code, ach_tier))
    
    # Convert all matching achievements to bronze units
    total_bronze_units = 0
    exact_count = 0
    
    for ach_code, ach_tier in matching_achievements:
        if ach_tier is None:
            continue
        
        # Count exact matches (same tier or higher)
        tier_value = TIER_HIERARCHY.get(ach_tier.lower(), 0)
        target_tier_value = TIER_HIERARCHY.get(target_tier.lower(), 0)
        
        if tier_value >= target_tier_value:
            exact_count += 1
        
        # Add to total bronze units
        total_bronze_units += convert_tier_to_base_units(ach_tier, 1)
    
    # Convert total bronze units to target tier count
    target_tier_value = TIER_HIERARCHY.get(target_tier.lower(), 1)
    bronze_units_per_target = 2 ** (target_tier_value - 1) if target_tier_value > 1 else 1
    equivalent_count = total_bronze_units // bronze_units_per_target
    
    return equivalent_count, exact_count

