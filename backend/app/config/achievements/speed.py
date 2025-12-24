"""Speed achievement definitions."""

from typing import Any

from app.utils.tier_utils import ALL_TIERS

# Lightning Fast achievements - level-specific speed achievements
# These are awarded per level with metadata {"level": N}
def _generate_lightning_fast_achievements() -> dict[str, dict[str, Any]]:
    """Generate Lightning Fast (level-specific speed) achievement definitions."""
    achievements = {}
    
    tier_requirements = {
        "bronze": {"max_avg_speed": 5.0, "min_questions": 50},
        "silver": {"max_avg_speed": 4.0, "min_questions": 100},
        "gold": {"max_avg_speed": 3.0, "min_questions": 150},
        "platinum": {"max_avg_speed": 2.7, "min_questions": 200},
        "diamond": {"max_avg_speed": 2.4, "min_questions": 300},
        "master": {"max_avg_speed": 2.1, "min_questions": 400},
        "grandmaster": {"max_avg_speed": 1.8, "min_questions": 500},
        "legendary": {"max_avg_speed": 1.5, "min_questions": 750},
        "mythic": {"max_avg_speed": 1.3, "min_questions": 1000},
        "divine": {"max_avg_speed": 1.2, "min_questions": 1500},
        "champion": {"max_avg_speed": 1.2, "min_questions": 1500},  # Same as divine, requires server record
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
            "min_questions": req.get("min_questions", 50),  # Minimum questions per tier
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
            "constraint": {
                "allow_multiple_per_tier": True,
                "allow_multiple_per_session": True,
                "unique_achievement": False,
            },
        }
    
    return achievements


SPEED_ACHIEVEMENTS: dict[str, dict[str, Any]] = {}
SPEED_ACHIEVEMENTS.update(_generate_lightning_fast_achievements())
