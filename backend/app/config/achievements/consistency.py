"""Consistency/streak achievement definitions."""

from typing import Any

# Consistency/Streak achievements
CONSISTENCY_ACHIEVEMENTS: dict[str, dict[str, Any]] = {
    "streak-2": {
        "title": "First Steps",
        "description": "Complete a 2-day streak",
        "icon": "🔥",
        "category": "consistency",
        "requirements": {
            "type": "streak",
            "min_streak_days": 2
        }
    },
    "streak-3": {
        "title": "Getting Consistent",
        "description": "Complete a 3-day streak",
        "icon": "🔥",
        "category": "consistency",
        "requirements": {
            "type": "streak",
            "min_streak_days": 3
        }
    },
    "streak-5": {
        "title": "Practice Makes Perfect",
        "description": "Complete a 5-day streak",
        "icon": "🔥",
        "category": "consistency",
        "requirements": {
            "type": "streak",
            "min_streak_days": 5
        }
    },
    "streak-10": {
        "title": "Dedicated Learner",
        "description": "Complete a 10-day streak",
        "icon": "🔥",
        "category": "consistency",
        "requirements": {
            "type": "streak",
            "min_streak_days": 10
        }
    },
    "perfect-week": {
        "title": "Perfect Week",
        "description": "Practiced every day this week",
        "icon": "🌟",
        "category": "consistency",
        "requirements": {
            "type": "streak",
            "min_streak_days": 7
        }
    },
    # Perfect Sessions Chain Achievements
    "perfect-sessions-2": {
        "title": "Perfect Sessions (Bronze)",
        "description": "Complete 2 sessions in a row with 100% accuracy",
        "icon": "🔥",
        "category": "consistency",
        "requirements": {
            "type": "perfect_sessions",
            "min_sessions": 2
        }
    },
    "perfect-sessions-4": {
        "title": "Perfect Sessions (Silver)",
        "description": "Complete 4 sessions in a row with 100% accuracy",
        "icon": "🔥",
        "category": "consistency",
        "requirements": {
            "type": "perfect_sessions",
            "min_sessions": 4
        }
    },
    "perfect-sessions-8": {
        "title": "Perfect Sessions (Gold)",
        "description": "Complete 8 sessions in a row with 100% accuracy",
        "icon": "🔥",
        "category": "consistency",
        "requirements": {
            "type": "perfect_sessions",
            "min_sessions": 8
        }
    },
    "perfect-sessions-16": {
        "title": "Perfect Sessions (Diamond)",
        "description": "Complete 16 sessions in a row with 100% accuracy",
        "icon": "🔥",
        "category": "consistency",
        "requirements": {
            "type": "perfect_sessions",
            "min_sessions": 16
        }
    },
}

