"""Accuracy achievement definitions."""

from typing import Any

# Accuracy achievements
ACCURACY_ACHIEVEMENTS: dict[str, dict[str, Any]] = {
    "addition-basics": {
        "title": "Addition Basics",
        "description": "Complete Level 1 with 80%+ accuracy",
        "icon": "⭐",
        "category": "accuracy",
        "requirements": {
            "type": "level_accuracy",
            "level": 1,
            "min_accuracy": 0.80,
            "min_questions": 10
        }
    },
    "subtraction-basics": {
        "title": "Subtraction Basics",
        "description": "Complete Level 3 with 80%+ accuracy",
        "icon": "⭐",
        "category": "accuracy",
        "requirements": {
            "type": "level_accuracy",
            "level": 3,
            "min_accuracy": 0.80,
            "min_questions": 10
        }
    },
    "double-addition": {
        "title": "Double Addition",
        "description": "Complete Level 5 with 80%+ accuracy",
        "icon": "➕",
        "category": "accuracy",
        "requirements": {
            "type": "level_accuracy",
            "level": 5,
            "min_accuracy": 0.80,
            "min_questions": 10
        }
    },
    "double-subtraction": {
        "title": "Double Subtraction",
        "description": "Complete Level 6 with 80%+ accuracy",
        "icon": "➖",
        "category": "accuracy",
        "requirements": {
            "type": "level_accuracy",
            "level": 6,
            "min_accuracy": 0.80,
            "min_questions": 10
        }
    },
    "triple-subtraction": {
        "title": "Triple Subtraction",
        "description": "Complete Level 22 with 80%+ accuracy",
        "icon": "➖",
        "category": "accuracy",
        "requirements": {
            "type": "level_accuracy",
            "level": 22,
            "min_accuracy": 0.80,
            "min_questions": 10
        }
    },
    "divide-by-one": {
        "title": "Divide by One",
        "description": "Complete Level 25 with 80%+ accuracy",
        "icon": "➗",
        "category": "accuracy",
        "requirements": {
            "type": "level_accuracy",
            "level": 25,
            "min_accuracy": 0.80,
            "min_questions": 10
        }
    },
    "division-double-remainder": {
        "title": "Division Double Remainder",
        "description": "Complete Level 38 with 80%+ accuracy",
        "icon": "➗",
        "category": "accuracy",
        "requirements": {
            "type": "level_accuracy",
            "level": 38,
            "min_accuracy": 0.80,
            "min_questions": 10
        }
    },
    "division-double-fraction": {
        "title": "Division Double Fraction",
        "description": "Complete Level 40 with 80%+ accuracy",
        "icon": "➗",
        "category": "accuracy",
        "requirements": {
            "type": "level_accuracy",
            "level": 40,
            "min_accuracy": 0.80,
            "min_questions": 10
        }
    },
    "division-triple-fraction": {
        "title": "Division Triple Fraction",
        "description": "Complete Level 41 with 80%+ accuracy",
        "icon": "➗",
        "category": "accuracy",
        "requirements": {
            "type": "level_accuracy",
            "level": 41,
            "min_accuracy": 0.80,
            "min_questions": 10
        }
    },
    "division-double-decimal": {
        "title": "Division Double Decimal",
        "description": "Complete Level 44 with 80%+ accuracy",
        "icon": "➗",
        "category": "accuracy",
        "requirements": {
            "type": "level_accuracy",
            "level": 44,
            "min_accuracy": 0.80,
            "min_questions": 10
        }
    },
    "accuracy-ace": {
        "title": "Accuracy Ace",
        "description": "Maintained 95%+ accuracy in at least one operation",
        "icon": "🎯",
        "category": "accuracy",
        "requirements": {
            "type": "operation_accuracy",
            "min_accuracy": 0.95,
            "min_questions": 20
        }
    },
}

