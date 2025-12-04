"""Backend tests for AchievementService session tracking functionality.

Tests verify that achievements can be created with session_id and that
session-specific achievement methods correctly pass session_id.
"""

import pytest
from datetime import datetime

from app import create_app, db
from app.models import User, Achievement, PracticeSession
from app.services.achievement_service import AchievementService


@pytest.fixture
def app():
    """Create test Flask application."""
    app = create_app(test_config={'TESTING': True})
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def test_user_id(app):
    """Create a test user and return ID."""
    with app.app_context():
        user = User(display_name="TestUser", pin="1234", avatar="🐯", level=1)
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def test_session_id(app, test_user_id):
    """Create a test practice session and return ID."""
    with app.app_context():
        session = PracticeSession(
            user_id=test_user_id,
            mode="standard",
            level=1,
            is_test=True,
            test_type="addition_1digit",
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            total_questions=30,
            correct_count=30,
            accuracy=100.0,
            total_duration_ms=60000,  # 2 seconds per question
        )
        db.session.add(session)
        db.session.commit()
        return session.id


def test_achievement_service_001_create_achievement_without_session_id(app, test_user_id):
    """ACH-SVC-001: create_achievement() accepts session_id=None (optional parameter)."""
    with app.app_context():
        achievement = AchievementService.create_achievement(
            user_id=test_user_id,
            code="test-achievement-no-session",
            title="Test Achievement",
            description="Test description",
            icon="🏆",
            category="test",
            session_id=None,
        )
        
        assert achievement.id is not None
        assert achievement.session_id is None
        assert achievement.code == "test-achievement-no-session"


def test_achievement_service_002_create_achievement_with_session_id(app, test_user_id, test_session_id):
    """ACH-SVC-002: create_achievement() stores session_id correctly."""
    with app.app_context():
        achievement = AchievementService.create_achievement(
            user_id=test_user_id,
            code="test-achievement-with-session",
            title="Test Achievement",
            description="Test description",
            icon="🏆",
            category="test",
            session_id=test_session_id,
        )
        
        assert achievement.id is not None
        assert achievement.session_id == test_session_id
        assert achievement.code == "test-achievement-with-session"
        
        # Verify it's persisted
        db.session.refresh(achievement)
        assert achievement.session_id == test_session_id


def test_achievement_service_003_check_test_tier_achievements_passes_session_id(app, test_user_id, test_session_id):
    """ACH-SVC-003: check_test_tier_achievements() passes session.id to create_achievement()."""
    with app.app_context():
        test_session = db.session.get(PracticeSession, test_session_id)
        # Call check_test_tier_achievements with a completed test session
        # This should award a tier achievement (Rank B for 30 questions, 100% accuracy)
        achievements = AchievementService.check_test_tier_achievements(test_session)
        
        # Should have awarded at least one achievement
        assert len(achievements) > 0
        
        # Check that the achievement has session_id set
        achievement = achievements[0]
        assert achievement.session_id == test_session.id
        assert achievement.user_id == test_user_id
        
        # Verify it's persisted
        db.session.refresh(achievement)
        assert achievement.session_id == test_session.id


def test_achievement_service_004_query_achievements_by_session(app, test_user_id, test_session_id):
    """ACH-SVC-004: Achievements created with session_id can be queried by session."""
    with app.app_context():
        # Create achievements with and without session_id
        achievement1 = AchievementService.create_achievement(
            user_id=test_user_id,
            code="achievement-with-session",
            title="Achievement with Session",
            description="Description",
            icon="🏆",
            category="test",
            session_id=test_session_id,
        )
        achievement2 = AchievementService.create_achievement(
            user_id=test_user_id,
            code="achievement-without-session",
            title="Achievement without Session",
            description="Description",
            icon="🏆",
            category="test",
            session_id=None,
        )
        
        # Query achievements by session_id
        session_achievements = Achievement.query.filter_by(session_id=test_session_id).all()
        
        assert len(session_achievements) == 1
        assert session_achievements[0].id == achievement1.id
        assert session_achievements[0].session_id == test_session_id


def test_achievement_service_005_serialize_achievement_includes_session_id(app, test_user_id, test_session_id):
    """ACH-SVC-005: serialize_achievement() includes sessionId in response."""
    with app.app_context():
        achievement = AchievementService.create_achievement(
            user_id=test_user_id,
            code="test-serialization",
            title="Test Achievement",
            description="Test description",
            icon="🏆",
            category="test",
            session_id=test_session_id,
        )
        
        serialized = AchievementService.serialize_achievement(achievement)
        
        assert "sessionId" in serialized
        assert serialized["sessionId"] == test_session_id
        assert serialized["code"] == "test-serialization"


def test_achievement_service_006_serialize_achievement_without_session_id(app, test_user_id):
    """ACH-SVC-006: serialize_achievement() returns None for sessionId when not set."""
    with app.app_context():
        achievement = AchievementService.create_achievement(
            user_id=test_user_id,
            code="test-serialization-no-session",
            title="Test Achievement",
            description="Test description",
            icon="🏆",
            category="test",
            session_id=None,
        )
        
        serialized = AchievementService.serialize_achievement(achievement)
        
        assert "sessionId" in serialized
        assert serialized["sessionId"] is None
        assert serialized["code"] == "test-serialization-no-session"


def test_achievement_service_007_test_tier_achievement_rank_b(app, test_user_id):
    """ACH-SVC-007: Test tier achievement (Rank B) is created with session_id."""
    with app.app_context():
        # Create a test session that qualifies for Rank B
        session = PracticeSession(
            user_id=test_user_id,
            mode="standard",
            level=1,
            is_test=True,
            test_type="addition_1digit",
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            total_questions=30,
            correct_count=25,  # Not 100% accuracy
            accuracy=83.33,
            total_duration_ms=90000,
        )
        db.session.add(session)
        db.session.commit()
        
        # Need to refresh/merge if accessing relationships, but here we pass object directly
        # However, db.session.commit() expires it.
        # Reload to be safe against detached errors
        session_id = session.id
        session = db.session.get(PracticeSession, session_id)
        
        achievements = AchievementService.check_test_tier_achievements(session)
        
        # Should award Rank B achievement
        assert len(achievements) == 1
        achievement = achievements[0]
        assert achievement.session_id == session.id
        assert achievement.code.endswith("-b")
        assert "addition-1digit" in achievement.code


def test_achievement_service_008_test_tier_achievement_rank_a(app, test_user_id):
    """ACH-SVC-008: Test tier achievement (Rank A) is created with session_id."""
    with app.app_context():
        # Create a test session that qualifies for Rank A (100% accuracy, <30 questions)
        session = PracticeSession(
            user_id=test_user_id,
            mode="standard",
            level=1,
            is_test=True,
            test_type="addition_1digit",
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            total_questions=25,
            correct_count=25,
            accuracy=100.0,
            total_duration_ms=50000,
        )
        db.session.add(session)
        db.session.commit()
        
        # Reload
        session_id = session.id
        session = db.session.get(PracticeSession, session_id)
        
        achievements = AchievementService.check_test_tier_achievements(session)
        
        # Should award Rank SS achievement (since 25 < 90 and 100% accuracy)
        assert len(achievements) == 1
        achievement = achievements[0]
        assert achievement.session_id == session.id
        assert achievement.code.endswith("-ss") or achievement.code.endswith("-a")
        assert "addition-1digit" in achievement.code

