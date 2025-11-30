"""Level mastery achievements for levels 5-10."""

from typing import Any

# Level Mastery Achievements (Level 5-10)
LEVELS_5_10_MASTERY: dict[str, dict[str, Any]] = {
    "level-5-mastery": {
        "title": "Level 5 Mastery",
        "description": "Complete Level 5 with 90%+ accuracy (minimum 15 questions) AND answer 50 level 5 questions correct in a row",
        "icon": "⭐",
        "category": "progression",
        "requirements": {
            "type": "level_mastery",
            "level": 5,
            "min_accuracy": 0.90,
            "min_questions": 15,
            "consecutive_correct": 50
        }
    },
    "level-6-mastery": {
        "title": "Level 6 Mastery",
        "description": "Complete Level 6 with 90%+ accuracy (minimum 20 questions) AND answer 50 level 6 questions correct in a row",
        "icon": "⭐",
        "category": "progression",
        "requirements": {
            "type": "level_mastery",
            "level": 6,
            "min_accuracy": 0.90,
            "min_questions": 20,
            "consecutive_correct": 50
        }
    },
    "level-7-mastery": {
        "title": "Level 7 Mastery",
        "description": "Complete Level 7 with 90%+ accuracy (minimum 25 questions) AND answer 50 level 7 questions correct in a row",
        "icon": "⭐",
        "category": "progression",
        "requirements": {
            "type": "level_mastery",
            "level": 7,
            "min_accuracy": 0.90,
            "min_questions": 25,
            "consecutive_correct": 50
        }
    },
    "level-8-mastery": {
        "title": "Level 8 Mastery",
        "description": "Complete Level 8 with 95%+ accuracy (minimum 30 questions) AND answer 80 level 8 questions correct in a row",
        "icon": "⭐",
        "category": "progression",
        "requirements": {
            "type": "level_mastery",
            "level": 8,
            "min_accuracy": 0.95,
            "min_questions": 30,
            "consecutive_correct": 80
        }
    },
    "level-9-mastery": {
        "title": "Level 9 Mastery",
        "description": "Complete Level 9 with 95%+ accuracy (minimum 35 questions) AND answer 80 level 9 questions correct in a row",
        "icon": "⭐",
        "category": "progression",
        "requirements": {
            "type": "level_mastery",
            "level": 9,
            "min_accuracy": 0.95,
            "min_questions": 35,
            "consecutive_correct": 80
        }
    },
    "level-10-mastery": {
        "title": "Level 10 Mastery",
        "description": "Complete Level 10 test with 95%+ accuracy (25 questions) AND answer 80 level 10 questions correct in a row",
        "icon": "⭐",
        "category": "progression",
        "requirements": {
            "type": "level_mastery",
            "level": 10,
            "min_accuracy": 0.95,
            "min_questions": 25,
            "consecutive_correct": 80
        }
    },
}

