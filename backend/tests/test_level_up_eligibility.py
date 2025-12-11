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

def get_level_requirements():
    """Get level requirements from actual config, converting to test format."""
    from app.config.level_progression_config import LEVEL_PROGRESSION_CONFIG
    
    requirements = []
    for level, reqs in LEVEL_PROGRESSION_CONFIG.items():
        # Convert config format to test format, preserving quantity and metadata
        req_list = []
        for req in reqs:
            code = req["achievement_code"]
            quantity = req.get("quantity", 1)
            metadata = req.get("metadata_filter")
            # Store as tuple: (code, quantity, metadata)
            req_list.append((code, quantity, metadata))
        requirements.append((level, req_list))
    return requirements


LEVEL_REQUIREMENTS = get_level_requirements()


@pytest.mark.parametrize("target_level,required_achievements", LEVEL_REQUIREMENTS)
def test_level_up_requires_achievements(app, test_user, target_level, required_achievements):
    """Test that level up requires all specified achievements for each level."""
    with app.app_context():
        from app.services.achievement_service import AchievementService
        
        # Refresh user to get latest state
        user = User.query.get(test_user.id)
        
        # User should not have achievements initially
        can_level, missing = UserService.can_level_up(user, target_level)
        assert can_level is False, f"Level {target_level} should require achievements"
        
        # Check that all required achievements are in missing list
        missing_str = " ".join(missing)
        for req_tuple in required_achievements:
            code, quantity, metadata = req_tuple
            # Check if code (or code with metadata) is in missing list
            if metadata:
                # Metadata achievements might be reported with metadata in the string
                assert code in missing_str or str(metadata) in missing_str, \
                    f"Missing achievement {code} with metadata {metadata} should be reported for level {target_level}"
            else:
                assert code in missing_str, \
                    f"Missing achievement {code} should be reported for level {target_level}"
        
        # Award all required achievements
        # Check existing achievements first to avoid duplicates
        # Track both code and (code, metadata) combinations since UNIQUE constraint is only on (user_id, code)
        # but we need to create multiple achievements with same code but different metadata
        existing_codes = AchievementService.get_achievement_codes(test_user.id)
        # Track (code, metadata) pairs we've created in this test
        created_achievements = set()  # Set of (code, metadata_json) tuples
        
        # Helper to calculate what achievements to create for quantity > 1 using tier substitution
        from app.utils.tier_utils import extract_base_code_and_tier, TIER_HIERARCHY, ALL_TIERS
        import json
        
        def create_achievements_for_quantity(base_code, target_tier, quantity, metadata=None):
            """Create achievements to satisfy quantity requirement using tier substitution.
            
            Note: UNIQUE constraint is on (user_id, code, achievement_metadata).
            This allows multiple achievements with same code but different metadata.
            """
            if quantity <= 1:
                # Single achievement needed
                code = f"{base_code}-{target_tier}" if target_tier else base_code
                metadata_json = json.dumps(metadata, sort_keys=True) if metadata else None
                achievement_key = (code, metadata_json)
                
                # Check if we've already created this exact (code, metadata) combination
                if achievement_key not in created_achievements:
                    # Check if achievement with this exact (code, metadata) already exists in DB
                    from app.models import Achievement
                    import json as json_lib
                    metadata_json_str = json_lib.dumps(metadata, sort_keys=True) if metadata else None
                    existing_ach = Achievement.query.filter_by(
                        user_id=test_user.id,
                        code=code
                    ).filter(
                        (Achievement.achievement_metadata == metadata_json_str) if metadata_json_str
                        else ((Achievement.achievement_metadata.is_(None)) | (Achievement.achievement_metadata == ""))
                    ).first()
                    
                    if existing_ach:
                        # Already exists with this exact metadata, skip
                        created_achievements.add(achievement_key)
                    else:
                        # Safe to create - UNIQUE constraint includes metadata, so we can have
                        # multiple achievements with same code but different metadata
                        try:
                            if metadata:
                                AchievementService.create_achievement(
                                    user_id=test_user.id,
                                    code=code,
                                    title=f"Test {code}",
                                    description="Test",
                                    icon="🏆",
                                    category="test",
                                    metadata=metadata,
                                )
                            else:
                                if code not in existing_codes:
                                    award_achievement_directly(test_user.id, code)
                                    existing_codes.add(code)
                            created_achievements.add(achievement_key)
                        except Exception as e:
                            # Catch any other errors
                            if "UNIQUE constraint" not in str(e) and "IntegrityError" not in str(type(e).__name__):
                                raise
                return
            
            # Need multiple achievements - use tier substitution
            # Calculate bronze units needed
            target_tier_value = TIER_HIERARCHY.get(target_tier.lower(), 1) if target_tier else 1
            bronze_units_per_target = 2 ** (target_tier_value - 1) if target_tier_value > 1 else 1
            total_bronze_needed = quantity * bronze_units_per_target
            
            # Create higher tier achievements to satisfy requirement
            # Start from highest tier and work down to minimize number of achievements created
            remaining_bronze = total_bronze_needed
            for tier in reversed(ALL_TIERS):
                if remaining_bronze <= 0:
                    break
                tier_value = TIER_HIERARCHY.get(tier.lower(), 1)
                bronze_per_tier = 2 ** (tier_value - 1) if tier_value > 1 else 1
                # Create as many of this tier as needed
                while bronze_per_tier <= remaining_bronze:
                    code = f"{base_code}-{tier}"
                    metadata_json = json.dumps(metadata, sort_keys=True) if metadata else None
                    achievement_key = (code, metadata_json)
                    
                    if achievement_key not in created_achievements:
                        # Check if achievement with this exact (code, metadata) already exists
                        from app.models import Achievement
                        import json as json_lib
                        metadata_json_str = json_lib.dumps(metadata, sort_keys=True) if metadata else None
                        existing_ach = Achievement.query.filter_by(
                            user_id=test_user.id,
                            code=code
                        ).filter(
                            (Achievement.achievement_metadata == metadata_json_str) if metadata_json_str
                            else ((Achievement.achievement_metadata.is_(None)) | (Achievement.achievement_metadata == ""))
                        ).first()
                        
                        if existing_ach:
                            # Already exists with this exact metadata, skip
                            created_achievements.add(achievement_key)
                        else:
                            # Safe to create - UNIQUE constraint includes metadata, so we can have
                            # multiple achievements with same code but different metadata
                            try:
                                if metadata:
                                    AchievementService.create_achievement(
                                        user_id=test_user.id,
                                        code=code,
                                        title=f"Test {code}",
                                        description="Test",
                                        icon="🏆",
                                        category="test",
                                        metadata=metadata,
                                    )
                                else:
                                    if code not in existing_codes:
                                        award_achievement_directly(test_user.id, code)
                                        existing_codes.add(code)
                                created_achievements.add(achievement_key)
                            except Exception as e:
                                if "UNIQUE constraint" not in str(e) and "IntegrityError" not in str(type(e).__name__):
                                    raise
                    remaining_bronze -= bronze_per_tier
                    # Only create one of each (code, metadata) combination
                    # Move to next lower tier
                    break
        
        for req_tuple in required_achievements:
            code, quantity, metadata = req_tuple
            # Extract base code and tier
            base_code, tier = extract_base_code_and_tier(code)
            create_achievements_for_quantity(base_code, tier, quantity, metadata)
        
        # Commit to ensure achievements are persisted
        db.session.commit()
        
        # Refresh user to get updated achievements
        db.session.refresh(user)
        user = User.query.get(test_user.id)
        
        # User should now be able to level up
        can_level, missing = UserService.can_level_up(user, target_level)
        if not can_level:
            # Debug: show what's missing
            missing_str = "; ".join(missing)
            assert can_level is True, f"Level {target_level} should be unlockable after awarding achievements. Missing: {missing_str}"
        assert len(missing) == 0, f"No missing achievements should be reported for level {target_level}. Missing: {missing}"


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
        from app.services.achievement_service import AchievementService
        
        # Award all required achievements for level 2:
        # 1. first-steps
        # 2. first-victory
        # 3. accuracy-ace-platinum with test_type: addition-1digit
        award_achievement_directly(test_user.id, "first-steps")
        award_achievement_directly(test_user.id, "first-victory")
        AchievementService.create_achievement(
            user_id=test_user.id,
            code="accuracy-ace-platinum",
            title="Test Accuracy Ace Platinum",
            description="Test",
            icon="🎯",
            category="accuracy",
            metadata={"test_type": "addition-1digit"},
        )
        
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
    """LVL-UP-006: Level 5 requires multiple achievements (accuracy-ace-platinum with test_type AND question-master-silver)."""
    with app.app_context():
        from app.services.achievement_service import AchievementService
        
        user = User.query.get(test_user.id)
        
        # Check without any achievements
        can_level, missing = UserService.can_level_up(user, 5)
        assert can_level is False
        assert len(missing) == 2  # Both required
        
        # Award only one achievement
        award_achievement_directly(test_user.id, "question-master-silver")
        db.session.refresh(user)
        user = User.query.get(test_user.id)
        
        can_level, missing = UserService.can_level_up(user, 5)
        assert can_level is False
        assert len(missing) == 1  # Still missing accuracy-ace-platinum with test_type metadata
        
        # Award the second achievement with metadata
        AchievementService.create_achievement(
            user_id=test_user.id,
            code="accuracy-ace-platinum",
            title="Test Accuracy Ace Platinum",
            description="Test",
            icon="🎯",
            category="accuracy",
            metadata={"test_type": "subtraction-1digit-zeros"},
        )
        db.session.refresh(user)
        user = User.query.get(test_user.id)
        
        can_level, missing = UserService.can_level_up(user, 5)
        assert can_level is True
        assert len(missing) == 0

