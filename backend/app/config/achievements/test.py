"""Test achievement definitions."""

from typing import Any

from app.utils.tier_utils import ALL_TIERS

# Old test achievements removed - replaced by generic {test-type}-{tier} achievements
# generated dynamically by _generate_test_tier_achievements()
TEST_ACHIEVEMENTS: dict[str, dict[str, Any]] = {}


def _generate_test_tier_achievements() -> dict[str, dict[str, Any]]:
    """Generate test tier achievement definitions for all test types using metal/prestige tier system."""
    test_types = [
        ("addition-1digit", "1-Digit Addition"),
        ("addition-2digit", "2-Digit Addition"),
        ("addition-3digit", "3-Digit Addition"),
        ("subtraction-1digit", "1-Digit Subtraction"),
        ("subtraction-2digit", "2-Digit Subtraction"),
        ("subtraction-3digit", "3-Digit Subtraction"),
        ("multiplication-2", "Times Table ×2"),
        ("multiplication-3", "Times Table ×3"),
        ("multiplication-4", "Times Table ×4"),
        ("multiplication-5", "Times Table ×5"),
        ("multiplication-6", "Times Table ×6"),
        ("multiplication-7", "Times Table ×7"),
        ("multiplication-8", "Times Table ×8"),
        ("multiplication-9", "Times Table ×9"),
        ("multiplication-10", "Times Table ×10"),
        ("multiplication-11", "Times Table ×11"),
        ("multiplication-12", "Times Table ×12"),
        ("multiplication-2digit", "2-Digit Multiplication"),
        ("multiplication-3digit", "3-Digit Multiplication"),
        ("division-1digit", "1-Digit Division"),
        ("division-2digit", "2-Digit Division"),
        ("division-3digit", "3-Digit Division"),
    ]
    
    # Test tier requirements matching the new system
    TEST_TIER_REQUIREMENTS = {
        "bronze": {
            "min_accuracy": None,
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
        },
    }
    
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
    
    achievements = {}
    for test_type, display_name in test_types:
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
