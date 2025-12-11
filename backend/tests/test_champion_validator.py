"""Tests for champion validator."""

import pytest
from datetime import datetime

from app import create_app, db
from app.models import PracticeSession, ServerRecord, User
from app.services.achievements.achievement_validators.champion_validator import ChampionValidator


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
        db.session.refresh(user)
        # Access id to ensure it's loaded before returning (prevents DetachedInstanceError)
        _ = user.id
        return user


@pytest.fixture
def test_session(app, test_user):
    """Create a test practice session."""
    with app.app_context():
        # Refresh user to ensure it's attached to the session
        user = db.session.merge(test_user)
        session = PracticeSession(
            user_id=user.id,
            mode="standard",
            level=1,
            is_test=False,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            total_questions=50,
            correct_count=50,
            accuracy=100.0,
            total_duration_ms=50000,  # 1 second per question average
        )
        db.session.add(session)
        db.session.commit()
        db.session.refresh(session)
        return session


def test_check_eligibility_returns_false_for_non_champion_tier(app, test_session):
    """Test that validator returns False for non-Champion tier."""
    with app.app_context():
        result = ChampionValidator.check_eligibility(
            "addition-basics-champion",
            test_session,
            "divine"
        )
        
        assert result is False, "Should return False for non-Champion tier"


def test_check_eligibility_returns_false_for_non_qualifying_achievement(app, test_session):
    """Test that validator returns False for achievements that can't have Champion tier."""
    with app.app_context():
        result = ChampionValidator.check_eligibility(
            "first-steps",  # Cannot have Champion tier
            test_session,
            "champion"
        )
        
        assert result is False, "Should return False for non-qualifying achievement"


def test_check_eligibility_sets_record_when_no_existing_record(app, test_session):
    """Test that validator sets a record when no existing record exists."""
    with app.app_context():
        achievement_code = "addition-basics-champion"
        
        # Ensure no existing record
        existing = ServerRecord.query.filter_by(achievement_type=achievement_code).first()
        if existing:
            db.session.delete(existing)
            db.session.commit()
        
        result = ChampionValidator.check_eligibility(
            achievement_code,
            test_session,
            "champion"
        )
        
        assert result is True, "Should return True when setting new record"
        
        # Verify record was created
        record = ServerRecord.query.filter_by(achievement_type=achievement_code).first()
        assert record is not None, "Record should be created"
        assert record.user_id == test_session.user_id, "Record should have correct user_id"
        assert record.session_id == test_session.id, "Record should have correct session_id"


def test_check_eligibility_updates_record_when_beating_existing(app, test_session):
    """Test that validator updates record when beating existing record."""
    with app.app_context():
        # Use speed-demon-champion for speed-based test
        achievement_code = "speed-demon-champion"
        
        # Create an existing record with slower speed (higher time per question)
        existing_record = ServerRecord(
            achievement_type=achievement_code,
            record_type="speed",
            record_value=2.0,  # 2 seconds per question (slower)
            user_id=test_session.user_id,
            achieved_at=datetime.utcnow(),
        )
        db.session.add(existing_record)
        db.session.commit()
        
        # test_session has 1 second per question (faster), so should beat record
        result = ChampionValidator.check_eligibility(
            achievement_code,
            test_session,
            "champion"
        )
        
        assert result is True, "Should return True when beating existing record"
        
        # Verify record was updated
        record = ServerRecord.query.filter_by(achievement_type=achievement_code).first()
        assert record is not None, "Record should exist"
        assert record.record_value == 1.0, "Record should be updated to new value (1 sec/question)"
        assert record.user_id == test_session.user_id, "Record should have correct user_id"


