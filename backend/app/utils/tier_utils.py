"""Tier system utilities for achievement tier hierarchy and mapping."""

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

# Mapping from old letter tier system to new metal/prestige system
OLD_TIER_TO_NEW = {
    "b": "bronze",
    "a": "silver",
    "s": "gold",
    "ss": "platinum",
    "sss": "diamond",
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


def map_old_tier_to_new(old_tier: str) -> str:
    """Map old letter tier system (B/A/S/SS/SSS) to new metal/prestige system.
    
    Args:
        old_tier: Old tier code (b, a, s, ss, sss)
        
    Returns:
        New tier name (bronze, silver, gold, platinum, diamond)
    """
    return OLD_TIER_TO_NEW.get(old_tier.lower(), old_tier.lower())


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

