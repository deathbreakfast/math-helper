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
        },
        "constraint": {
            "allow_multiple_per_tier": False,
            "allow_multiple_per_session": False,
            "unique_achievement": True,
        },
    },
    "first-victory": {
        "title": "First Victory",
        "description": "Complete your first session",
        "icon": "🎯",
        "category": "milestone",
        "tier": "silver",
        "requirements": {
            "type": "completed_session_count",
            "min_sessions": 1
        },
        "constraint": {
            "allow_multiple_per_tier": False,
            "allow_multiple_per_session": False,
            "unique_achievement": True,
        },
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
            "constraint": {
                "allow_multiple_per_tier": True,
                "allow_multiple_per_session": False,
                "unique_achievement": False,
            },
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
            "constraint": {
                "allow_multiple_per_tier": False,
                "allow_multiple_per_session": False,
                "unique_achievement": False,
            },
        }
    
    return achievements


def _generate_speed_demon_achievements() -> dict[str, dict[str, Any]]:
    """Generate Speed Demon (average speed) achievement definitions."""
    achievements = {}
    
    tier_requirements = {
        "bronze": {"max_avg_speed": 5.0},
        "silver": {"max_avg_speed": 4.0},
        "gold": {"max_avg_speed": 3.0},
        "platinum": {"max_avg_speed": 2.7},
        "diamond": {"max_avg_speed": 2.4},
        "master": {"max_avg_speed": 2.1},
        "grandmaster": {"max_avg_speed": 1.8},
        "legendary": {"max_avg_speed": 1.5},
        "mythic": {"max_avg_speed": 1.3},
        "divine": {"max_avg_speed": 1.2},
        "champion": {"max_avg_speed": 1.2},  # Same as divine, requires server record
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
            "constraint": {
                "allow_multiple_per_tier": True,
                "allow_multiple_per_session": False,
                "unique_achievement": False,
            },
        }
    
    return achievements


def _generate_perfect_streak_achievements() -> dict[str, dict[str, Any]]:
    """Generate Perfect Streak (consecutive perfect sessions) achievement definitions.
    
    Perfect Streak achievements are awarded once per uninterrupted perfect run.
    A run is defined as consecutive perfect sessions (100% accuracy) that ends
    when an imperfect session is encountered. Achievements can be re-awarded
    after a run is broken by an imperfect session.
    
    For example:
    - 3 perfect sessions → awards bronze (once)
    - 4th perfect session → no new award (bronze already awarded for this run)
    - 1 imperfect session → breaks the run
    - 3 more perfect sessions → awards bronze again (new run)
    """
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
            description = f"{min_sessions} consecutive perfect sessions (awarded once per uninterrupted run)"
        
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
            "constraint": {
                "allow_multiple_per_tier": True,
                "allow_multiple_per_session": False,
                "unique_achievement": False,
            },
        }
    
    return achievements


def _generate_math_grandmaster_achievements() -> dict[str, dict[str, Any]]:
    """Generate Math Grandmaster milestone achievement definitions.
    
    Requires having Math Master (Bronze) achievement for all descriptive concepts.
    Previously named "Level Grandmaster", renamed to "Math Grandmaster".
    """
    achievements = {}
    
    code = "math-grandmaster"
    title = "Math Grandmaster"
    description = "Math Master (Bronze) on all descriptive concepts"
    
    requirements = {
        "type": "level_grandmaster",
        "required_achievement": "math-master-bronze",
    }
    
    achievements[code] = {
        "title": title,
        "description": description,
        "icon": "👑",
        "category": "milestone",
        "tier": "bronze",
        "requirements": requirements,
        "constraint": {
            "allow_multiple_per_tier": True,
            "allow_multiple_per_session": True,
            "unique_achievement": False,
        },
    }
    
    return achievements