def test_check_eligibility_returns_false_when_not_beating_record(app, test_session):
    """Test that validator returns False when not beating existing record."""
    with app.app_context():
        # Use speed-demon-champion for speed-based test
        achievement_code = "speed-demon-champion"
        
        # Create an existing record with faster speed (lower time per question)
        existing_record = ServerRecord(
            achievement_type=achievement_code,
            record_type="speed",
            record_value=0.5,  # 0.5 seconds per question (faster)
            user_id=test_session.user_id,
            achieved_at=datetime.utcnow(),
        )
        db.session.add(existing_record)
        db.session.commit()
        
        # test_session has 1 second per question (slower), so should not beat record
        result = ChampionValidator.check_eligibility(
            achievement_code,
            test_session,
            "champion"
        )
        
        assert result is False, "Should return False when not beating existing record"
        
        # Verify record was not updated
        record = ServerRecord.query.filter_by(achievement_type=achievement_code).first()
        assert record.record_value == 0.5, "Record should remain unchanged"


def test_check_eligibility_handles_accuracy_based_achievement(app, test_user):
    """Test that validator handles accuracy-based achievements correctly."""
    with app.app_context():
        # Refresh user to ensure it's attached to the session
        user = db.session.merge(test_user)
        # Create a session with high accuracy
        session = PracticeSession(
            user_id=user.id,
            mode="standard",
            level=1,
            is_test=False,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            total_questions=50,
            correct_count=50,
            accuracy=100.0,
            total_duration_ms=50000,
        )
        db.session.add(session)
        db.session.commit()
        
        achievement_code = "addition-basics-champion"
        
        # Ensure no existing record
        existing = ServerRecord.query.filter_by(achievement_type=achievement_code).first()
        if existing:
            db.session.delete(existing)
            db.session.commit()
        
        result = ChampionValidator.check_eligibility(
            achievement_code,
            session,
            "champion"
        )
        
        assert result is True, "Should return True for accuracy-based achievement"
        
        # Verify record was created with accuracy value
        record = ServerRecord.query.filter_by(achievement_type=achievement_code).first()
        assert record is not None, "Record should be created"
        assert record.record_type == "accuracy", "Record type should be accuracy"
        assert record.record_value == 100.0, "Record value should be accuracy percentage"


def test_check_eligibility_handles_volume_based_achievement(app, test_user):
    """Test that validator handles volume-based achievements correctly."""
    with app.app_context():
        # Refresh user to ensure it's attached to the session
        user = db.session.merge(test_user)
        # Create a session with many questions
        session = PracticeSession(
            user_id=user.id,
            mode="standard",
            level=1,
            is_test=False,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            total_questions=100,
            correct_count=100,
            accuracy=100.0,
            total_duration_ms=100000,
        )
        db.session.add(session)
        db.session.commit()
        
        achievement_code = "question-master-champion"
        
        # Ensure no existing record
        existing = ServerRecord.query.filter_by(achievement_type=achievement_code).first()
        if existing:
            db.session.delete(existing)
            db.session.commit()
        
        result = ChampionValidator.check_eligibility(
            achievement_code,
            session,
            "champion"
        )
        
        assert result is True, "Should return True for volume-based achievement"
        
        # Verify record was created with volume value
        record = ServerRecord.query.filter_by(achievement_type=achievement_code).first()
        assert record is not None, "Record should be created"
        assert record.record_type == "volume", "Record type should be volume"
        assert record.record_value == 100.0, "Record value should be question count"


def test_check_eligibility_returns_false_when_record_value_cannot_be_determined(app, test_user):
    """Test that validator returns False when record value cannot be determined."""
    with app.app_context():
        # Refresh user to ensure it's attached to the session
        user = db.session.merge(test_user)
        # Create a session with missing data (no duration for speed calculation)
        session = PracticeSession(
            user_id=user.id,
            mode="standard",
            level=1,
            is_test=False,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            total_questions=50,
            correct_count=50,
            accuracy=100.0,
            total_duration_ms=None,  # Missing duration
        )
        db.session.add(session)
        db.session.commit()
        
        achievement_code = "speed-demon-champion"
        
        result = ChampionValidator.check_eligibility(
            achievement_code,
            session,
            "champion"
        )
        
        assert result is False, "Should return False when record value cannot be determined"

