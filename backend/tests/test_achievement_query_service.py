"""Tests for achievement query service."""

import pytest
from datetime import datetime

from app import create_app, db
from app.models import Achievement, PracticeSession, Question, Response, User
from app.services.achievements.achievement_queries.achievement_query_service import AchievementQueryService


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
        _ = user.id
        return user


@pytest.fixture
def test_user2(app):
    """Create a second test user."""
    with app.app_context():
        user = User(display_name="TestUser2", pin="5678", avatar="🐰", level=2)
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        _ = user.id
        return user


@pytest.fixture
def test_session(app, test_user):
    """Create a test practice session."""
    with app.app_context():
        user = db.session.merge(test_user)
        session = PracticeSession(
            user_id=user.id,
            mode="standard",
            level=1,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            total_questions=10,
            correct_count=10,
            accuracy=100.0,
            total_duration_ms=10000,
        )
        db.session.add(session)
        db.session.commit()
        db.session.refresh(session)
        return session


def test_get_user_achievements(app, test_user):
    """Test getting achievements for a user."""
    with app.app_context():
        user = db.session.merge(test_user)
        
        # Create some achievements
        achievement1 = Achievement(
            user_id=user.id,
            code="test-achievement-1",
            title="Test Achievement 1",
            description="Test",
            icon="🏆",
            category="test",
            earned_at=datetime.utcnow(),
        )
        achievement2 = Achievement(
            user_id=user.id,
            code="test-achievement-2",
            title="Test Achievement 2",
            description="Test",
            icon="🏆",
            category="test",
            earned_at=datetime.utcnow(),
        )
        db.session.add_all([achievement1, achievement2])
        db.session.commit()
        
        # Get achievements
        achievements = AchievementQueryService.get_user_achievements(user.id)
        
        assert len(achievements) == 2, "Should return 2 achievements"
        assert achievements[0].code in ["test-achievement-1", "test-achievement-2"]


def test_get_user_achievements_with_limit(app, test_user):
    """Test getting achievements for a user with limit."""
    with app.app_context():
        user = db.session.merge(test_user)
        
        # Create multiple achievements
        for i in range(5):
            achievement = Achievement(
                user_id=user.id,
                code=f"test-achievement-{i}",
                title=f"Test Achievement {i}",
                description="Test",
                icon="🏆",
                category="test",
                earned_at=datetime.utcnow(),
            )
            db.session.add(achievement)
        db.session.commit()
        
        # Get achievements with limit
        achievements = AchievementQueryService.get_user_achievements(user.id, limit=3)
        
        assert len(achievements) == 3, "Should return 3 achievements with limit"


def test_get_achievements_by_session(app, test_user, test_session):
    """Test getting achievements by session."""
    with app.app_context():
        user = db.session.merge(test_user)
        session = db.session.merge(test_session)
        
        # Create achievements linked to session
        achievement1 = Achievement(
            user_id=user.id,
            code="test-achievement-1",
            title="Test Achievement 1",
            description="Test",
            icon="🏆",
            category="test",
            session_id=session.id,
            earned_at=datetime.utcnow(),
        )
        achievement2 = Achievement(
            user_id=user.id,
            code="test-achievement-2",
            title="Test Achievement 2",
            description="Test",
            icon="🏆",
            category="test",
            session_id=session.id,
            earned_at=datetime.utcnow(),
        )
        db.session.add_all([achievement1, achievement2])
        db.session.commit()
        
        # Get achievements by session
        achievements = AchievementQueryService.get_achievements_by_session(session.id)
        
        assert len(achievements) == 2, "Should return 2 achievements for session"


def test_get_achievements_by_category(app, test_user):
    """Test getting achievements by category."""
    with app.app_context():
        user = db.session.merge(test_user)
        
        # Create achievements in different categories
        achievement1 = Achievement(
            user_id=user.id,
            code="test-achievement-1",
            title="Test Achievement 1",
            description="Test",
            icon="🏆",
            category="test",
            earned_at=datetime.utcnow(),
        )
        achievement2 = Achievement(
            user_id=user.id,
            code="practice-achievement-1",
            title="Practice Achievement 1",
            description="Test",
            icon="🏆",
            category="practice",
            earned_at=datetime.utcnow(),
        )
        db.session.add_all([achievement1, achievement2])
        db.session.commit()
        
        # Get achievements by category
        achievements = AchievementQueryService.get_achievements_by_category(
            user_id=user.id, category="test"
        )
        
        assert len(achievements) == 1, "Should return 1 achievement in test category"
        assert achievements[0].category == "test"


