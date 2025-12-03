"""Milestone achievement definitions with full tier progression."""

from typing import Any

from app.utils.tier_utils import ALL_TIERS

# Milestone achievements
MILESTONE_ACHIEVEMENTS: dict[str, dict[str, Any]] = {
    # Basic milestones (keep existing)
    "first-steps": {
        "title": "First Steps",
        "description": "Answer your first question",
        "icon": "👣",
        "category": "milestone",
        "tier": "bronze",
        "requirements": {
            "type": "question_count",
            "min_questions": 1
        }
    },
    "first-victory": {
        "title": "First Victory",
        "description": "Complete your first session",
        "icon": "🎯",
        "category": "milestone",
        "tier": "silver",
        "requirements": {
            "type": "question_count",
            "min_questions": 1
        }
    },
}


def _generate_week_warrior_achievements() -> dict[str, dict[str, Any]]:
    """Generate Week Warrior (streak) achievement definitions."""
    achievements = {}
    
    tier_requirements = {
        "bronze": {"min_streak_days": 7},
        "silver": {"min_streak_days": 14},
        "gold": {"min_streak_days": 30},
        "platinum": {"min_streak_days": 60},
        "diamond": {"min_streak_days": 90},
        "master": {"min_streak_days": 180},
        "grandmaster": {"min_streak_days": 365},
        "legendary": {"min_streak_days": 730},
        "mythic": {"min_streak_days": 1000},
        "divine": {"min_streak_days": 2000},
        "champion": {"min_streak_days": 2000},  # Same as divine, requires server record
    }
    
    for tier in ALL_TIERS:
        code = f"week-warrior-{tier}"
        req = tier_requirements.get(tier, {})
        min_days = req.get("min_streak_days", 7)
        
        tier_title = tier.capitalize()
        title = f"Week Warrior ({tier_title})"
        
        if tier == "champion":
            description = f"Longest streak on server ({min_days}+ days)"
        else:
            description = f"Complete a {min_days} day streak"
        
        requirements = {
            "type": "streak",
            "min_streak_days": min_days,
        }
        
        if tier == "champion":
            requirements["requires_champion_check"] = True
        
        achievements[code] = {
            "title": title,
            "description": description,
            "icon": "🔥",
            "category": "consistency",
            "tier": tier,
            "requirements": requirements,
        }
    
    return achievements


def _generate_question_master_achievements() -> dict[str, dict[str, Any]]:
    """Generate Question Master (total questions) achievement definitions."""
    achievements = {}
    
    tier_requirements = {
        "bronze": {"min_questions": 100},
        "silver": {"min_questions": 500},
        "gold": {"min_questions": 1000},
        "platinum": {"min_questions": 2500},
        "diamond": {"min_questions": 5000},
        "master": {"min_questions": 10000},
        "grandmaster": {"min_questions": 25000},
        "legendary": {"min_questions": 50000},
        "mythic": {"min_questions": 100000},
        "divine": {"min_questions": 250000},
        "champion": {"min_questions": 250000},  # Same as divine, requires server record
    }
    
    for tier in ALL_TIERS:
        code = f"question-master-{tier}"
        req = tier_requirements.get(tier, {})
        min_questions = req.get("min_questions", 100)
        
        tier_title = tier.capitalize()
        title = f"Question Master ({tier_title})"
        
        if tier == "champion":
            description = f"Most questions answered on server ({min_questions}+ total)"
        else:
            description = f"Answer {min_questions}+ total questions"
        
        requirements = {
            "type": "question_count",
            "min_questions": min_questions,
        }
        
        if tier == "champion":
            requirements["requires_champion_check"] = True
        
        achievements[code] = {
            "title": title,
            "description": description,
            "icon": "📚",
            "category": "milestone",
            "tier": tier,
            "requirements": requirements,
        }
    
    return achievements


def _generate_speed_demon_achievements() -> dict[str, dict[str, Any]]:
    """Generate Speed Demon (average speed) achievement definitions."""
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
        code = f"speed-demon-{tier}"
        req = tier_requirements.get(tier, {})
        max_speed = req.get("max_avg_speed", 5.0)
        
        tier_title = tier.capitalize()
        title = f"Speed Demon ({tier_title})"
        
        if tier == "champion":
            description = f"Fastest average speed on server (<{max_speed}s/question)"
        else:
            description = f"Average <{max_speed}s per question"
        
        requirements = {
            "type": "speed",
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


def _generate_perfect_streak_achievements() -> dict[str, dict[str, Any]]:
    """Generate Perfect Streak (consecutive perfect sessions) achievement definitions."""
    achievements = {}
    
    tier_requirements = {
        "bronze": {"min_sessions": 3},
        "silver": {"min_sessions": 5},
        "gold": {"min_sessions": 10},
        "platinum": {"min_sessions": 20},
        "diamond": {"min_sessions": 50},
        "master": {"min_sessions": 100},
        "grandmaster": {"min_sessions": 250},
        "legendary": {"min_sessions": 500},
        "mythic": {"min_sessions": 1000},
        "divine": {"min_sessions": 2500},
        "champion": {"min_sessions": 2500},  # Same as divine, requires server record
    }
    
    for tier in ALL_TIERS:
        code = f"perfect-streak-{tier}"
        req = tier_requirements.get(tier, {})
        min_sessions = req.get("min_sessions", 3)
        
        tier_title = tier.capitalize()
        title = f"Perfect Streak ({tier_title})"
        
        if tier == "champion":
            description = f"Longest perfect streak on server ({min_sessions}+ consecutive perfect sessions)"
        else:
            description = f"{min_sessions} consecutive perfect sessions"
        
        requirements = {
            "type": "perfect_sessions",
            "min_sessions": min_sessions,
        }
        
        if tier == "champion":
            requirements["requires_champion_check"] = True
        
        achievements[code] = {
            "title": title,
            "description": description,
            "icon": "🌟",
            "category": "consistency",
            "tier": tier,
            "requirements": requirements,
        }
    
    return achievements


# Generate all milestone achievements
MILESTONE_ACHIEVEMENTS.update(_generate_week_warrior_achievements())
MILESTONE_ACHIEVEMENTS.update(_generate_question_master_achievements())
MILESTONE_ACHIEVEMENTS.update(_generate_speed_demon_achievements())
MILESTONE_ACHIEVEMENTS.update(_generate_perfect_streak_achievements())

