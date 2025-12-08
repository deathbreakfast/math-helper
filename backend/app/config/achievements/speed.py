"""Speed achievement definitions."""

from typing import Any

from app.utils.tier_utils import ALL_TIERS

# Lightning Fast achievements - level-specific speed achievements
# These are awarded per level with metadata {"level": N}
def _generate_lightning_fast_achievements() -> dict[str, dict[str, Any]]:
    """Generate Lightning Fast (level-specific speed) achievement definitions."""
    achievements = {}
    
    tier_requirements = {
        "bronze": {"max_avg_speed": 5.0},
        "silver": {"max_avg_speed": 4.0},
        "gold": {"max_avg_speed": 3.0},
        "platinum": {"max_avg_speed": 2.5},
        "diamond": {"max_avg_speed": 2.0},
        "master": {"max_avg_speed": 1.5},
        "grandmaster": {"max_avg_speed": 1.0},
        "legendary": {"max_avg_speed": 0.8},
        "mythic": {"max_avg_speed": 0.6},
        "divine": {"max_avg_speed": 0.5},
        "champion": {"max_avg_speed": 0.5},  # Same as divine, requires server record
    }
    
    for tier in ALL_TIERS:
        code = f"lightning-fast-{tier}"
        req = tier_requirements.get(tier, {})
        max_speed = req.get("max_avg_speed", 5.0)
        
        tier_title = tier.capitalize()
        title = f"Lightning Fast ({tier_title})"
        
        if tier == "champion":
            description = f"Fastest average speed at any level on server (<{max_speed}s/question)"
        else:
            description = f"Average <{max_speed}s per question at a specific level"
        
        requirements = {
            "type": "lightning_fast",
            "max_speed_seconds": max_speed,
            "min_questions": 10,  # Minimum questions to qualify
        }
        
        if tier == "champion":
            requirements["requires_champion_check"] = True
        
        achievements[code] = {
            "title": title,
            "description": description,
            "icon": "⚡",
            "category": "speed",
            "tier": tier,
            "requirements": requirements,
        }
    
    return achievements


SPEED_ACHIEVEMENTS: dict[str, dict[str, Any]] = {}
SPEED_ACHIEVEMENTS.update(_generate_lightning_fast_achievements())
