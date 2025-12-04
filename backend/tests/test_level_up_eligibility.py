"""Backend tests for level up eligibility validation.

Tests verify that level up requirements are correctly checked for all levels 2-45.
"""

import pytest

from app import create_app, db
from app.models import User
from app.services.user_service import UserService
from tests.helpers.data_helpers import award_achievement_directly, set_user_level_directly


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
        # Access id to ensure it's loaded before returning (prevents DetachedInstanceError)
        _ = user.id
        return user


# ============================================================================
# Level Up Eligibility Tests - Parameterized for all levels
# ============================================================================

# Level requirements from level_progression_config.py
LEVEL_REQUIREMENTS = [
    (2, ["addition-1digit-bronze"]),
    (3, ["addition-1digit-bronze"]),
    (4, ["subtraction-1digit-bronze"]),
    (5, ["perfect-streak-bronze", "addition-1digit-bronze"]),
    (6, ["subtraction-1digit-bronze"]),
    (7, ["addition-2digit-bronze"]),
    (8, ["subtraction-2digit-bronze"]),
    (9, ["multiplication-by-1-bronze"]),
    (10, ["multiplication-by-2-silver"]),
    (11, ["multiplication-by-3-silver"]),
    (12, ["multiplication-by-4-silver"]),
    (13, ["multiplication-by-5-silver"]),
    (14, ["multiplication-by-6-silver"]),
    (15, ["multiplication-by-7-silver"]),
    (16, ["multiplication-by-8-silver"]),
    (17, ["multiplication-by-9-silver"]),
    (18, ["multiplication-by-2-silver"]),
    (19, ["multiplication-by-10-silver"]),
    (20, ["multiplication-by-11-silver"]),
    (21, ["multiplication-by-12-silver"]),
    (22, ["addition-3digit-bronze"]),
    (23, ["subtraction-3digit-bronze"]),
    (24, ["multiplication-2digit-bronze"]),
    (25, ["multiplication-2digit-bronze"]),
    (26, ["multiplication-2digit-gold", "addition-2digit-gold", "subtraction-2digit-gold"]),
    (27, ["division-by-2-silver"]),
    (28, ["division-by-3-silver"]),
    (29, ["division-by-4-silver"]),
    (30, ["division-by-5-silver"]),
    (31, ["division-by-6-silver"]),
    (32, ["division-by-7-silver"]),
    (33, ["division-by-8-silver"]),
    (34, ["division-by-9-silver"]),
    (35, ["division-by-10-silver"]),
    (36, ["division-by-11-silver"]),
    (37, ["division-by-12-silver"]),
    (38, ["division-2digit-bronze"]),
    (39, ["division-2digit-bronze"]),
    (40, ["division-2digit-bronze"]),
    (41, ["division-2digit-bronze"]),
    (42, ["multiplication-3digit-bronze"]),
    (43, ["division-3digit-bronze"]),
    (44, ["division-3digit-bronze"]),
    (45, ["division-3digit-bronze"]),
]


@pytest.mark.parametrize("target_level,required_achievements", LEVEL_REQUIREMENTS)
def test_level_up_requires_achievements(app, test_user, target_level, required_achievements):
    """Test that level up requires all specified achievements for each level."""
    with app.app_context():
        # Refresh user to get latest state
        user = User.query.get(test_user.id)
        
        # User should not have achievements initially
        can_level, missing = UserService.can_level_up(user, target_level)
        assert can_level is False, f"Level {target_level} should require achievements"
        
        # Check that all required achievements are in missing list
        missing_codes = [m.split(" (")[0] for m in missing]  # Extract code from "code (need X, have Y)"
        for req_code in required_achievements:
            assert req_code in missing_codes, f"Missing achievement {req_code} should be reported for level {target_level}"
        
        # Award all required achievements
        for achievement_code in required_achievements:
            award_achievement_directly(test_user.id, achievement_code)
        
        # Refresh user to get updated achievements
        db.session.refresh(user)
        user = User.query.get(test_user.id)
        
        # User should now be able to level up
        can_level, missing = UserService.can_level_up(user, target_level)
        assert can_level is True, f"Level {target_level} should be unlockable after awarding achievements"
        assert len(missing) == 0, f"No missing achievements should be reported for level {target_level}"


def test_level_up_cannot_go_backwards(app, test_user):
    """LVL-UP-001: User cannot level up to a level lower than current level."""
    with app.app_context():
        # Set user to level 5
        set_user_level_directly(test_user.id, 5)
        user = User.query.get(test_user.id)
        
        # Try to level up to level 3 (lower than current)
        can_level, missing = UserService.can_level_up(user, 3)
        assert can_level is False
        assert "Target level must be greater than current level" in missing[0]


def test_level_up_same_level(app, test_user):
    """LVL-UP-002: User cannot level up to the same level."""
    with app.app_context():
        # User is at level 1
        user = User.query.get(test_user.id)
        
        # Try to level up to level 1 (same as current)
        can_level, missing = UserService.can_level_up(user, 1)
        assert can_level is False
        assert "Target level must be greater than current level" in missing[0]


def test_level_up_level_1_has_no_requirements(app, test_user):
    """LVL-UP-003: Level 1 has no requirements (users start at level 1)."""
    with app.app_context():
        # This is more of a documentation test - users start at level 1
        user = User.query.get(test_user.id)
        assert user.level == 1


def test_level_up_api_endpoint_success(app, test_user):
    """LVL-UP-004: Level up API endpoint succeeds when eligible."""
    with app.app_context():
        # Award required achievement for level 2
        award_achievement_directly(test_user.id, "addition-1digit-bronze")
        
        user = User.query.get(test_user.id)
        
        # Use level_up service method (simulates API endpoint)
        success, errors = UserService.level_up(user, 2)
        
        assert success is True
        assert len(errors) == 0
        
        # Verify level increased
        db.session.refresh(user)
        assert user.level == 2


def test_level_up_api_endpoint_failure(app, test_user):
    """LVL-UP-005: Level up API endpoint fails when not eligible."""
    with app.app_context():
        user = User.query.get(test_user.id)
        
        # Try to level up without required achievements
        success, errors = UserService.level_up(user, 2)
        
        assert success is False
        assert len(errors) > 0
        assert "Missing required achievements" in errors[0]
        
        # Verify level did not increase
        db.session.refresh(user)
        assert user.level == 1


def test_level_up_multiple_requirements(app, test_user):
    """LVL-UP-006: Level 5 requires multiple achievements (perfect-streak-bronze AND addition-1digit-bronze)."""
    with app.app_context():
        user = User.query.get(test_user.id)
        
        # Check without any achievements
        can_level, missing = UserService.can_level_up(user, 5)
        assert can_level is False
        assert len(missing) == 2  # Both required
        
        # Award only one achievement
        award_achievement_directly(test_user.id, "addition-1digit-bronze")
        db.session.refresh(user)
        user = User.query.get(test_user.id)
        
        can_level, missing = UserService.can_level_up(user, 5)
        assert can_level is False
        assert len(missing) == 1  # Still missing perfect-streak-bronze
        
        # Award the second achievement
        award_achievement_directly(test_user.id, "perfect-streak-bronze")
        db.session.refresh(user)
        user = User.query.get(test_user.id)
        
        can_level, missing = UserService.can_level_up(user, 5)
        assert can_level is True
        assert len(missing) == 0

