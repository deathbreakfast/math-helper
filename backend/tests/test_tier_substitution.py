"""Tests for tier substitution functionality."""

import pytest
from app.utils.tier_utils import (
    convert_tier_to_base_units,
    convert_base_units_to_tier_count,
    extract_base_code_and_tier,
    count_achievements_with_tier_substitution,
)


def test_convert_tier_to_base_units():
    """Test converting tier counts to bronze units."""
    # Bronze: 1 bronze = 1 bronze unit
    assert convert_tier_to_base_units("bronze", 1) == 1
    assert convert_tier_to_base_units("bronze", 4) == 4
    
    # Silver: 1 silver = 2 bronze units
    assert convert_tier_to_base_units("silver", 1) == 2
    assert convert_tier_to_base_units("silver", 2) == 4
    
    # Gold: 1 gold = 4 bronze units (2^2)
    assert convert_tier_to_base_units("gold", 1) == 4
    assert convert_tier_to_base_units("gold", 2) == 8
    
    # Platinum: 1 platinum = 8 bronze units (2^3)
    assert convert_tier_to_base_units("platinum", 1) == 8


def test_convert_base_units_to_tier_count():
    """Test converting bronze units to tier counts."""
    # 2 bronze units = 1 silver
    assert convert_base_units_to_tier_count(2, "silver") == 1
    assert convert_base_units_to_tier_count(4, "silver") == 2
    
    # 4 bronze units = 1 gold
    assert convert_base_units_to_tier_count(4, "gold") == 1
    assert convert_base_units_to_tier_count(8, "gold") == 2
    
    # 8 bronze units = 1 platinum
    assert convert_base_units_to_tier_count(8, "platinum") == 1


def test_extract_base_code_and_tier():
    """Test extracting base code and tier from achievement codes."""
    base, tier = extract_base_code_and_tier("speed-demon-bronze")
    assert base == "speed-demon"
    assert tier == "bronze"
    
    base, tier = extract_base_code_and_tier("math-master-gold")
    assert base == "math-master"
    assert tier == "gold"
    
    base, tier = extract_base_code_and_tier("first-steps")
    assert base == "first-steps"
    assert tier is None


def test_tier_substitution_conversion_rates():
    """Test that tier substitution follows the correct conversion rates."""
    # 4 bronze = 2 silver = 1 gold
    bronze_units_4 = convert_tier_to_base_units("bronze", 4)
    silver_units_2 = convert_tier_to_base_units("silver", 2)
    gold_units_1 = convert_tier_to_base_units("gold", 1)
    
    assert bronze_units_4 == silver_units_2 == gold_units_1 == 4
    
    # 4 gold = 2 platinum = 1 diamond
    gold_units_4 = convert_tier_to_base_units("gold", 4)
    platinum_units_2 = convert_tier_to_base_units("platinum", 2)
    diamond_units_1 = convert_tier_to_base_units("diamond", 1)
    
    # gold = 4 bronze, so 4 gold = 16 bronze
    # platinum = 8 bronze, so 2 platinum = 16 bronze
    # diamond = 16 bronze, so 1 diamond = 16 bronze
    assert gold_units_4 == platinum_units_2 == diamond_units_1 == 16


def test_count_achievements_with_tier_substitution():
    """Test counting achievements with tier substitution."""
    # User has: 2 gold, 1 silver, 3 bronze of speed-demon
    # Target: speed-demon-bronze, quantity: 10
    user_achievements = [
        {"code": "speed-demon-gold", "achievement_metadata": None},
        {"code": "speed-demon-gold", "achievement_metadata": None},
        {"code": "speed-demon-silver", "achievement_metadata": None},
        {"code": "speed-demon-bronze", "achievement_metadata": None},
        {"code": "speed-demon-bronze", "achievement_metadata": None},
        {"code": "speed-demon-bronze", "achievement_metadata": None},
    ]
    
    equivalent_count, exact_count = count_achievements_with_tier_substitution(
        user_achievements,
        "speed-demon-bronze",
        10,
        None
    )
    
    # 2 gold = 8 bronze units, 1 silver = 2 bronze units, 3 bronze = 3 bronze units
    # Total = 13 bronze units = 13 bronze achievements
    assert equivalent_count == 13
    # Exact count: all 6 achievements match (same or higher tier)
    assert exact_count == 6

