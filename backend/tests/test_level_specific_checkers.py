"""Tests for level-specific achievement checkers.

Tests verify that perfect_streak checker works correctly in isolation.
"""

import pytest
from datetime import datetime

from app import create_app, db
from app.models import Achievement, PracticeSession, Question, Response, User
from app.services.achievements.achievement_checkers.perfect_streak_checker import PerfectStreakChecker
from app.services.level_config_service import LevelConfigService
from tests.helpers.data_helpers import (
    create_test_questions,
    create_test_session_with_responses,
)


@pytest.fixture
def app():
    """Create test Flask application."""
    app = create_app(test_config={'TESTING': True})
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def test_user(app):
    """Create a test user."""
    with app.app_context():
        user = User(display_name="TestUser", pin="1234", avatar="🐯", level=1)
        db.session.add(user)
        db.session.commit()
        _ = user.id
        return user


@pytest.fixture
def achievement_configs():
    """Get achievement configs."""
    return LevelConfigService.get_all_achievement_configs()


class TestPerfectStreakChecker:
    """Test PerfectStreakChecker."""
    
    def test_perfect_streak_checker_awards_bronze(self, app, test_user, achievement_configs):
        """Test that PerfectStreakChecker awards bronze for 3 perfect sessions."""
        with app.app_context():
            # Create 3 consecutive perfect sessions
            for _ in range(3):
                questions = create_test_questions(10, 1)
                responses_data = [{
                    'question_id': q.id,
                    'answer': q.correct_answer,
                    'is_correct': True,
                    'duration_ms': 3000
                } for q in questions]
                
                session = create_test_session_with_responses(test_user.id, responses_data)
            
            checker = PerfectStreakChecker(achievement_configs)
            achievements = checker.check(test_user)
            
            # Should award perfect-streak-bronze
            codes = [a.code for a in achievements]
            assert any("perfect-streak" in code for code in codes)
    
    def test_perfect_streak_checker_no_award_for_imperfect_session(self, app, test_user, achievement_configs):
        """Test that PerfectStreakChecker doesn't award when streak is broken."""
        with app.app_context():
            # Create 2 perfect sessions
            for _ in range(2):
                questions = create_test_questions(10, 1)
                responses_data = [{
                    'question_id': q.id,
                    'answer': q.correct_answer,
                    'is_correct': True,
                    'duration_ms': 3000
                } for q in questions]
                
                session = create_test_session_with_responses(test_user.id, responses_data)
            
            # Create one imperfect session
            questions = create_test_questions(10, 1)
            responses_data = []
            for i, q in enumerate(questions):
                responses_data.append({
                    'question_id': q.id,
                    'answer': q.correct_answer if i < 9 else '999',
                    'is_correct': i < 9,
                    'duration_ms': 3000
                })
            
            session = create_test_session_with_responses(test_user.id, responses_data)
            
            checker = PerfectStreakChecker(achievement_configs)
            achievements = checker.check(test_user)
            
            # Should not award (need at least 3)
            codes = [a.code for a in achievements]
            assert not any("perfect-streak" in code for code in codes)