def _generate_so_wow_achievements() -> dict[str, dict[str, Any]]:
    """Generate So, Wow! achievement definitions.
    
    Awarded for being awarded a new tier. E.g. You get "So, Wow! (Bronze)" when you acquire
    your first bronze tier achievement. You get "So, Wow! (Gold)" when you get your first gold
    achievement. If you only have bronze achievements and you skip to gold, you would get two
    "So, Wow!" achievements, both gold and silver.
    """
    achievements = {}
    
    for tier in ALL_TIERS:
        code = f"so-wow-{tier}"
        tier_title = tier.capitalize()
        title = f"So, Wow! ({tier_title})"
        description = f"Acquire your first {tier_title} tier achievement"
        
        requirements = {
            "type": "so_wow",
            "tier": tier,
        }
        
        achievements[code] = {
            "title": title,
            "description": description,
            "icon": "✨",
            "category": "milestone",
            "tier": tier,
            "requirements": requirements,
            "constraint": {
                "allow_multiple_per_tier": True,
                "allow_multiple_per_session": True,
                "unique_achievement": False,
            },
        }
    
    return achievements


def _generate_human_calculator_achievements() -> dict[str, dict[str, Any]]:
    """Generate Human Calculator achievement definitions.
    
    Like Level Grandmaster, but for Lightning Fast. Requires Lightning Fast (Bronze or Silver) at all levels.
    """
    achievements = {}
    
    # Bronze tier
    code = "human-calculator"
    title = "Human Calculator"
    description = "Lightning Fast (Bronze) on all levels"
    
    requirements = {
        "type": "human_calculator",
        "required_achievement": "lightning-fast-bronze",
    }
    
    achievements[code] = {
        "title": title,
        "description": description,
        "icon": "🧮",
        "category": "milestone",
        "tier": "bronze",
        "requirements": requirements,
        "constraint": {
            "allow_multiple_per_tier": True,
            "allow_multiple_per_session": True,
            "unique_achievement": False,
        },
    }
    
    # Silver tier
    code_silver = "human-calculator-silver"
    title_silver = "Human Calculator (Silver)"
    description_silver = "Lightning Fast (Silver) on all levels"
    
    requirements_silver = {
        "type": "human_calculator",
        "required_achievement": "lightning-fast-silver",
    }
    
    achievements[code_silver] = {
        "title": title_silver,
        "description": description_silver,
        "icon": "🧮",
        "category": "milestone",
        "tier": "silver",
        "requirements": requirements_silver,
        "constraint": {
            "allow_multiple_per_tier": True,
            "allow_multiple_per_session": True,
            "unique_achievement": False,
        },
    }
    
    return achievements


def _generate_master_of_times_tables_achievements() -> dict[str, dict[str, Any]]:
    """Generate Master of Times Tables achievement definitions.
    
    Milestone achievement, bronze awarded if all "Multiplication by n" tests have
    Level Master Bronze and Lightning Fast. Higher tier can be substituted.
    """
    achievements = {}
    
    tier_requirements = {
        "bronze": {"required_tier": "bronze"},
        "silver": {"required_tier": "silver"},
        "gold": {"required_tier": "gold"},
        "platinum": {"required_tier": "platinum"},
        "diamond": {"required_tier": "diamond"},
        "master": {"required_tier": "master"},
        "grandmaster": {"required_tier": "grandmaster"},
        "legendary": {"required_tier": "legendary"},
        "mythic": {"required_tier": "mythic"},
        "divine": {"required_tier": "divine"},
        "champion": {"required_tier": "divine"},  # Same as divine, requires server record
    }
    
    for tier in ALL_TIERS:
        code = f"master-of-times-tables-{tier}"
        req = tier_requirements.get(tier, {})
        required_tier = req.get("required_tier", "bronze")
        
        tier_title = tier.capitalize()
        title = f"Master of Times Tables ({tier_title})"
        
        if tier == "champion":
            description = f"Level Master ({required_tier.capitalize()}) and Lightning Fast ({required_tier.capitalize()}) on all multiplication tables (server record)"
        else:
            description = f"Level Master ({required_tier.capitalize()}) and Lightning Fast ({required_tier.capitalize()}) on all multiplication tables"
        
        requirements = {
            "type": "master_of_times_tables",
            "required_tier": required_tier,
        }
        
        if tier == "champion":
            requirements["requires_champion_check"] = True
        
        achievements[code] = {
            "title": title,
            "description": description,
            "icon": "✖️",
            "category": "milestone",
            "tier": tier,
            "requirements": requirements,
            "constraint": {
                "allow_multiple_per_tier": True,
                "allow_multiple_per_session": True,
                "unique_achievement": False,
            },
        }
    
    return achievements


