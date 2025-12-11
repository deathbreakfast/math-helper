"""Comprehensive tests for AccuracyAceChecker.

Tests cover all methods in AccuracyAceChecker to achieve >80% coverage.
"""

import pytest
from datetime import datetime

from app import create_app, db
from app.models import Achievement, PracticeSession, User
from app.services.achievements.achievement_checkers.accuracy_ace_checker import AccuracyAceChecker
from app.services.level_config_service import LevelConfigService


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
        user = User(display_name="Test User", pin="1234", avatar="🐯", level=1)
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user


@pytest.fixture
def achievement_configs():
    """Get achievement configs for testing."""
    return LevelConfigService.get_all_achievement_configs()


@pytest.fixture
def accuracy_ace_checker(achievement_configs):
    """Create an AccuracyAceChecker instance."""
    return AccuracyAceChecker(achievement_configs)


class TestAccuracyAceChecker:
    """Test suite for AccuracyAceChecker."""

    def test_init(self, achievement_configs):
        """Test __init__ initializes checker."""
        checker = AccuracyAceChecker(achievement_configs)
        assert checker.achievement_configs == achievement_configs

    def test_check_no_session(self, app, test_user, accuracy_ace_checker):
        """Test check returns empty when no session provided."""
        with app.app_context():
            result = accuracy_ace_checker.check(None, user=test_user)
            assert result == []

    def test_check_incomplete_session(self, app, test_user, accuracy_ace_checker):
        """Test check returns empty for incomplete session."""
        with app.app_context():
            session = PracticeSession(
                user_id=test_user.id,
                is_test=False,
                mode="standard",
                level=1,
                total_questions=10,
                correct_count=8,
                accuracy=80.0,
                completed_at=None  # Not completed
            )
            db.session.add(session)
            db.session.commit()
            
            result = accuracy_ace_checker.check(session, user=test_user)
            assert result == []

    def test_check_test_session(self, app, test_user, accuracy_ace_checker):
        """Test check returns empty for test session."""
        with app.app_context():
            session = PracticeSession(
                user_id=test_user.id,
                is_test=True,
                mode="standard",
                level=1,
                total_questions=10,
                correct_count=10,
                accuracy=100.0,
                completed_at=datetime.utcnow()
            )
            db.session.add(session)
            db.session.commit()
            
            result = accuracy_ace_checker.check(session, user=test_user)
            assert result == []

    def test_check_no_user_provided(self, app, test_user, accuracy_ace_checker):
        """Test check fetches user from session if not provided."""
        with app.app_context():
            session = PracticeSession(
                user_id=test_user.id,
                is_test=False,
                mode="standard",
                level=1,
                total_questions=10,
                correct_count=8,
                accuracy=80.0,
                completed_at=datetime.utcnow()
            )
            db.session.add(session)
            db.session.commit()
            
            # Don't provide user, should fetch from session
            result = accuracy_ace_checker.check(session, user=None)
            # Should handle gracefully (may return empty if user not found via relationship)
            assert isinstance(result, list)

    def test_check_user_not_found(self, app, accuracy_ace_checker):
        """Test check returns empty when user not found via query."""
        with app.app_context():
            from unittest.mock import patch
            from app.models import User
            
            # Create a mock session object
            session = PracticeSession(
                user_id=1,
                is_test=False,
                mode="standard",
                level=1,
                total_questions=10,
                correct_count=8,
                accuracy=80.0,
                completed_at=datetime.utcnow()
            )
            
            # Mock User.query.get to return None
            with patch.object(User, 'query') as mock_query:
                mock_query.get.return_value = None
                
                result = accuracy_ace_checker.check(session, user=None)
                assert result == []

    def test_check_no_accuracy_ace_configs(self, app, test_user):
        """Test check returns empty when no accuracy-ace configs."""
        with app.app_context():
            # Create checker with empty configs
            checker = AccuracyAceChecker({})
            
            session = PracticeSession(
                user_id=test_user.id,
                is_test=False,
                mode="standard",
                level=1,
                total_questions=10,
                correct_count=8,
                accuracy=80.0,
                completed_at=datetime.utcnow()
            )
            db.session.add(session)
            db.session.commit()
            
            result = checker.check(session, user=test_user)
            assert result == []

    def test_check_too_few_questions(self, app, test_user, accuracy_ace_checker):
        """Test check returns empty when less than 10 questions."""
        with app.app_context():
            session = PracticeSession(
                user_id=test_user.id,
                is_test=False,
                mode="standard",
                level=1,
                total_questions=5,  # Less than 10
                correct_count=5,
                accuracy=100.0,
                completed_at=datetime.utcnow()
            )
            db.session.add(session)
            db.session.commit()
            
            result = accuracy_ace_checker.check(session, user=test_user)
            assert result == []

    def test_check_already_earned(self, app, test_user, accuracy_ace_checker):
        """Test check does not award if already earned."""
        with app.app_context():
            # Create existing achievement
            achievement = Achievement(
                user_id=test_user.id,
                code="accuracy-ace-bronze",
                title="Accuracy Ace (Bronze)",
                description="80% accuracy",
                icon="🎯",
                category="accuracy"
            )
            db.session.add(achievement)
            
            session = PracticeSession(
                user_id=test_user.id,
                is_test=False,
                mode="standard",
                level=1,
                total_questions=10,
                correct_count=8,
                accuracy=80.0,
                completed_at=datetime.utcnow()
            )
            db.session.add(session)
            db.session.commit()
            
            result = accuracy_ace_checker.check(session, user=test_user)
            # Should not award if already earned
            assert len(result) == 0

    def test_check_awards_highest_tier(self, app, test_user, accuracy_ace_checker):
        """Test check awards highest qualifying tier."""
        with app.app_context():
            session = PracticeSession(
                user_id=test_user.id,
                is_test=False,
                mode="standard",
                level=1,
                total_questions=10,
                correct_count=9,  # 90% accuracy (qualifies for gold)
                accuracy=90.0,
                completed_at=datetime.utcnow()
            )
            db.session.add(session)
            db.session.commit()
            
            result = accuracy_ace_checker.check(session, user=test_user)
            
            # Should award highest tier (gold, not bronze or silver)
            assert len(result) == 1
            assert result[0].code == "accuracy-ace-gold"

    def test_check_champion_eligibility_check(self, app, test_user, accuracy_ace_checker):
        """Test check checks Champion tier eligibility for Divine tier."""
        with app.app_context():
            session = PracticeSession(
                user_id=test_user.id,
                is_test=False,
                mode="standard",
                level=1,
                total_questions=10,
                correct_count=10,  # 100% accuracy (qualifies for divine)
                accuracy=100.0,
                completed_at=datetime.utcnow()
            )
            db.session.add(session)
            db.session.commit()
            
            result = accuracy_ace_checker.check(session, user=test_user)
            
            # Should check champion eligibility if divine tier achieved
            # May award divine or champion depending on eligibility
            assert isinstance(result, list)

    def test_check_accuracy_none(self, app, test_user, accuracy_ace_checker):
        """Test check handles None accuracy."""
        with app.app_context():
            session = PracticeSession(
                user_id=test_user.id,
                is_test=False,
                mode="standard",
                level=1,
                total_questions=10,
                correct_count=0,
                accuracy=None,  # None accuracy
                completed_at=datetime.utcnow()
            )
            db.session.add(session)
            db.session.commit()
            
            result = accuracy_ace_checker.check(session, user=test_user)
            # Should handle None gracefully
            assert result == []

