"""Progression achievement definitions."""

from typing import Any

# Progression achievements
PROGRESSION_ACHIEVEMENTS: dict[str, dict[str, Any]] = {
    "level-2-mastery": {
        "title": "Level 2 Mastery",
        "description": "Complete 4 sessions with 90%+ accuracy and answer 10 level 2 questions correct in a row",
        "icon": "⭐",
        "category": "progression",
        "requirements": {
            "type": "session_accuracy_and_consecutive",
            "min_sessions": 4,
            "min_session_accuracy": 0.90,
            "level": 2,
            "consecutive_correct": 10
        }
    },
    "mixed-addition": {
        "title": "Mixed Addition",
        "description": "Complete Level 2 with 20 correct answers",
        "icon": "➕",
        "category": "progression",
        "requirements": {
            "type": "level_correct_count",
            "level": 2,
            "min_correct": 20
        }
    },
    "mixed-subtraction": {
        "title": "Mixed Subtraction",
        "description": "Complete Level 4 with 20 correct answers",
        "icon": "➖",
        "category": "progression",
        "requirements": {
            "type": "level_correct_count",
            "level": 4,
            "min_correct": 20
        }
    },
    "multiply-by-one": {
        "title": "Multiply by One",
        "description": "Complete Level 7 with 30 correct answers",
        "icon": "✖️",
        "category": "progression",
        "requirements": {
            "type": "level_correct_count",
            "level": 7,
            "min_correct": 30
        }
    },
    "triple-addition": {
        "title": "Triple Addition",
        "description": "Complete Level 8 with 50 correct answers",
        "icon": "➕",
        "category": "progression",
        "requirements": {
            "type": "level_correct_count",
            "level": 8,
            "min_correct": 50
        }
    },
    "multiplication-work": {
        "title": "Multiplication Work",
        "description": "Complete Level 24 with 30 correct answers",
        "icon": "✖️",
        "category": "progression",
        "requirements": {
            "type": "level_correct_count",
            "level": 24,
            "min_correct": 30
        }
    },
    "division-remainder": {
        "title": "Division Remainder",
        "description": "Complete Level 37 with 30 correct answers",
        "icon": "➗",
        "category": "progression",
        "requirements": {
            "type": "level_correct_count",
            "level": 37,
            "min_correct": 30
        }
    },
    "division-fraction": {
        "title": "Division Fraction",
        "description": "Complete Level 38 with 20 correct answers",
        "icon": "➗",
        "category": "progression",
        "requirements": {
            "type": "level_correct_count",
            "level": 38,
            "min_correct": 20
        }
    },
    "multiplication-triple": {
        "title": "Multiplication Triple",
        "description": "Complete Level 25 with 50 correct answers",
        "icon": "✖️",
        "category": "progression",
        "requirements": {
            "type": "level_correct_count",
            "level": 25,
            "min_correct": 50
        }
    },
    "division-decimal": {
        "title": "Division Decimal",
        "description": "Complete Level 40 with 20 correct answers",
        "icon": "➗",
        "category": "progression",
        "requirements": {
            "type": "level_correct_count",
            "level": 40,
            "min_correct": 20
        }
    },
    "addition-mastery": {
        "title": "Addition Mastery",
        "description": "Earn 50 platinum or higher level achievements on basic addition (1-digit)",
        "icon": "💎",
        "category": "progression",
        "requirements": {
            "type": "achievement_count_by_category",
            "category": "addition",
            "min_level": 1,
            "max_level": 1,
            "min_tier": "platinum",
            "min_count": 50
        }
    },
    "subtraction-mastery": {
        "title": "Subtraction Mastery",
        "description": "Earn 50 platinum or higher level achievements on basic subtraction (1-digit)",
        "icon": "💎",
        "category": "progression",
        "requirements": {
            "type": "achievement_count_by_category",
            "category": "subtraction",
            "min_level": 1,
            "max_level": 1,
            "min_tier": "platinum",
            "min_count": 50
        }
    },
    "addition-subtraction-advanced-mastery": {
        "title": "Advanced Addition & Subtraction Mastery",
        "description": "Earn 100 gold or higher level achievements on addition and subtraction (outside of basic 1-digit)",
        "icon": "💎",
        "category": "progression",
        "requirements": {
            "type": "achievement_count_by_category",
            "category": "addition_subtraction",
            "min_level": 2,
            "min_tier": "gold",
            "min_count": 100
        }
    },
}

