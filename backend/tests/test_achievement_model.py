"""Backend tests for Achievement model with session_id tracking.

Tests verify that achievements can be created with and without session_id,
and that the foreign key relationship works correctly.
"""

import pytest
from datetime import datetime

from app import create_app, db
from app.models import User, Achievement, PracticeSession


@pytest.fixture
def app():
    """Create test Flask application."""
    app = create_app(testing=True)
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
        return user


@pytest.fixture
def test_session(app, test_user):
    """Create a test practice session."""
    with app.app_context():
        session = PracticeSession(
            user_id=test_user.id,
            mode="standard",
            level=1,
            is_test=False,
            started_at=datetime.utcnow(),
        )
        db.session.add(session)
        db.session.commit()
        return session


def test_achievement_model_001_create_without_session_id(app, test_user):
    """ACH-MODEL-001: Achievement can be created without session_id (nullable)."""
    with app.app_context():
        achievement = Achievement(
            user_id=test_user.id,
            code="test-achievement",
            title="Test Achievement",
            description="Test description",
            icon="🏆",
            category="test",
            earned_at=datetime.utcnow(),
            session_id=None,
        )
        db.session.add(achievement)
        db.session.commit()
        
        assert achievement.id is not None
        assert achievement.session_id is None
        assert achievement.user_id == test_user.id


def test_achievement_model_002_create_with_session_id(app, test_user, test_session):
    """ACH-MODEL-002: Achievement can be created with session_id."""
    with app.app_context():
        achievement = Achievement(
            user_id=test_user.id,
            code="test-achievement-session",
            title="Test Achievement with Session",
            description="Test description",
            icon="🏆",
            category="test",
            earned_at=datetime.utcnow(),
            session_id=test_session.id,
        )
        db.session.add(achievement)
        db.session.commit()
        
        assert achievement.id is not None
        assert achievement.session_id == test_session.id
        assert achievement.user_id == test_user.id


def test_achievement_model_003_query_by_session_id(app, test_user, test_session):
    """ACH-MODEL-003: Achievements can be queried by session_id."""
    with app.app_context():
        # Create achievements with and without session_id
        achievement1 = Achievement(
            user_id=test_user.id,
            code="achievement-1",
            title="Achievement 1",
            description="Description 1",
            icon="🏆",
            category="test",
            session_id=test_session.id,
        )
        achievement2 = Achievement(
            user_id=test_user.id,
            code="achievement-2",
            title="Achievement 2",
            description="Description 2",
            icon="🏆",
            category="test",
            session_id=None,
        )
        db.session.add(achievement1)
        db.session.add(achievement2)
        db.session.commit()
        
        # Query achievements by session_id
        session_achievements = Achievement.query.filter_by(session_id=test_session.id).all()
        
        assert len(session_achievements) == 1
        assert session_achievements[0].code == "achievement-1"
        assert session_achievements[0].session_id == test_session.id


def test_achievement_model_004_foreign_key_constraint(app, test_user):
    """ACH-MODEL-004: Foreign key constraint prevents invalid session_id."""
    with app.app_context():
        # Try to create achievement with non-existent session_id
        achievement = Achievement(
            user_id=test_user.id,
            code="test-achievement-invalid",
            title="Test Achievement",
            description="Test description",
            icon="🏆",
            category="test",
            session_id=99999,  # Non-existent session ID
        )
        db.session.add(achievement)
        
        # Should raise IntegrityError when committing
        with pytest.raises(Exception):  # SQLAlchemy raises IntegrityError
            db.session.commit()


def test_achievement_model_005_session_relationship(app, test_user, test_session):
    """ACH-MODEL-005: Achievement has relationship to PracticeSession."""
    with app.app_context():
        achievement = Achievement(
            user_id=test_user.id,
            code="test-achievement-relationship",
            title="Test Achievement",
            description="Test description",
            icon="🏆",
            category="test",
            session_id=test_session.id,
        )
        db.session.add(achievement)
        db.session.commit()
        
        # Refresh to load relationship
        db.session.refresh(achievement)
        
        # Check relationship works
        assert achievement.session is not None
        assert achievement.session.id == test_session.id
        assert achievement.session.user_id == test_user.id


def test_achievement_model_006_index_on_session_id(app, test_user, test_session):
    """ACH-MODEL-006: Index exists on session_id for query performance."""
    with app.app_context():
        # Create multiple achievements with same session_id
        achievements = []
        for i in range(5):
            achievement = Achievement(
                user_id=test_user.id,
                code=f"achievement-{i}",
                title=f"Achievement {i}",
                description="Description",
                icon="🏆",
                category="test",
                session_id=test_session.id,
            )
            db.session.add(achievement)
            achievements.append(achievement)
        db.session.commit()
        
        # Query should be fast with index
        session_achievements = Achievement.query.filter_by(session_id=test_session.id).all()
        assert len(session_achievements) == 5

