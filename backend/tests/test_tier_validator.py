"""Tests for tier validator."""

import pytest

from app import create_app, db
from app.models import Achievement, PracticeSession, User
from app.services.achievements.achievement_validators.tier_validator import TierValidator
from tests.helpers.data_helpers import create_test_session_with_responses


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


def test_validate_removes_achievement_without_valid_session(app, test_user):
    """Test that validator removes achievements that don't have a valid session."""
    with app.app_context():
        # Create an achievement without a valid session
        achievement = Achievement(
            user_id=test_user.id,
            code="addition-1digit-b",
            title="Test Achievement",
            description="Test",
            icon="🏆",
            category="test",
        )
        db.session.add(achievement)
        db.session.commit()
        
        # Validate - should remove the achievement since there's no session
        removed_count = TierValidator.validate_and_cleanup_tier_achievements(test_user.id)
        
        assert removed_count == 1, "Should remove achievement without valid session"
        
        # Verify achievement was removed
        remaining = Achievement.query.filter_by(
            user_id=test_user.id,
            code="addition-1digit-b"
        ).first()
        
        assert remaining is None, "Achievement should be removed"


def test_validate_keeps_achievement_with_valid_session(app, test_user):
    """Test that validator keeps achievements that have a valid session."""
    with app.app_context():
        # Create a test session that meets tier 'b' requirements (min 30 questions)
        from datetime import datetime
        
        session = PracticeSession(
            user_id=test_user.id,
            mode="standard",
            level=1,
            is_test=True,
            test_type="addition_1digit",
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            total_questions=30,
            correct_count=30,
            accuracy=100.0,
            total_duration_ms=30000,
        )
        db.session.add(session)
        db.session.commit()
        
        # Create an achievement for this tier
        achievement = Achievement(
            user_id=test_user.id,
            code="addition-1digit-b",
            title="Test Achievement",
            description="Test",
            icon="🏆",
            category="test",
        )
        db.session.add(achievement)
        db.session.commit()
        
        # Validate - should keep the achievement since session is valid
        removed_count = TierValidator.validate_and_cleanup_tier_achievements(test_user.id)
        
        assert removed_count == 0, "Should not remove achievement with valid session"
        
        # Verify achievement still exists
        remaining = Achievement.query.filter_by(
            user_id=test_user.id,
            code="addition-1digit-b"
        ).first()
        
        assert remaining is not None, "Achievement should still exist"


def test_validate_removes_achievement_with_invalid_session(app, test_user):
    """Test that validator removes achievements when session doesn't meet requirements."""
    with app.app_context():
        # Create a test session that doesn't meet tier 'b' requirements (needs 30+ questions)
        from datetime import datetime
        
        session = PracticeSession(
            user_id=test_user.id,
            mode="standard",
            level=1,
            is_test=True,
            test_type="addition_1digit",
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            total_questions=20,  # Below minimum of 30
            correct_count=20,
            accuracy=100.0,
            total_duration_ms=20000,
        )
        db.session.add(session)
        db.session.commit()
        
        # Create an achievement for tier 'b' (requires 30+ questions)
        achievement = Achievement(
            user_id=test_user.id,
            code="addition-1digit-b",
            title="Test Achievement",
            description="Test",
            icon="🏆",
            category="test",
        )
        db.session.add(achievement)
        db.session.commit()
        
        # Validate - should remove the achievement since session doesn't meet requirements
        removed_count = TierValidator.validate_and_cleanup_tier_achievements(test_user.id)
        
        assert removed_count == 1, "Should remove achievement when session doesn't meet requirements"
        
        # Verify achievement was removed
        remaining = Achievement.query.filter_by(
            user_id=test_user.id,
            code="addition-1digit-b"
        ).first()
        
        assert remaining is None, "Achievement should be removed"


def test_validate_handles_multiple_achievements(app, test_user):
    """Test that validator handles multiple tier achievements correctly."""
    with app.app_context():
        from datetime import datetime
        
        # Create valid session for tier 'b'
        session = PracticeSession(
            user_id=test_user.id,
            mode="standard",
            level=1,
            is_test=True,
            test_type="addition_1digit",
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            total_questions=30,
            correct_count=30,
            accuracy=100.0,
            total_duration_ms=30000,
        )
        db.session.add(session)
        db.session.commit()
        
        # Create valid achievement
        valid_achievement = Achievement(
            user_id=test_user.id,
            code="addition-1digit-b",
            title="Valid Achievement",
            description="Test",
            icon="🏆",
            category="test",
        )
        db.session.add(valid_achievement)
        
        # Create invalid achievement (no session)
        invalid_achievement = Achievement(
            user_id=test_user.id,
            code="subtraction-1digit-a",
            title="Invalid Achievement",
            description="Test",
            icon="🏆",
            category="test",
        )
        db.session.add(invalid_achievement)
        db.session.commit()
        
        # Validate
        removed_count = TierValidator.validate_and_cleanup_tier_achievements(test_user.id)
        
        assert removed_count == 1, "Should remove only invalid achievement"
        
        # Verify valid achievement still exists
        valid = Achievement.query.filter_by(
            user_id=test_user.id,
            code="addition-1digit-b"
        ).first()
        assert valid is not None, "Valid achievement should still exist"
        
        # Verify invalid achievement was removed
        invalid = Achievement.query.filter_by(
            user_id=test_user.id,
            code="subtraction-1digit-a"
        ).first()
        assert invalid is None, "Invalid achievement should be removed"


def test_validate_handles_unknown_test_type(app, test_user):
    """Test that validator handles unknown test types gracefully."""
    with app.app_context():
        # Create achievement with unknown test type
        achievement = Achievement(
            user_id=test_user.id,
            code="unknown-test-type-b",
            title="Unknown Test",
            description="Test",
            icon="🏆",
            category="test",
        )
        db.session.add(achievement)
        db.session.commit()
        
        # Validate - should skip unknown test types
        removed_count = TierValidator.validate_and_cleanup_tier_achievements(test_user.id)
        
        # Unknown test types are skipped, so achievement remains
        # (This is the current behavior - could be changed to remove them)
        remaining = Achievement.query.filter_by(
            user_id=test_user.id,
            code="unknown-test-type-b"
        ).first()
        
        # Current behavior: unknown test types are skipped, not removed
        assert remaining is not None, "Unknown test types are currently skipped"


def test_validate_handles_invalid_achievement_code_format(app, test_user):
    """Test that validator handles invalid achievement code formats."""
    with app.app_context():
        # Create achievement with invalid format (no tier suffix)
        achievement = Achievement(
            user_id=test_user.id,
            code="addition-1digit",  # Missing tier suffix
            title="Invalid Format",
            description="Test",
            icon="🏆",
            category="test",
        )
        db.session.add(achievement)
        db.session.commit()
        
        # Validate - should skip invalid formats
        removed_count = TierValidator.validate_and_cleanup_tier_achievements(test_user.id)
        
        assert removed_count == 0, "Should skip invalid code formats"
        
        # Verify achievement still exists (skipped, not removed)
        remaining = Achievement.query.filter_by(
            user_id=test_user.id,
            code="addition-1digit"
        ).first()
        
        assert remaining is not None, "Invalid formats are skipped"


