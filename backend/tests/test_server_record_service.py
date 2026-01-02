"""Backend tests for ServerRecordService.

Tests verify server record tracking, Champion tier qualification,
and record checking logic.
"""

import pytest
from datetime import datetime

from app import create_app, db
from app.models import User, ServerRecord, PracticeSession
from app.services.server_record_service import ServerRecordService


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
        # Access id to ensure it's loaded before returning (prevents DetachedInstanceError)
        _ = user.id
        return user


@pytest.fixture
def test_session(app, test_user):
    """Create a test practice session."""
    with app.app_context():
        session = PracticeSession(
            user_id=test_user.id,
            mode="standard",
            level=1,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            total_questions=100,
            correct_count=100,
            accuracy=100.0,
            total_duration_ms=150000,  # 1.5 seconds per question
        )
        db.session.add(session)
        db.session.commit()
        # Access id to ensure it's loaded before returning (prevents DetachedInstanceError)
        _ = session.id
        return session


def test_server_record_model_001_create_record(app, test_user, test_session):
    """SR-MODEL-001: ServerRecord can be created with all required fields."""
    with app.app_context():
        record = ServerRecord(
            achievement_type="addition-basics-champion",
            record_type="speed",
            record_value=1.5,
            user_id=test_user.id,
            session_id=test_session.id,
        )
        db.session.add(record)
        db.session.commit()
        
        assert record.id is not None
        assert record.achievement_type == "addition-basics-champion"
        assert record.record_type == "speed"
        assert record.record_value == 1.5
        assert record.user_id == test_user.id
        assert record.session_id == test_session.id


def test_server_record_service_001_get_current_record_none(app):
    """SR-SVC-001: getCurrentRecord() returns None when no record exists."""
    with app.app_context():
        record = ServerRecordService.getCurrentRecord("nonexistent-achievement")
        assert record is None


def test_server_record_service_002_get_current_record_exists(app, test_user, test_session):
    """SR-SVC-002: getCurrentRecord() returns existing record."""
    with app.app_context():
        # Create a record
        record = ServerRecord(
            achievement_type="test-achievement",
            record_type="speed",
            record_value=2.0,
            user_id=test_user.id,
            session_id=test_session.id,
        )
        db.session.add(record)
        db.session.commit()
        
        # Retrieve it
        retrieved = ServerRecordService.getCurrentRecord("test-achievement")
        assert retrieved is not None
        assert retrieved.achievement_type == "test-achievement"
        assert retrieved.record_value == 2.0


def test_server_record_service_003_is_champion_eligible_no_record(app):
    """SR-SVC-003: isChampionEligible() returns True when no record exists."""
    with app.app_context():
        # No existing record, should be eligible
        eligible = ServerRecordService.isChampionEligible(
            "test-achievement", "speed", 1.5
        )
        assert eligible is True


def test_server_record_service_004_is_champion_eligible_speed_beats_record(app, test_user, test_session):
    """SR-SVC-004: isChampionEligible() returns True for speed when value is lower (better)."""
    with app.app_context():
        # Create existing record with slower time
        record = ServerRecord(
            achievement_type="test-achievement",
            record_type="speed",
            record_value=2.0,  # 2 seconds per question
            user_id=test_user.id,
            session_id=test_session.id,
        )
        db.session.add(record)
        db.session.commit()
        
        # New value is faster (lower is better for speed)
        eligible = ServerRecordService.isChampionEligible(
            "test-achievement", "speed", 1.5  # 1.5 seconds per question
        )
        assert eligible is True


def test_server_record_service_005_is_champion_eligible_speed_tie_rejected(app, test_user, test_session):
    """SR-SVC-005: isChampionEligible() returns False for speed when value ties (no ties allowed)."""
    with app.app_context():
        # Create existing record
        record = ServerRecord(
            achievement_type="test-achievement",
            record_type="speed",
            record_value=2.0,
            user_id=test_user.id,
            session_id=test_session.id,
        )
        db.session.add(record)
        db.session.commit()
        
        # Same value (tie) should not be eligible
        eligible = ServerRecordService.isChampionEligible(
            "test-achievement", "speed", 2.0
        )
        assert eligible is False


def test_server_record_service_006_is_champion_eligible_accuracy_beats_record(app, test_user, test_session):
    """SR-SVC-006: isChampionEligible() returns True for accuracy when value is higher (better)."""
    with app.app_context():
        # Create existing record with lower accuracy
        record = ServerRecord(
            achievement_type="test-achievement",
            record_type="accuracy",
            record_value=95.0,  # 95% accuracy
            user_id=test_user.id,
            session_id=test_session.id,
        )
        db.session.add(record)
        db.session.commit()
        
        # New value is higher (better for accuracy)
        eligible = ServerRecordService.isChampionEligible(
            "test-achievement", "accuracy", 100.0  # 100% accuracy
        )
        assert eligible is True


def test_server_record_service_007_check_and_update_record_new_record(app, test_user, test_session):
    """SR-SVC-007: checkAndUpdateRecord() creates new record when none exists."""
    with app.app_context():
        result = ServerRecordService.checkAndUpdateRecord(
            achievement_type="test-achievement",
            record_type="speed",
            value=1.5,
            user_id=test_user.id,
            session_id=test_session.id,
        )
        
        assert result is True
        
        # Verify record was created
        record = ServerRecordService.getCurrentRecord("test-achievement")
        assert record is not None
        assert record.record_value == 1.5
        assert record.user_id == test_user.id


