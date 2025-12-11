"""Backend tests for Perfect Streak achievements.

Tests verify that Perfect Streak achievements are correctly awarded for
consecutive perfect sessions.
"""

import pytest
from datetime import datetime

from app import create_app, db
from app.models import Achievement, PracticeSession, Question, Response, User
from app.services.achievement_service import AchievementService
from app.services.analytics_service import AnalyticsService
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


def test_perfect_streak_bronze_3_sessions(app, test_user):
    """Test that Perfect Streak (Bronze) is awarded for 3 consecutive perfect sessions."""
    with app.app_context():
        # Create 3 consecutive perfect sessions (100% accuracy)
        for session_num in range(3):
            questions = create_test_questions(10, 1)
            responses_data = [{
                'question_id': q.id,
                'answer': q.correct_answer,
                'is_correct': True,
                'duration_ms': 3000
            } for q in questions]
            
            session = create_test_session_with_responses(test_user.id, responses_data)
            user = User.query.get(test_user.id)
            metrics = AnalyticsService.compute_user_metrics(user.id)
            AchievementService.ensure_achievements(user, metrics, session_id=session.id)
        
        # Verify achievement was awarded
        achievement = Achievement.query.filter_by(
            user_id=test_user.id,
            code="perfect-streak-bronze"
        ).first()
        
        assert achievement is not None, "Perfect Streak (Bronze) should be awarded for 3 consecutive perfect sessions"


def test_perfect_streak_silver_5_sessions(app, test_user):
    """Test that Perfect Streak (Silver) is awarded for 5 consecutive perfect sessions."""
    with app.app_context():
        # Create 5 consecutive perfect sessions (100% accuracy)
        for session_num in range(5):
            questions = create_test_questions(10, 1)
            responses_data = [{
                'question_id': q.id,
                'answer': q.correct_answer,
                'is_correct': True,
                'duration_ms': 3000
            } for q in questions]
            
            session = create_test_session_with_responses(test_user.id, responses_data)
            user = User.query.get(test_user.id)
            metrics = AnalyticsService.compute_user_metrics(user.id)
            AchievementService.ensure_achievements(user, metrics, session_id=session.id)
        
        # Verify achievement was awarded
        achievement = Achievement.query.filter_by(
            user_id=test_user.id,
            code="perfect-streak-silver"
        ).first()
        
        assert achievement is not None, "Perfect Streak (Silver) should be awarded for 5 consecutive perfect sessions"


def test_perfect_streak_broken_by_imperfect_session(app, test_user):
    """Test that one imperfect session breaks the perfect streak."""
    with app.app_context():
        # Create 2 perfect sessions
        for session_num in range(2):
            questions = create_test_questions(10, 1)
            responses_data = [{
                'question_id': q.id,
                'answer': q.correct_answer,
                'is_correct': True,
                'duration_ms': 3000
            } for q in questions]
            
            session = create_test_session_with_responses(test_user.id, responses_data)
            user = User.query.get(test_user.id)
            metrics = AnalyticsService.compute_user_metrics(user.id)
            AchievementService.ensure_achievements(user, metrics, session_id=session.id)
        
        # Create one imperfect session (not 100% accuracy)
        questions = create_test_questions(10, 1)
        responses_data = []
        for i, q in enumerate(questions):
            responses_data.append({
                'question_id': q.id,
                'answer': q.correct_answer if i < 9 else '999',  # 9 correct, 1 wrong
                'is_correct': i < 9,
                'duration_ms': 3000
            })
        
        session = create_test_session_with_responses(test_user.id, responses_data)
        user = User.query.get(test_user.id)
        metrics = AnalyticsService.compute_user_metrics(user.id)
        AchievementService.ensure_achievements(user, metrics, session_id=session.id)
        
        # Verify NO achievement was awarded (streak broken)
        achievement = Achievement.query.filter(
            Achievement.user_id == test_user.id,
            Achievement.code.like("perfect-streak-%")
        ).first()
        
        assert achievement is None, "Perfect Streak should NOT be awarded when streak is broken"

