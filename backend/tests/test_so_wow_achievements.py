"""Backend tests for So, Wow! achievements.

Tests verify that So, Wow! achievements are correctly awarded when a user earns
their first achievement of a tier, and that multiple tiers can be awarded in one session.
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
    award_achievement_directly,
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


def test_so_wow_bronze_first_bronze_achievement(app, test_user):
    """Test that So, Wow! (Bronze) is awarded when user earns first bronze achievement."""
    with app.app_context():
        # Award a bronze achievement directly
        bronze_ach = award_achievement_directly(test_user.id, "speed-demon-bronze")
        
        # Check So, Wow! achievements
        so_wow_achievements = AchievementService.check_so_wow_achievements(
            test_user, [bronze_ach], session_id=None
        )
        
        # Verify So, Wow! (Bronze) was awarded
        so_wow = Achievement.query.filter_by(
            user_id=test_user.id,
            code="so-wow-bronze"
        ).first()
        
        assert so_wow is not None, "So, Wow! (Bronze) should be awarded when first bronze achievement is earned"


def test_so_wow_silver_first_silver_achievement(app, test_user):
    """Test that So, Wow! (Silver) is awarded when user earns first silver achievement."""
    with app.app_context():
        # Award a silver achievement directly
        silver_ach = award_achievement_directly(test_user.id, "speed-demon-silver")
        
        # Check So, Wow! achievements
        so_wow_achievements = AchievementService.check_so_wow_achievements(
            test_user, [silver_ach], session_id=None
        )
        
        # Verify So, Wow! (Silver) was awarded
        so_wow = Achievement.query.filter_by(
            user_id=test_user.id,
            code="so-wow-silver"
        ).first()
        
        assert so_wow is not None, "So, Wow! (Silver) should be awarded when first silver achievement is earned"


def test_so_wow_multiple_tiers_one_session(app, test_user):
    """Test that multiple So, Wow! tiers can be awarded in one session."""
    with app.app_context():
        # Award both bronze and silver achievements in one session
        bronze_ach = award_achievement_directly(test_user.id, "speed-demon-bronze")
        silver_ach = award_achievement_directly(test_user.id, "speed-demon-silver")
        
        # Check So, Wow! achievements
        so_wow_achievements = AchievementService.check_so_wow_achievements(
            test_user, [bronze_ach, silver_ach], session_id=None
        )
        
        # Verify both So, Wow! achievements were awarded
        so_wow_bronze = Achievement.query.filter_by(
            user_id=test_user.id,
            code="so-wow-bronze"
        ).first()
        so_wow_silver = Achievement.query.filter_by(
            user_id=test_user.id,
            code="so-wow-silver"
        ).first()
        
        assert so_wow_bronze is not None, "So, Wow! (Bronze) should be awarded"
        assert so_wow_silver is not None, "So, Wow! (Silver) should be awarded in same session"


def test_so_wow_only_awarded_once_per_tier(app, test_user):
    """Test that So, Wow! is only awarded once per tier, not per achievement."""
    with app.app_context():
        # Award first bronze achievement
        bronze_ach1 = award_achievement_directly(test_user.id, "speed-demon-bronze")
        
        # Check So, Wow! achievements
        so_wow_achievements1 = AchievementService.check_so_wow_achievements(
            test_user, [bronze_ach1], session_id=None
        )
        
        # Verify So, Wow! (Bronze) was awarded
        so_wow1 = Achievement.query.filter_by(
            user_id=test_user.id,
            code="so-wow-bronze"
        ).first()
        assert so_wow1 is not None, "First So, Wow! (Bronze) should be awarded"
        
        # Award second bronze achievement
        bronze_ach2 = award_achievement_directly(test_user.id, "question-master-bronze")
        
        # Check So, Wow! achievements again
        so_wow_achievements2 = AchievementService.check_so_wow_achievements(
            test_user, [bronze_ach2], session_id=None
        )
        
        # Verify only one So, Wow! (Bronze) exists
        so_wow_count = Achievement.query.filter_by(
            user_id=test_user.id,
            code="so-wow-bronze"
        ).count()
        
        assert so_wow_count == 1, "So, Wow! (Bronze) should only be awarded once per tier"


def test_so_wow_not_awarded_if_tier_already_exists(app, test_user):
    """Test that So, Wow! is NOT awarded if user already has achievements of that tier."""
    with app.app_context():
        # Award a bronze achievement (this will trigger So, Wow!)
        bronze_ach1 = award_achievement_directly(test_user.id, "speed-demon-bronze")
        AchievementService.check_so_wow_achievements(test_user, [bronze_ach1], session_id=None)
        
        # Verify So, Wow! (Bronze) was awarded
        so_wow1 = Achievement.query.filter_by(
            user_id=test_user.id,
            code="so-wow-bronze"
        ).first()
        assert so_wow1 is not None, "So, Wow! (Bronze) should be awarded first time"
        
        # Award another bronze achievement
        bronze_ach2 = award_achievement_directly(test_user.id, "question-master-bronze")
        
        # Check So, Wow! achievements again
        so_wow_achievements2 = AchievementService.check_so_wow_achievements(
            test_user, [bronze_ach2], session_id=None
        )
        
        # Verify no new So, Wow! achievement was created
        so_wow_count = Achievement.query.filter_by(
            user_id=test_user.id,
            code="so-wow-bronze"
        ).count()
        
        assert so_wow_count == 1, "So, Wow! should NOT be awarded again if tier already exists"


def test_so_wow_integration_with_session(app, test_user):
    """Test So, Wow! in integration with actual session completion."""
    with app.app_context():
        # Create a session that awards a bronze achievement (e.g., speed-demon-bronze)
        questions = create_test_questions(10, 1)
        responses_data = [{
            'question_id': q.id,
            'answer': q.correct_answer,
            'is_correct': True,
            'duration_ms': 4500  # 4.5s average, qualifies for speed-demon-bronze
        } for q in questions]
        
        session = create_test_session_with_responses(test_user.id, responses_data)
        
        # Get user and compute metrics, then check and award achievements
        user = User.query.get(test_user.id)
        metrics = AnalyticsService.compute_user_metrics(user.id)
        AchievementService.ensure_achievements(user, metrics, session_id=session.id)
        
        # Get newly awarded achievements
        new_achievements = AchievementService.get_achievements_by_session(session.id)
        
        # Check So, Wow! achievements
        so_wow_achievements = AchievementService.check_so_wow_achievements(
            user, new_achievements, session_id=session.id
        )
        
        # If a bronze achievement was awarded, So, Wow! (Bronze) should also be awarded
        bronze_achievements = [a for a in new_achievements if a.code.endswith("-bronze")]
        if bronze_achievements:
            so_wow = Achievement.query.filter_by(
                user_id=test_user.id,
                code="so-wow-bronze"
            ).first()
            assert so_wow is not None, "So, Wow! (Bronze) should be awarded when bronze achievement is earned in session"