def _generate_master_of_division_tables_achievements() -> dict[str, dict[str, Any]]:
    """Generate Master of Division Tables achievement definitions.
    
    Same as Master of Times Tables, but for division tables.
    """
    achievements = {}
    
    tier_requirements = {
        "bronze": {"required_tier": "bronze"},
        "silver": {"required_tier": "silver"},
        "gold": {"required_tier": "gold"},
        "platinum": {"required_tier": "platinum"},
        "diamond": {"required_tier": "diamond"},
        "master": {"required_tier": "master"},
        "grandmaster": {"required_tier": "grandmaster"},
        "legendary": {"required_tier": "legendary"},
        "mythic": {"required_tier": "mythic"},
        "divine": {"required_tier": "divine"},
        "champion": {"required_tier": "divine"},  # Same as divine, requires server record
    }
    
    for tier in ALL_TIERS:
        code = f"master-of-division-tables-{tier}"
        req = tier_requirements.get(tier, {})
        required_tier = req.get("required_tier", "bronze")
        
        tier_title = tier.capitalize()
        title = f"Master of Division Tables ({tier_title})"
        
        if tier == "champion":
            description = f"Level Master ({required_tier.capitalize()}) and Lightning Fast ({required_tier.capitalize()}) on all division tables (server record)"
        else:
            description = f"Level Master ({required_tier.capitalize()}) and Lightning Fast ({required_tier.capitalize()}) on all division tables"
        
        requirements = {
            "type": "master_of_division_tables",
            "required_tier": required_tier,
        }
        
        if tier == "champion":
            requirements["requires_champion_check"] = True
        
        achievements[code] = {
            "title": title,
            "description": description,
            "icon": "➗",
            "category": "milestone",
            "tier": tier,
            "requirements": requirements,
            "constraint": {
                "allow_multiple_per_tier": True,
                "allow_multiple_per_session": True,
                "unique_achievement": False,
            },
        }
    
    return achievements


def _generate_master_of_basic_addition_achievements() -> dict[str, dict[str, Any]]:
    """Generate Master of Basic Addition achievement definitions.

    Milestone achievement awarded when the user has Level Master at all basic addition concepts.
    This is concept-based (e.g. c_add_0s..c_add_10s) and is intended to power concept unlock requirements.
    """
    achievements: dict[str, dict[str, Any]] = {}

    # Mirrors the 11-tier pattern used by other milestone achievements.
    tier_requirements = {
        "bronze": {"required_tier": "bronze"},
        "silver": {"required_tier": "silver"},
        "gold": {"required_tier": "gold"},
        "platinum": {"required_tier": "platinum"},
        "diamond": {"required_tier": "diamond"},
        "master": {"required_tier": "master"},
        "grandmaster": {"required_tier": "grandmaster"},
        "legendary": {"required_tier": "legendary"},
        "mythic": {"required_tier": "mythic"},
        "divine": {"required_tier": "divine"},
        "champion": {"required_tier": "divine"},  # Same as divine, requires server record
    }

    for tier in ALL_TIERS:
        code = f"master-of-basic-addition-{tier}"
        req = tier_requirements.get(tier, {})
        required_tier = req.get("required_tier", "bronze")

        tier_title = tier.capitalize()
        title = f"Master of Basic Addition ({tier_title})"

        if tier == "champion":
            description = f"Level Master ({required_tier.capitalize()}) on all basic addition concepts (server record)"
        else:
            description = f"Level Master ({required_tier.capitalize()}) on all basic addition concepts"

        requirements: dict[str, Any] = {
            "type": "master_of_basic_addition",
            "required_tier": required_tier,
        }
        if tier == "champion":
            requirements["requires_champion_check"] = True

        achievements[code] = {
            "title": title,
            "description": description,
            "icon": "➕",
            "category": "milestone",
            "tier": tier,
            "requirements": requirements,
            "constraint": {
                "allow_multiple_per_tier": True,
                "allow_multiple_per_session": True,
                "unique_achievement": False,
            },
        }

    return achievements


