"""Level mastery achievements for levels 21-25."""

from typing import Any

# Level Mastery Achievements (Level 21-25)
LEVELS_21_25_MASTERY: dict[str, dict[str, Any]] = {
    "level-21-mastery": {
        "title": "Level 21 Mastery",
        "description": "Complete Level 21 test with 95%+ accuracy (25 questions) AND answer 80 level 21 questions correct in a row",
        "icon": "⭐",
        "category": "progression",
        "requirements": {
            "type": "level_mastery",
            "level": 21,
            "min_accuracy": 0.95,
            "min_questions": 25,
            "consecutive_correct": 80
        }
    },
    "level-22-mastery": {
        "title": "Level 22 Mastery",
        "description": "Complete Level 22 with 95%+ accuracy (minimum 40 questions) AND answer 50 level 22 questions correct in a row",
        "icon": "⭐",
        "category": "progression",
        "requirements": {
            "type": "level_mastery",
            "level": 22,
            "min_accuracy": 0.95,
            "min_questions": 40,
            "consecutive_correct": 50
        }
    },
    "level-23-mastery": {
        "title": "Level 23 Mastery",
        "description": "Complete Level 23 with 95%+ accuracy (minimum 40 questions) AND answer 50 level 23 questions correct in a row",
        "icon": "⭐",
        "category": "progression",
        "requirements": {
            "type": "level_mastery",
            "level": 23,
            "min_accuracy": 0.95,
            "min_questions": 40,
            "consecutive_correct": 50
        }
    },
    "level-24-mastery": {
        "title": "Level 24 Mastery",
        "description": "Complete Level 24 with 95%+ accuracy (minimum 40 questions) AND answer 50 level 24 questions correct in a row",
        "icon": "⭐",
        "category": "progression",
        "requirements": {
            "type": "level_mastery",
            "level": 24,
            "min_accuracy": 0.95,
            "min_questions": 40,
            "consecutive_correct": 50
        }
    },
    "level-25-mastery": {
        "title": "Level 25 Mastery",
        "description": "Complete Level 25 with 95%+ accuracy (minimum 40 questions) AND answer 100 level 25 questions correct in a row",
        "icon": "⭐",
        "category": "progression",
        "requirements": {
            "type": "level_mastery",
            "level": 25,
            "min_accuracy": 0.95,
            "min_questions": 40,
            "consecutive_correct": 100
        }
    },
}

