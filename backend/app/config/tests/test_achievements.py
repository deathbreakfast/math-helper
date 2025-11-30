"""Test achievement definitions for new test types.

This module generates B-SSS tier achievements for all new test definitions.
"""

from typing import Any

from ..tests.test_definitions import NEW_TEST_DEFINITIONS


def _generate_new_test_tier_achievements() -> dict[str, dict[str, Any]]:
    """Generate test tier achievement definitions for all new test types.
    
    Returns:
        Dictionary of achievement code -> achievement definition
    """
    tiers = [
        {
            "suffix": "b",
            "title_suffix": "Rank B",
            "description": "Complete test",
            "icon": "📘",
            "category": "test",
            "requirements": {
                "type": "test_tier",
                "tier": "b",
                "min_question_count": 30,
            }
        },
        {
            "suffix": "a",
            "title_suffix": "Rank A",
            "description": "100% accuracy (under 30 questions)",
            "icon": "📗",
            "category": "test",
            "requirements": {
                "type": "test_tier",
                "tier": "a",
                "min_accuracy": 100,
                "max_question_count": 29,
            }
        },
        {
            "suffix": "s",
            "title_suffix": "Rank S",
            "description": "Perfect score with speed",
            "icon": "⭐",
            "category": "test",
            "requirements": {
                "type": "test_tier",
                "tier": "s",
                "min_accuracy": 100,
                "min_question_count": 31,
                "max_question_count": 59,
                "max_speed": 6,
            }
        },
        {
            "suffix": "ss",
            "title_suffix": "Rank SS",
            "description": "Elite performance",
            "icon": "🌟",
            "category": "test",
            "requirements": {
                "type": "test_tier",
                "tier": "ss",
                "min_accuracy": 100,
                "max_question_count": 90,
                "max_speed": 4,
            }
        },
        {
            "suffix": "sss",
            "title_suffix": "Rank SSS",
            "description": "Legendary mastery",
            "icon": "💎",
            "category": "test",
            "requirements": {
                "type": "test_tier",
                "tier": "sss",
                "min_accuracy": 100,
                "min_question_count": 90,
                "max_speed": 3,
            }
        },
    ]
    
    achievements = {}
    for test_type, (_, _, _, _, display_name) in NEW_TEST_DEFINITIONS.items():
        for tier_config in tiers:
            code = f"{test_type}-{tier_config['suffix']}"
            achievements[code] = {
                "title": f"{display_name} - {tier_config['title_suffix']}",
                "description": tier_config["description"],
                "icon": tier_config["icon"],
                "category": tier_config["category"],
                "requirements": {
                    **tier_config["requirements"],
                    "test_type": test_type,
                }
            }
    
    return achievements


# Generate all tier achievements for new test types
NEW_TEST_TIER_ACHIEVEMENTS = _generate_new_test_tier_achievements()


def get_new_test_achievements() -> dict[str, dict[str, Any]]:
    """Get all tier achievements for new test types.
    
    Returns:
        Dictionary of achievement code -> achievement definition
    """
    return NEW_TEST_TIER_ACHIEVEMENTS.copy()