def test_get_achievements_by_category_all_users(app, test_user, test_user2):
    """Test getting achievements by category for all users."""
    with app.app_context():
        user1 = db.session.merge(test_user)
        user2 = db.session.merge(test_user2)
        
        # Create achievements for both users
        achievement1 = Achievement(
            user_id=user1.id,
            code="test-achievement-1",
            title="Test Achievement 1",
            description="Test",
            icon="🏆",
            category="test",
            earned_at=datetime.utcnow(),
        )
        achievement2 = Achievement(
            user_id=user2.id,
            code="test-achievement-2",
            title="Test Achievement 2",
            description="Test",
            icon="🏆",
            category="test",
            earned_at=datetime.utcnow(),
        )
        db.session.add_all([achievement1, achievement2])
        db.session.commit()
        
        # Get achievements by category for all users
        achievements = AchievementQueryService.get_achievements_by_category(
            user_id=None, category="test", include_user_name=True
        )
        
        assert len(achievements) == 2, "Should return 2 achievements for all users"
        assert all(a.category == "test" for a in achievements)


def test_get_achievement_codes(app, test_user):
    """Test getting achievement codes for a user."""
    with app.app_context():
        user = db.session.merge(test_user)
        
        # Create achievements
        achievement1 = Achievement(
            user_id=user.id,
            code="test-achievement-1",
            title="Test Achievement 1",
            description="Test",
            icon="🏆",
            category="test",
            earned_at=datetime.utcnow(),
        )
        achievement2 = Achievement(
            user_id=user.id,
            code="test-achievement-2",
            title="Test Achievement 2",
            description="Test",
            icon="🏆",
            category="test",
            earned_at=datetime.utcnow(),
        )
        db.session.add_all([achievement1, achievement2])
        db.session.commit()
        
        # Get achievement codes
        codes = AchievementQueryService.get_achievement_codes(user.id)
        
        assert len(codes) == 2, "Should return 2 achievement codes"
        assert "test-achievement-1" in codes
        assert "test-achievement-2" in codes


def test_count_achievements_by_code(app, test_user):
    """Test counting achievements by code."""
    with app.app_context():
        user = db.session.merge(test_user)
        
        # Create achievement (unique constraint prevents duplicates)
        achievement = Achievement(
            user_id=user.id,
            code="test-achievement",
            title="Test Achievement",
            description="Test",
            icon="🏆",
            category="test",
            earned_at=datetime.utcnow(),
        )
        db.session.add(achievement)
        db.session.commit()
        
        # Count achievements by code
        count = AchievementQueryService.count_achievements_by_code(user.id, "test-achievement")
        
        assert count == 1, "Should return count of 1 (unique constraint prevents duplicates)"
        
        # Count non-existent achievement
        count = AchievementQueryService.count_achievements_by_code(user.id, "non-existent")
        
        assert count == 0, "Should return count of 0 for non-existent achievement"


def test_count_achievements_by_code_with_filters_level(app, test_user, test_session):
    """Test counting achievements by code with level filter."""
    with app.app_context():
        user = db.session.merge(test_user)
        session = db.session.merge(test_session)
        
        # Create achievement linked to session
        achievement = Achievement(
            user_id=user.id,
            code="test-achievement",
            title="Test Achievement",
            description="Test",
            icon="🏆",
            category="test",
            session_id=session.id,
            earned_at=datetime.utcnow(),
        )
        db.session.add(achievement)
        db.session.commit()
        
        # Count with level filter (session is level 1)
        count = AchievementQueryService.count_achievements_by_code_with_filters(
            user.id, "test-achievement", level=1
        )
        
        assert count == 1, "Should return count of 1 for level 1"
        
        # Count with different level filter
        count = AchievementQueryService.count_achievements_by_code_with_filters(
            user.id, "test-achievement", level=2
        )
        
        assert count == 0, "Should return count of 0 for level 2"


def test_count_achievements_by_code_with_filters_accuracy(app, test_user, test_session):
    """Test counting achievements by code with accuracy filter."""
    with app.app_context():
        user = db.session.merge(test_user)
        session = db.session.merge(test_session)
        
        # Create achievement linked to session (100% accuracy)
        achievement = Achievement(
            user_id=user.id,
            code="test-achievement",
            title="Test Achievement",
            description="Test",
            icon="🏆",
            category="test",
            session_id=session.id,
            earned_at=datetime.utcnow(),
        )
        db.session.add(achievement)
        db.session.commit()
        
        # Count with accuracy filter (0.9 = 90%)
        count = AchievementQueryService.count_achievements_by_code_with_filters(
            user.id, "test-achievement", min_accuracy=0.9
        )
        
        assert count == 1, "Should return count of 1 for accuracy >= 90%"
        
        # Count with higher accuracy filter
        count = AchievementQueryService.count_achievements_by_code_with_filters(
            user.id, "test-achievement", min_accuracy=0.95
        )
        
        assert count == 1, "Should return count of 1 for accuracy >= 95%"

