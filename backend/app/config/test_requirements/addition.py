"""Test requirements for addition levels."""

from typing import Any

# Test requirements for addition levels (1, 2, 5, 7, 22)
ADDITION_TEST_REQUIREMENTS: dict[int, dict[str, Any]] = {
    1: {
        "sessions_required": 3,
        "question_count": 25,
        "passing_score": 0.80,
        "missed_questions_threshold": 3,
        "missed_questions_window_days": 7,
        "test_type": "level_1",
    },
    2: {
        "sessions_required": 3,
        "question_count": 25,
        "passing_score": 0.80,
        "missed_questions_threshold": 3,
        "missed_questions_window_days": 7,
        "test_type": "level_2",
    },
    5: {
        "sessions_required": 3,
        "question_count": 25,
        "passing_score": 0.80,
        "missed_questions_threshold": 3,
        "missed_questions_window_days": 7,
        "test_type": "level_5",
    },
    7: {
        "sessions_required": 3,
        "question_count": 25,
        "passing_score": 0.80,
        "missed_questions_threshold": 3,
        "missed_questions_window_days": 7,
        "test_type": "level_7",
    },
    22: {
        "sessions_required": 3,
        "question_count": 30,
        "passing_score": 0.80,
        "missed_questions_threshold": 3,
        "missed_questions_window_days": 7,
        "test_type": "level_22",
    },
}

