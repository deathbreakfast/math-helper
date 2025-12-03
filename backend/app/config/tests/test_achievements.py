"""Test achievement definitions for new test types with metal/prestige tier system."""

from typing import Any

from app.utils.tier_utils import ALL_TIERS

from ..tests.test_definitions import NEW_TEST_DEFINITIONS

# Tier requirements for test achievements
TEST_TIER_REQUIREMENTS = {
    "bronze": {
        "min_accuracy": None,  # Just complete the test
        "min_question_count": 1,
        "max_question_count": None,
        "max_speed": None,
    },
    "silver": {
        "min_accuracy": 0.90,
        "min_question_count": 1,
        "max_question_count": 29,
        "max_speed": None,
    },
    "gold": {
        "min_accuracy": 0.95,
        "min_question_count": 31,
        "max_question_count": 59,
        "max_speed": None,
    },
    "platinum": {
        "min_accuracy": 0.98,
        "min_question_count": 60,
        "max_question_count": 89,
        "max_speed": 5.0,
    },
    "diamond": {
        "min_accuracy": 1.0,
        "min_question_count": 90,
        "max_question_count": None,
        "max_speed": 4.0,
    },
    "master": {
        "min_accuracy": 1.0,
        "min_question_count": 100,
        "max_question_count": None,
        "max_speed": 3.5,
    },
    "grandmaster": {
        "min_accuracy": 1.0,
        "min_question_count": 100,
        "max_question_count": None,
        "max_speed": 3.0,
    },
    "legendary": {
        "min_accuracy": 1.0,
        "min_question_count": 100,
        "max_question_count": None,
        "max_speed": 2.5,
    },
    "mythic": {
        "min_accuracy": 1.0,
        "min_question_count": 100,
        "max_question_count": None,
        "max_speed": 2.0,
    },
    "divine": {
        "min_accuracy": 1.0,
        "min_question_count": 100,
        "max_question_count": None,
        "max_speed": 1.5,
    },
    "champion": {
        "min_accuracy": 1.0,
        "min_question_count": 100,
        "max_question_count": None,
        "max_speed": 1.5,
        # Champion requires server record check (handled in achievement service)
    },
}

# Icon mapping for tiers
TIER_ICONS = {
    "bronze": "📘",
    "silver": "📗",
    "gold": "⭐",
    "platinum": "💎",
    "diamond": "💠",
    "master": "👑",
    "grandmaster": "🌟",
    "legendary": "🔥",
    "mythic": "✨",
    "divine": "⚡",
    "champion": "🏆",
}


def _generate_new_test_tier_achievements() -> dict[str, dict[str, Any]]:
    """Generate test tier achievement definitions for all new test types using metal/prestige tiers.
    
    Returns:
        Dictionary of achievement code -> achievement definition
    """
    achievements = {}
    
    for test_type, (_, _, _, _, display_name) in NEW_TEST_DEFINITIONS.items():
        for tier in ALL_TIERS:
            code = f"{test_type}-{tier}"
            
            req = TEST_TIER_REQUIREMENTS.get(tier, {})
            min_accuracy = req.get("min_accuracy")
            min_question_count = req.get("min_question_count", 1)
            max_question_count = req.get("max_question_count")
            max_speed = req.get("max_speed")
            
            # Build title
            tier_title = tier.capitalize()
            title = f"{display_name} ({tier_title})"
            
            # Build description
            if tier == "bronze":
                description = "Complete test"
            elif min_accuracy:
                description_parts = []
                if min_accuracy == 1.0:
                    description_parts.append("100% accuracy")
                else:
                    description_parts.append(f"{min_accuracy:.0%}+ accuracy")
                
                if max_question_count:
                    description_parts.append(f"under {max_question_count + 1} questions")
                elif min_question_count:
                    description_parts.append(f"{min_question_count}+ questions")
                
                if max_speed:
                    description_parts.append(f"<{max_speed}s/question")
                
                description = ", ".join(description_parts)
            else:
                description = "Complete test"
            
            icon = TIER_ICONS.get(tier, "⭐")
            
            # Requirements structure
            requirements = {
                "type": "test_tier",
                "test_type": test_type,
                "tier": tier,
            }
            
            if min_accuracy:
                requirements["min_accuracy"] = int(min_accuracy * 100) if min_accuracy < 1.0 else 100
            
            if min_question_count:
                requirements["min_question_count"] = min_question_count
            
            if max_question_count:
                requirements["max_question_count"] = max_question_count
            
            if max_speed:
                requirements["max_speed"] = max_speed
            
            if tier == "champion":
                requirements["requires_champion_check"] = True
            
            achievements[code] = {
                "title": title,
                "description": description,
                "icon": icon,
                "category": "test",
                "tier": tier,
                "requirements": requirements,
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
