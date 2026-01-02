"""Comprehensive tests for tier_utils.

Tests cover all functions in tier_utils to achieve >80% coverage.
"""

import json
import pytest

from app.utils.tier_utils import (
    get_tier_hierarchy,
    get_all_tiers,
    map_old_tier_to_new,
    is_tier_higher_than,
    get_tier_value,
    get_highest_tier,
    convert_tier_to_base_units,
    convert_base_units_to_tier_count,
    extract_base_code_and_tier,
    count_achievements_with_tier_substitution,
)


class TestTierUtils:
    """Test suite for tier_utils functions."""

    def test_get_tier_hierarchy(self):
        """Test get_tier_hierarchy returns tier hierarchy."""
        hierarchy = get_tier_hierarchy()
        
        assert isinstance(hierarchy, dict)
        assert hierarchy["bronze"] == 1
        assert hierarchy["champion"] == 11
        assert len(hierarchy) == 11

    def test_get_all_tiers(self):
        """Test get_all_tiers returns all tiers in order."""
        tiers = get_all_tiers()
        
        assert isinstance(tiers, list)
        assert tiers[0] == "bronze"
        assert tiers[-1] == "champion"
        assert len(tiers) == 11

    def test_map_old_tier_to_new_b(self):
        """Test map_old_tier_to_new maps B to bronze."""
        assert map_old_tier_to_new("B") == "bronze"
        assert map_old_tier_to_new("b") == "bronze"

    def test_map_old_tier_to_new_a(self):
        """Test map_old_tier_to_new maps A to silver."""
        assert map_old_tier_to_new("A") == "silver"
        assert map_old_tier_to_new("a") == "silver"

    def test_map_old_tier_to_new_s(self):
        """Test map_old_tier_to_new maps S to gold."""
        assert map_old_tier_to_new("S") == "gold"
        assert map_old_tier_to_new("s") == "gold"

    def test_map_old_tier_to_new_ss(self):
        """Test map_old_tier_to_new maps SS to platinum."""
        assert map_old_tier_to_new("SS") == "platinum"
        assert map_old_tier_to_new("ss") == "platinum"

    def test_map_old_tier_to_new_sss(self):
        """Test map_old_tier_to_new maps SSS to diamond."""
        # Note: The mapping checks "ss" before "sss", so we need to check the actual mapping
        # Looking at the code, "ss" maps to "platinum" and "sss" should map to "diamond"
        # But the function checks in order, so "ss" might match first
        # Actually, the OLD_TIER_TO_NEW dict has "ss": "platinum" and "sss": "diamond"
        # But map_old_tier_to_new uses .get() which doesn't check substring
        assert map_old_tier_to_new("sss") == "diamond"
        assert map_old_tier_to_new("SSS") == "diamond"

    def test_map_old_tier_to_new_unknown(self):
        """Test map_old_tier_to_new returns lowercase for unknown tiers."""
        assert map_old_tier_to_new("unknown") == "unknown"
        assert map_old_tier_to_new("gold") == "gold"

    def test_is_tier_higher_than_true(self):
        """Test is_tier_higher_than returns True when tier1 > tier2."""
        assert is_tier_higher_than("gold", "bronze") is True
        assert is_tier_higher_than("champion", "divine") is True
        assert is_tier_higher_than("silver", "bronze") is True

    def test_is_tier_higher_than_false(self):
        """Test is_tier_higher_than returns False when tier1 <= tier2."""
        assert is_tier_higher_than("bronze", "gold") is False
        assert is_tier_higher_than("bronze", "bronze") is False
        assert is_tier_higher_than("silver", "gold") is False

    def test_is_tier_higher_than_case_insensitive(self):
        """Test is_tier_higher_than is case insensitive."""
        assert is_tier_higher_than("GOLD", "BRONZE") is True
        assert is_tier_higher_than("Gold", "Bronze") is True

    def test_is_tier_higher_than_unknown_tier(self):
        """Test is_tier_higher_than handles unknown tiers."""
        # Unknown tier returns 0, so gold (3) > unknown (0) is True
        assert is_tier_higher_than("unknown", "bronze") is False  # 0 > 1 is False
        assert is_tier_higher_than("gold", "unknown") is True  # 3 > 0 is True

    def test_get_tier_value(self):
        """Test get_tier_value returns correct values."""
        assert get_tier_value("bronze") == 1
        assert get_tier_value("silver") == 2
        assert get_tier_value("gold") == 3
        assert get_tier_value("champion") == 11

    def test_get_tier_value_case_insensitive(self):
        """Test get_tier_value is case insensitive."""
        assert get_tier_value("BRONZE") == 1
        assert get_tier_value("Gold") == 3

    def test_get_tier_value_unknown(self):
        """Test get_tier_value returns 0 for unknown tiers."""
        assert get_tier_value("unknown") == 0

    def test_get_highest_tier(self):
        """Test get_highest_tier returns highest tier."""
        tiers = ["bronze", "silver", "gold"]
        assert get_highest_tier(tiers) == "gold"

    def test_get_highest_tier_single(self):
        """Test get_highest_tier with single tier."""
        assert get_highest_tier(["bronze"]) == "bronze"

    def test_get_highest_tier_empty(self):
        """Test get_highest_tier returns None for empty list."""
        assert get_highest_tier([]) is None

    def test_get_highest_tier_case_insensitive(self):
        """Test get_highest_tier is case insensitive."""
        tiers = ["BRONZE", "GOLD", "SILVER"]
        # Function returns the original string from the list, not lowercase
        result = get_highest_tier(tiers)
        assert result in ["GOLD", "gold"]  # Could be either depending on implementation
        # Verify it's the highest tier by value
        assert get_tier_value(result) == 3

    def test_get_highest_tier_unknown_tier(self):
        """Test get_highest_tier handles unknown tiers."""
        tiers = ["bronze", "unknown", "gold"]
        # Should return gold (highest known tier)
        assert get_highest_tier(tiers) == "gold"

    def test_convert_tier_to_base_units_bronze(self):
        """Test convert_tier_to_base_units for bronze."""
        assert convert_tier_to_base_units("bronze", 1) == 1
        assert convert_tier_to_base_units("bronze", 4) == 4

    def test_convert_tier_to_base_units_silver(self):
        """Test convert_tier_to_base_units for silver."""
        assert convert_tier_to_base_units("silver", 1) == 2
        assert convert_tier_to_base_units("silver", 2) == 4

    def test_convert_tier_to_base_units_gold(self):
        """Test convert_tier_to_base_units for gold."""
        assert convert_tier_to_base_units("gold", 1) == 4
        assert convert_tier_to_base_units("gold", 2) == 8

    def test_convert_tier_to_base_units_platinum(self):
        """Test convert_tier_to_base_units for platinum."""
        assert convert_tier_to_base_units("platinum", 1) == 8
        assert convert_tier_to_base_units("platinum", 2) == 16

    def test_convert_tier_to_base_units_unknown(self):
        """Test convert_tier_to_base_units for unknown tier."""
        assert convert_tier_to_base_units("unknown", 5) == 5

    def test_convert_base_units_to_tier_count_bronze(self):
        """Test convert_base_units_to_tier_count for bronze."""
        assert convert_base_units_to_tier_count(4, "bronze") == 4
        assert convert_base_units_to_tier_count(1, "bronze") == 1

    def test_convert_base_units_to_tier_count_silver(self):
        """Test convert_base_units_to_tier_count for silver."""
        assert convert_base_units_to_tier_count(4, "silver") == 2
        assert convert_base_units_to_tier_count(2, "silver") == 1

    def test_convert_base_units_to_tier_count_gold(self):
        """Test convert_base_units_to_tier_count for gold."""
        assert convert_base_units_to_tier_count(4, "gold") == 1
        assert convert_base_units_to_tier_count(8, "gold") == 2

    def test_convert_base_units_to_tier_count_unknown(self):
        """Test convert_base_units_to_tier_count for unknown tier."""
        assert convert_base_units_to_tier_count(5, "unknown") == 5

    def test_extract_base_code_and_tier_with_tier(self):
        """Test extract_base_code_and_tier extracts tier from code."""
        base, tier = extract_base_code_and_tier("speed-demon-bronze")
        assert base == "speed-demon"
        assert tier == "bronze"

    def test_extract_base_code_and_tier_no_tier(self):
        """Test extract_base_code_and_tier returns None for tier when no tier found."""
        base, tier = extract_base_code_and_tier("first-steps")
        assert base == "first-steps"
        assert tier is None

    def test_extract_base_code_and_tier_longest_first(self):
        """Test extract_base_code_and_tier checks longest tiers first."""
        # "grandmaster" should match before "master" when code ends with "-grandmaster"
        # The function checks in reverse order (longest first)
        base, tier = extract_base_code_and_tier("math-master-grandmaster")
        # Should extract "grandmaster" as the tier (not "master")
        assert tier == "grandmaster"
        # Base should be "math-master" (everything before "-grandmaster")
        assert base == "math-master"

    def test_count_achievements_with_tier_substitution_no_tier(self):
        """Test count_achievements_with_tier_substitution for code without tier."""
        achievements = [
            {"code": "first-steps", "achievement_metadata": None}
        ]
        
        equivalent, actual = count_achievements_with_tier_substitution(
            achievements,
            "first-steps",
            1
        )
        
        assert equivalent == 1
        assert actual == 1

    def test_count_achievements_with_tier_substitution_exact_match(self):
        """Test count_achievements_with_tier_substitution with exact tier match."""
        achievements = [
            {"code": "speed-demon-bronze", "achievement_metadata": None}
        ]
        
        equivalent, actual = count_achievements_with_tier_substitution(
            achievements,
            "speed-demon-bronze",
            1
        )
        
        assert equivalent == 1
        assert actual == 1

    def test_count_achievements_with_tier_substitution_higher_tier(self):
        """Test count_achievements_with_tier_substitution with higher tier."""
        achievements = [
            {"code": "speed-demon-silver", "achievement_metadata": None}
        ]
        
        equivalent, actual = count_achievements_with_tier_substitution(
            achievements,
            "speed-demon-bronze",
            1
        )
        
        # 1 silver = 2 bronze units, so equivalent count should be 2
        assert equivalent == 2
        assert actual == 1  # 1 achievement at higher tier

    def test_count_achievements_with_tier_substitution_multiple_tiers(self):
        """Test count_achievements_with_tier_substitution with multiple tiers."""
        achievements = [
            {"code": "speed-demon-bronze", "achievement_metadata": None},
            {"code": "speed-demon-bronze", "achievement_metadata": None},
            {"code": "speed-demon-silver", "achievement_metadata": None},
        ]
        
        equivalent, actual = count_achievements_with_tier_substitution(
            achievements,
            "speed-demon-bronze",
            1
        )
        
        # 2 bronze + 1 silver = 2 + 2 = 4 bronze units
        assert equivalent == 4
        assert actual == 3  # 3 achievements total

    def test_count_achievements_with_tier_substitution_with_metadata(self):
        """Test count_achievements_with_tier_substitution with metadata filter."""
        achievements = [
            {"code": "math-master-bronze", "achievement_metadata": {"concept_id": "c_concept_001"}},
            {"code": "math-master-bronze", "achievement_metadata": {"concept_id": "c_concept_002"}},
        ]
        
        metadata_filter = {"concept_id": "c_concept_001"}
        
        equivalent, actual = count_achievements_with_tier_substitution(
            achievements,
            "math-master-bronze",
            1,
            metadata_filter=metadata_filter
        )
        
        # Should only count achievement with matching metadata
        assert equivalent == 1
        assert actual == 1

    def test_count_achievements_with_tier_substitution_metadata_string(self):
        """Test count_achievements_with_tier_substitution handles string metadata."""
        achievements = [
            {"code": "math-master-bronze", "achievement_metadata": json.dumps({"concept_id": "c_concept_001"})},
        ]
        
        metadata_filter = {"concept_id": "c_concept_001"}
        
        equivalent, actual = count_achievements_with_tier_substitution(
            achievements,
            "math-master-bronze",
            1,
            metadata_filter=metadata_filter
        )
        
        # Should parse JSON string and match
        assert equivalent == 1
        assert actual == 1

    def test_count_achievements_with_tier_substitution_invalid_json(self):
        """Test count_achievements_with_tier_substitution handles invalid JSON."""
        achievements = [
            {"code": "math-master-bronze", "achievement_metadata": "invalid json"},
        ]
        
        metadata_filter = {"concept_id": "c_concept_001"}
        
        equivalent, actual = count_achievements_with_tier_substitution(
            achievements,
            "math-master-bronze",
            1,
            metadata_filter=metadata_filter
        )
        
        # Should not match invalid JSON
        assert equivalent == 0
        assert actual == 0

    def test_count_achievements_with_tier_substitution_different_base_code(self):
        """Test count_achievements_with_tier_substitution ignores different base codes."""
        achievements = [
            {"code": "speed-demon-bronze", "achievement_metadata": None},
            {"code": "question-master-bronze", "achievement_metadata": None},
        ]
        
        equivalent, actual = count_achievements_with_tier_substitution(
            achievements,
            "speed-demon-bronze",
            1
        )
        
        # Should only count speed-demon achievements
        assert equivalent == 1
        assert actual == 1

    def test_count_achievements_with_tier_substitution_no_tier_in_achievement(self):
        """Test count_achievements_with_tier_substitution handles achievements without tier."""
        achievements = [
            {"code": "speed-demon", "achievement_metadata": None},  # No tier
        ]
        
        equivalent, actual = count_achievements_with_tier_substitution(
            achievements,
            "speed-demon-bronze",
            1
        )
        
        # Should not count achievements without tier
        assert equivalent == 0
        assert actual == 0