def test_server_record_service_008_check_and_update_record_updates_existing(app, test_user, test_session):
    """SR-SVC-008: checkAndUpdateRecord() updates existing record when new value is better."""
    with app.app_context():
        # Create initial record
        record = ServerRecord(
            achievement_type="test-achievement",
            record_type="speed",
            record_value=2.0,
            user_id=test_user.id,
            session_id=test_session.id,
        )
        db.session.add(record)
        db.session.commit()
        
        original_id = record.id
        
        # Update with better value
        result = ServerRecordService.checkAndUpdateRecord(
            achievement_type="test-achievement",
            record_type="speed",
            value=1.5,
            user_id=test_user.id,
            session_id=test_session.id,
        )
        
        assert result is True
        
        # Verify record was updated (same ID)
        updated_record = ServerRecordService.getCurrentRecord("test-achievement")
        assert updated_record.id == original_id
        assert updated_record.record_value == 1.5


def test_server_record_service_009_check_and_update_record_rejects_worse(app, test_user, test_session):
    """SR-SVC-009: checkAndUpdateRecord() returns False when value doesn't beat existing record."""
    with app.app_context():
        # Create existing record with better value
        record = ServerRecord(
            achievement_type="test-achievement",
            record_type="speed",
            record_value=1.5,
            user_id=test_user.id,
            session_id=test_session.id,
        )
        db.session.add(record)
        db.session.commit()
        
        # Try to update with worse value
        result = ServerRecordService.checkAndUpdateRecord(
            achievement_type="test-achievement",
            record_type="speed",
            value=2.0,  # Slower (worse)
            user_id=test_user.id,
            session_id=test_session.id,
        )
        
        assert result is False
        
        # Verify record was not changed
        unchanged_record = ServerRecordService.getCurrentRecord("test-achievement")
        assert unchanged_record.record_value == 1.5


def test_server_record_service_010_determine_record_type(app):
    """SR-SVC-010: _determine_record_type() correctly identifies record types."""
    with app.app_context():
        assert ServerRecordService._determine_record_type("speed-demon-champion") == "speed"
        assert ServerRecordService._determine_record_type("addition-basics-champion") == "accuracy"
        assert ServerRecordService._determine_record_type("question-master-champion") == "volume"
        assert ServerRecordService._determine_record_type("week-warrior-champion") == "streak"
        assert ServerRecordService._determine_record_type("unknown") is None


def test_server_record_service_011_determine_record_value_speed(app, test_session):
    """SR-SVC-011: _determine_record_value() calculates speed correctly."""
    with app.app_context():
        # Session with 100 questions in 150 seconds = 1.5s per question
        value = ServerRecordService._determine_record_value(test_session, "speed")
        assert value == pytest.approx(1.5, rel=0.01)


def test_server_record_service_012_determine_record_value_accuracy(app, test_session):
    """SR-SVC-012: _determine_record_value() returns accuracy correctly."""
    with app.app_context():
        value = ServerRecordService._determine_record_value(test_session, "accuracy")
        assert value == 100.0


def test_server_record_service_013_determine_record_value_volume(app, test_session):
    """SR-SVC-013: _determine_record_value() returns question count for volume."""
    with app.app_context():
        value = ServerRecordService._determine_record_value(test_session, "volume")
        assert value == 100.0


def test_server_record_service_014_can_achievement_have_champion_tier(app):
    """SR-SVC-014: canAchievementHaveChampionTier() correctly identifies qualifying achievements."""
    with app.app_context():
        # Qualifying achievements
        assert ServerRecordService.canAchievementHaveChampionTier("speed-demon-champion") is True
        assert ServerRecordService.canAchievementHaveChampionTier("addition-basics-champion") is True
        assert ServerRecordService.canAchievementHaveChampionTier("addition-1digit-champion") is True
        assert ServerRecordService.canAchievementHaveChampionTier("question-master-champion") is True
        assert ServerRecordService.canAchievementHaveChampionTier("week-warrior-champion") is True
        
        # Non-qualifying achievements
        assert ServerRecordService.canAchievementHaveChampionTier("first-steps") is False
        assert ServerRecordService.canAchievementHaveChampionTier("first-victory") is False


def test_server_record_model_002_unique_constraint(app, test_user, test_session):
    """SR-MODEL-002: ServerRecord enforces unique constraint on achievement_type."""
    with app.app_context():
        # Create first record
        record1 = ServerRecord(
            achievement_type="test-achievement",
            record_type="speed",
            record_value=2.0,
            user_id=test_user.id,
            session_id=test_session.id,
        )
        db.session.add(record1)
        db.session.commit()
        
        # Try to create second record with same achievement_type
        record2 = ServerRecord(
            achievement_type="test-achievement",  # Same achievement_type
            record_type="speed",
            record_value=1.5,
            user_id=test_user.id,
            session_id=test_session.id,
        )
        db.session.add(record2)
        
        # Should raise IntegrityError due to unique constraint
        with pytest.raises(Exception):  # SQLAlchemy raises IntegrityError
            db.session.commit()


def test_server_record_model_003_relationships(app, test_user, test_session):
    """SR-MODEL-003: ServerRecord has relationships to User and PracticeSession."""
    with app.app_context():
        record = ServerRecord(
            achievement_type="test-achievement",
            record_type="speed",
            record_value=1.5,
            user_id=test_user.id,
            session_id=test_session.id,
        )
        db.session.add(record)
        db.session.commit()
        
        # Refresh to load relationships
        db.session.refresh(record)
        
        # Check relationships work
        assert record.user is not None
        assert record.user.id == test_user.id
        assert record.session is not None
        assert record.session.id == test_session.id

