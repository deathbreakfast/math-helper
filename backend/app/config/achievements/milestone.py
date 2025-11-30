"""Milestone achievement definitions."""

from typing import Any

# Milestone achievements
MILESTONE_ACHIEVEMENTS: dict[str, dict[str, Any]] = {
    "first-steps": {
        "title": "First Steps",
        "description": "Complete 10 addition problems",
        "icon": "👣",
        "category": "milestone",
        "requirements": {
            "type": "operation_count",
            "operation": "addition",
            "count": 10,
            "level": 1
        }
    },
    "first-victory": {
        "title": "First Victory",
        "description": "Answer your first question",
        "icon": "🎯",
        "category": "milestone",
        "requirements": {
            "type": "question_count",
            "min_questions": 1
        }
    },
    "century": {
        "title": "Century Club",
        "description": "Answered 100+ questions",
        "icon": "💯",
        "category": "milestone",
        "requirements": {
            "type": "question_count",
            "min_questions": 100
        }
    },
}