def _generate_master_of_basic_subtraction_achievements() -> dict[str, dict[str, Any]]:
    """Generate Master of Basic Subtraction achievement definitions.

    Milestone achievement awarded when the user has Level Master at all basic subtraction concepts.
    This is concept-based (e.g. c_sub_0s..c_sub_10s) and is intended to power concept unlock requirements.
    """
    achievements: dict[str, dict[str, Any]] = {}

    tier_requirements = {
        "bronze": {"required_tier": "bronze"},
        "silver": {"required_tier": "silver"},
        "gold": {"required_tier": "gold"},
        "platinum": {"required_tier": "platinum"},
        "diamond": {"required_tier": "diamond"},
        "master": {"required_tier": "master"},
        "grandmaster": {"required_tier": "grandmaster"},
        "legendary": {"required_tier": "legendary"},
        "mythic": {"required_tier": "mythic"},
        "divine": {"required_tier": "divine"},
        "champion": {"required_tier": "divine"},  # Same as divine, requires server record
    }

    for tier in ALL_TIERS:
        code = f"master-of-basic-subtraction-{tier}"
        req = tier_requirements.get(tier, {})
        required_tier = req.get("required_tier", "bronze")

        tier_title = tier.capitalize()
        title = f"Master of Basic Subtraction ({tier_title})"

        if tier == "champion":
            description = f"Level Master ({required_tier.capitalize()}) on all basic subtraction concepts (server record)"
        else:
            description = f"Level Master ({required_tier.capitalize()}) on all basic subtraction concepts"

        requirements: dict[str, Any] = {
            "type": "master_of_basic_subtraction",
            "required_tier": required_tier,
        }
        if tier == "champion":
            requirements["requires_champion_check"] = True

        achievements[code] = {
            "title": title,
            "description": description,
            "icon": "➖",
            "category": "milestone",
            "tier": tier,
            "requirements": requirements,
            "constraint": {
                "allow_multiple_per_tier": True,
                "allow_multiple_per_session": True,
                "unique_achievement": False,
            },
        }

    return achievements


# Generate all milestone achievements
MILESTONE_ACHIEVEMENTS.update(_generate_week_warrior_achievements())
MILESTONE_ACHIEVEMENTS.update(_generate_question_master_achievements())
MILESTONE_ACHIEVEMENTS.update(_generate_speed_demon_achievements())
MILESTONE_ACHIEVEMENTS.update(_generate_perfect_streak_achievements())
MILESTONE_ACHIEVEMENTS.update(_generate_math_grandmaster_achievements())
MILESTONE_ACHIEVEMENTS.update(_generate_so_wow_achievements())
MILESTONE_ACHIEVEMENTS.update(_generate_human_calculator_achievements())
MILESTONE_ACHIEVEMENTS.update(_generate_master_of_times_tables_achievements())
MILESTONE_ACHIEVEMENTS.update(_generate_master_of_division_tables_achievements())
MILESTONE_ACHIEVEMENTS.update(_generate_master_of_basic_addition_achievements())
MILESTONE_ACHIEVEMENTS.update(_generate_master_of_basic_subtraction_achievements())

