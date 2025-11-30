"""Test requirements for subtraction levels."""

from typing import Any

# Test requirements for subtraction levels (3, 4, 6, 8, 23)
SUBTRACTION_TEST_REQUIREMENTS: dict[int, dict[str, Any]] = {
    3: {
        "sessions_required": 3,
        "question_count": 25,
        "passing_score": 0.80,
        "missed_questions_threshold": 3,
        "missed_questions_window_days": 7,
        "test_type": "level_3",
    },
    4: {
        "sessions_required": 3,
        "question_count": 25,
        "passing_score": 0.80,
        "missed_questions_threshold": 3,
        "missed_questions_window_days": 7,
        "test_type": "level_4",
    },
    6: {
        "sessions_required": 3,
        "question_count": 25,
        "passing_score": 0.80,
        "missed_questions_threshold": 3,
        "missed_questions_window_days": 7,
        "test_type": "level_6",
    },
    8: {
        "sessions_required": 3,
        "question_count": 25,
        "passing_score": 0.80,
        "missed_questions_threshold": 3,
        "missed_questions_window_days": 7,
        "test_type": "level_8",
    },
    23: {
        "sessions_required": 3,
        "question_count": 30,
        "passing_score": 0.80,
        "missed_questions_threshold": 3,
        "missed_questions_window_days": 7,
        "test_type": "level_23",
    },
}

