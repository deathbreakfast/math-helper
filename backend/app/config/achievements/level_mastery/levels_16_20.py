"""Level mastery achievements for levels 16-20."""

from typing import Any

# Level Mastery Achievements (Level 16-20)
LEVELS_16_20_MASTERY: dict[str, dict[str, Any]] = {
    "level-16-mastery": {
        "title": "Level 16 Mastery",
        "description": "Complete Level 16 test with 95%+ accuracy (25 questions) AND answer 80 level 16 questions correct in a row",
        "icon": "⭐",
        "category": "progression",
        "requirements": {
            "type": "level_mastery",
            "level": 16,
            "min_accuracy": 0.95,
            "min_questions": 25,
            "consecutive_correct": 80
        }
    },
    "level-17-mastery": {
        "title": "Level 17 Mastery",
        "description": "Complete Level 17 test with 95%+ accuracy (25 questions) AND answer 80 level 17 questions correct in a row",
        "icon": "⭐",
        "category": "progression",
        "requirements": {
            "type": "level_mastery",
            "level": 17,
            "min_accuracy": 0.95,
            "min_questions": 25,
            "consecutive_correct": 80
        }
    },
    "level-18-mastery": {
        "title": "Level 18 Mastery",
        "description": "Complete Level 18 test with 95%+ accuracy (25 questions) AND answer 80 level 18 questions correct in a row",
        "icon": "⭐",
        "category": "progression",
        "requirements": {
            "type": "level_mastery",
            "level": 18,
            "min_accuracy": 0.95,
            "min_questions": 25,
            "consecutive_correct": 80
        }
    },
    "level-19-mastery": {
        "title": "Level 19 Mastery",
        "description": "Complete Level 19 test with 95%+ accuracy (25 questions) AND answer 80 level 19 questions correct in a row",
        "icon": "⭐",
        "category": "progression",
        "requirements": {
            "type": "level_mastery",
            "level": 19,
            "min_accuracy": 0.95,
            "min_questions": 25,
            "consecutive_correct": 80
        }
    },
    "level-20-mastery": {
        "title": "Level 20 Mastery",
        "description": "Complete Level 20 test with 95%+ accuracy (25 questions) AND answer 80 level 20 questions correct in a row",
        "icon": "⭐",
        "category": "progression",
        "requirements": {
            "type": "level_mastery",
            "level": 20,
            "min_accuracy": 0.95,
            "min_questions": 25,
            "consecutive_correct": 80
        }
    },
}

