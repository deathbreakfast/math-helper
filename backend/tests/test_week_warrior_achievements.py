"""Backend tests for Week Warrior achievements.

Tests verify that Week Warrior achievements are correctly awarded based on
consecutive day streaks, with mocked dates for testing.
"""

import pytest
from datetime import datetime, timedelta

from app import create_app, db
from app.models import Achievement, PracticeSession, Question, Response, User
from app.services.achievement_service import AchievementService
from app.services.analytics_service import AnalyticsService
from tests.helpers.data_helpers import (
    create_test_questions,
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
        user = User(display_name="TestUser", pin="1234", avatar="🐯", experience=0)
        db.session.add(user)
        db.session.commit()
        _ = user.id
        return user


def test_week_warrior_bronze_7_days(app, test_user):
    """Test that Week Warrior (Bronze) is awarded for 7 consecutive days."""
    with app.app_context():
        from app.models import Response
        
        # Create responses on 7 consecutive days
        base_date = datetime.utcnow()
        questions = create_test_questions(1, 1)
        
        for day_offset in range(7):
            response_date = base_date - timedelta(days=6-day_offset)
            response = Response(
                session_id=None,
                user_id=test_user.id,
                question_id=questions[0].id,
                submitted_answer=questions[0].correct_answer,
                correct_answer=questions[0].correct_answer,
                is_correct=True,
                duration_ms=3000,
                answered_at=response_date
            )
            db.session.add(response)
        
        db.session.commit()
        
        # Aggregate daily stats to ensure streak calculation works
        for day_offset in range(7):
            stat_date = (base_date - timedelta(days=6-day_offset)).date()
            AnalyticsService.aggregate_daily_stats(test_user.id, stat_date)
        
        # Get user and compute metrics, then check and award achievements
        user = db.session.get(User, test_user.id)
        metrics = AnalyticsService.compute_user_metrics(test_user.id)
        AchievementService.ensure_achievements(user, metrics, session_id=None)
        
        # Verify achievement was awarded
        achievement = Achievement.query.filter_by(
            user_id=test_user.id,
            code="week-warrior-bronze"
        ).first()
        
        assert achievement is not None, "Week Warrior (Bronze) should be awarded for 7 consecutive days"


def test_week_warrior_silver_14_days(app, test_user):
    """Test that Week Warrior (Silver) is awarded for 14 consecutive days."""
    with app.app_context():
        from app.models import Response
        
        # Create responses on 14 consecutive days
        base_date = datetime.utcnow()
        questions = create_test_questions(1, 1)
        
        for day_offset in range(14):
            response_date = base_date - timedelta(days=13-day_offset)
            response = Response(
                session_id=None,
                user_id=test_user.id,
                question_id=questions[0].id,
                submitted_answer=questions[0].correct_answer,
                correct_answer=questions[0].correct_answer,
                is_correct=True,
                duration_ms=3000,
                answered_at=response_date
            )
            db.session.add(response)
        
        db.session.commit()
        
        # Aggregate daily stats
        for day_offset in range(14):
            stat_date = (base_date - timedelta(days=13-day_offset)).date()
            AnalyticsService.aggregate_daily_stats(test_user.id, stat_date)
        
        # Get user and compute metrics, then check and award achievements
        user = db.session.get(User, test_user.id)
        metrics = AnalyticsService.compute_user_metrics(test_user.id)
        AchievementService.ensure_achievements(user, metrics, session_id=None)
        
        # Verify achievement was awarded
        achievement = Achievement.query.filter_by(
            user_id=test_user.id,
            code="week-warrior-silver"
        ).first()
        
        assert achievement is not None, "Week Warrior (Silver) should be awarded for 14 consecutive days"


def test_week_warrior_streak_broken(app, test_user):
    """Test that missing a day breaks the streak."""
    with app.app_context():
        from app.models import Response
        
        # Create responses on 6 consecutive days, skip a day, then 1 more day
        base_date = datetime.utcnow()
        questions = create_test_questions(1, 1)
        
        # Days 1-6
        for day_offset in range(6):
            response_date = base_date - timedelta(days=7-day_offset)
            response = Response(
                session_id=None,
                user_id=test_user.id,
                question_id=questions[0].id,
                submitted_answer=questions[0].correct_answer,
                correct_answer=questions[0].correct_answer,
                is_correct=True,
                duration_ms=3000,
                answered_at=response_date
            )
            db.session.add(response)
        
        # Skip day 7, then day 8
        response_date = base_date - timedelta(days=0)
        response = Response(
            session_id=None,
            user_id=test_user.id,
            question_id=questions[0].id,
            submitted_answer=questions[0].correct_answer,
            correct_answer=questions[0].correct_answer,
            is_correct=True,
            duration_ms=3000,
            answered_at=response_date
        )
        db.session.add(response)
        
        db.session.commit()
        
        # Aggregate daily stats
        for day_offset in range(8):
            if day_offset != 6:  # Skip the missing day
                stat_date = (base_date - timedelta(days=7-day_offset)).date()
                AnalyticsService.aggregate_daily_stats(test_user.id, stat_date)
        
        # Get user and compute metrics, then check and award achievements
        user = db.session.get(User, test_user.id)
        metrics = AnalyticsService.compute_user_metrics(test_user.id)
        AchievementService.ensure_achievements(user, metrics, session_id=None)
        
        # Verify NO achievement was awarded (streak broken)
        achievement = Achievement.query.filter(
            Achievement.user_id == test_user.id,
            Achievement.code.like("week-warrior-%")
        ).first()
        
        assert achievement is None, "Week Warrior should NOT be awarded when streak is broken"




