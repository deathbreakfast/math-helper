"""Speed achievement definitions."""

from typing import Any

# Speed achievements
SPEED_ACHIEVEMENTS: dict[str, dict[str, Any]] = {
    "speed-demon": {
        "title": "Speed Demon",
        "description": "Average response time under 3 seconds",
        "icon": "⚡",
        "category": "speed",
        "requirements": {
            "type": "speed",
            "max_speed_seconds": 3.0,
            "min_questions": 10
        }
    },
    # Speed Achievements - Fast Sessions
    "fast-session-bronze": {
        "title": "Fast Session (Bronze)",
        "description": "Complete a session with average time under 5 seconds per question",
        "icon": "⚡",
        "category": "speed",
        "requirements": {
            "type": "fast_session",
            "max_avg_time": 5.0,
            "min_questions": 10
        }
    },
    "fast-session-silver": {
        "title": "Fast Session (Silver)",
        "description": "Complete a session with average time under 4 seconds per question",
        "icon": "⚡",
        "category": "speed",
        "requirements": {
            "type": "fast_session",
            "max_avg_time": 4.0,
            "min_questions": 10
        }
    },
    "fast-session-gold": {
        "title": "Fast Session (Gold)",
        "description": "Complete a session with average time under 3 seconds per question",
        "icon": "⚡",
        "category": "speed",
        "requirements": {
            "type": "fast_session",
            "max_avg_time": 3.0,
            "min_questions": 10
        }
    },
    "fast-session-platinum": {
        "title": "Fast Session (Platinum)",
        "description": "Complete a session with average time under 2.5 seconds per question",
        "icon": "⚡",
        "category": "speed",
        "requirements": {
            "type": "fast_session",
            "max_avg_time": 2.5,
            "min_questions": 10
        }
    },
    "fast-session-diamond": {
        "title": "Fast Session (Diamond)",
        "description": "Complete a session with average time under 2 seconds per question",
        "icon": "⚡",
        "category": "speed",
        "requirements": {
            "type": "fast_session",
            "max_avg_time": 2.0,
            "min_questions": 10
        }
    },
    "fast-session-champion": {
        "title": "Fast Session (Champion)",
        "description": "Complete a session with average time under 1.5 seconds per question",
        "icon": "⚡",
        "category": "speed",
        "requirements": {
            "type": "fast_session",
            "max_avg_time": 1.5,
            "min_questions": 10
        }
    },
    # Speed Achievements - Fast Question Answering
    "fast-question-bronze": {
        "title": "Fast Answer (Bronze)",
        "description": "Answer 10 questions in a row with average time under 4 seconds",
        "icon": "🚀",
        "category": "speed",
        "requirements": {
            "type": "fast_questions",
            "max_avg_time": 4.0,
            "consecutive_count": 10
        }
    },
    "fast-question-silver": {
        "title": "Fast Answer (Silver)",
        "description": "Answer 15 questions in a row with average time under 3.5 seconds",
        "icon": "🚀",
        "category": "speed",
        "requirements": {
            "type": "fast_questions",
            "max_avg_time": 3.5,
            "consecutive_count": 15
        }
    },
    "fast-question-gold": {
        "title": "Fast Answer (Gold)",
        "description": "Answer 20 questions in a row with average time under 3 seconds",
        "icon": "🚀",
        "category": "speed",
        "requirements": {
            "type": "fast_questions",
            "max_avg_time": 3.0,
            "consecutive_count": 20
        }
    },
    "fast-question-platinum": {
        "title": "Fast Answer (Platinum)",
        "description": "Answer 25 questions in a row with average time under 2.5 seconds",
        "icon": "🚀",
        "category": "speed",
        "requirements": {
            "type": "fast_questions",
            "max_avg_time": 2.5,
            "consecutive_count": 25
        }
    },
    "fast-question-diamond": {
        "title": "Fast Answer (Diamond)",
        "description": "Answer 30 questions in a row with average time under 2 seconds",
        "icon": "🚀",
        "category": "speed",
        "requirements": {
            "type": "fast_questions",
            "max_avg_time": 2.0,
            "consecutive_count": 30
        }
    },
    "fast-question-champion": {
        "title": "Fast Answer (Champion)",
        "description": "Answer 50 questions in a row with average time under 1.5 seconds",
        "icon": "🚀",
        "category": "speed",
        "requirements": {
            "type": "fast_questions",
            "max_avg_time": 1.5,
            "consecutive_count": 50
        }
    },
}

