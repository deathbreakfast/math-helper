"""Level mastery achievements for levels 11-15."""

from typing import Any

# Level Mastery Achievements (Level 11-15)
LEVELS_11_15_MASTERY: dict[str, dict[str, Any]] = {
    "level-11-mastery": {
        "title": "Level 11 Mastery",
        "description": "Complete Level 11 test with 95%+ accuracy (25 questions) AND answer 80 level 11 questions correct in a row",
        "icon": "⭐",
        "category": "progression",
        "requirements": {
            "type": "level_mastery",
            "level": 11,
            "min_accuracy": 0.95,
            "min_questions": 25,
            "consecutive_correct": 80
        }
    },
    "level-12-mastery": {
        "title": "Level 12 Mastery",
        "description": "Complete Level 12 test with 95%+ accuracy (25 questions) AND answer 80 level 12 questions correct in a row",
        "icon": "⭐",
        "category": "progression",
        "requirements": {
            "type": "level_mastery",
            "level": 12,
            "min_accuracy": 0.95,
            "min_questions": 25,
            "consecutive_correct": 80
        }
    },
    "level-13-mastery": {
        "title": "Level 13 Mastery",
        "description": "Complete Level 13 test with 95%+ accuracy (25 questions) AND answer 80 level 13 questions correct in a row",
        "icon": "⭐",
        "category": "progression",
        "requirements": {
            "type": "level_mastery",
            "level": 13,
            "min_accuracy": 0.95,
            "min_questions": 25,
            "consecutive_correct": 80
        }
    },
    "level-14-mastery": {
        "title": "Level 14 Mastery",
        "description": "Complete Level 14 test with 95%+ accuracy (25 questions) AND answer 80 level 14 questions correct in a row",
        "icon": "⭐",
        "category": "progression",
        "requirements": {
            "type": "level_mastery",
            "level": 14,
            "min_accuracy": 0.95,
            "min_questions": 25,
            "consecutive_correct": 80
        }
    },
    "level-15-mastery": {
        "title": "Level 15 Mastery",
        "description": "Complete Level 15 test with 95%+ accuracy (25 questions) AND answer 80 level 15 questions correct in a row",
        "icon": "⭐",
        "category": "progression",
        "requirements": {
            "type": "level_mastery",
            "level": 15,
            "min_accuracy": 0.95,
            "min_questions": 25,
            "consecutive_correct": 80
        }
    },
}

