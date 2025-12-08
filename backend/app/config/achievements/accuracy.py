"""Generic accuracy achievement definitions with tiered system."""

from typing import Any

from app.utils.tier_utils import ALL_TIERS

# Legacy {operation}-basics-{tier} achievements removed
# These are redundant and covered by test achievements and regular speed/accuracy achievements
# All references have been replaced with test achievements in level progression

def _generate_level_master_achievements() -> dict[str, dict[str, Any]]:
    """Generate Level Master (consecutive correct at specific level) achievement definitions."""
    achievements = {}
    
    tier_requirements = {
        "bronze": {"min_consecutive": 30},
        "silver": {"min_consecutive": 60},
        "gold": {"min_consecutive": 120},
        "platinum": {"min_consecutive": 240},
        "diamond": {"min_consecutive": 480},
        "master": {"min_consecutive": 960},
        "grandmaster": {"min_consecutive": 1920},
        "legendary": {"min_consecutive": 3840},
        "mythic": {"min_consecutive": 7680},
        "divine": {"min_consecutive": 15360},
        "champion": {"min_consecutive": 15360},  # Same as divine, requires server record
    }
    
    for tier in ALL_TIERS:
        code = f"level-master-{tier}"
        req = tier_requirements.get(tier, {})
        min_consecutive = req.get("min_consecutive", 30)
        
        tier_title = tier.capitalize()
        title = f"Level Master ({tier_title})"
        
        if tier == "champion":
            description = f"Longest consecutive correct at any level on server ({min_consecutive}+ correct)"
        else:
            description = f"{min_consecutive} consecutive correct at any level"
        
        requirements = {
            "type": "level_master",
            "min_consecutive": min_consecutive,
        }
        
        if tier == "champion":
            requirements["requires_champion_check"] = True
        
        achievements[code] = {
            "title": title,
            "description": description,
            "icon": "🎯",
            "category": "accuracy",
            "tier": tier,
            "requirements": requirements,
        }
    
    return achievements


def _generate_accuracy_ace_achievements() -> dict[str, dict[str, Any]]:
    """Generate Accuracy Ace achievement definitions.
    
    Like Lightning Fast, but for accuracy. Session-based accuracy achievement.
    Awarded per session with high accuracy.
    """
    achievements = {}
    
    tier_requirements = {
        "bronze": {"min_accuracy": 0.80},  # 80%
        "silver": {"min_accuracy": 0.85},  # 85%
        "gold": {"min_accuracy": 0.90},  # 90%
        "platinum": {"min_accuracy": 0.95},  # 95%
        "diamond": {"min_accuracy": 0.98},  # 98%
        "master": {"min_accuracy": 0.99},  # 99%
        "grandmaster": {"min_accuracy": 1.0},  # 100%
        "legendary": {"min_accuracy": 1.0},  # 100%
        "mythic": {"min_accuracy": 1.0},  # 100%
        "divine": {"min_accuracy": 1.0},  # 100%
        "champion": {"min_accuracy": 1.0},  # 100%, requires server record
    }
    
    for tier in ALL_TIERS:
        code = f"accuracy-ace-{tier}"
        req = tier_requirements.get(tier, {})
        min_accuracy = req.get("min_accuracy", 0.80)
        
        tier_title = tier.capitalize()
        title = f"Accuracy Ace ({tier_title})"
        
        if tier == "champion":
            description = f"Highest session accuracy on server ({min_accuracy * 100:.0f}%+)"
        else:
            description = f"Session accuracy of {min_accuracy * 100:.0f}% or higher"
        
        requirements = {
            "type": "accuracy_ace",
            "min_accuracy": min_accuracy,
            "min_questions": 10,  # Minimum questions to qualify
        }
        
        if tier == "champion":
            requirements["requires_champion_check"] = True
        
        achievements[code] = {
            "title": title,
            "description": description,
            "icon": "🎯",
            "category": "accuracy",
            "tier": tier,
            "requirements": requirements,
        }
    
    return achievements


ACCURACY_ACHIEVEMENTS: dict[str, dict[str, Any]] = {}
ACCURACY_ACHIEVEMENTS.update(_generate_level_master_achievements())
ACCURACY_ACHIEVEMENTS.update(_generate_accuracy_ace_achievements())
