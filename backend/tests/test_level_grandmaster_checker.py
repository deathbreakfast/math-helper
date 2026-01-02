"""Tests for LevelGrandmasterChecker."""

import json
import pytest
from app.models import Achievement, Question, Response, User
from app.services.achievements.achievement_checkers.level_grandmaster_checker import LevelGrandmasterChecker
from app.services.level_config_service import LevelConfigService


@pytest.fixture
def achievement_configs():
    """Get achievement configs for testing."""
    return LevelConfigService.get_all_achievement_configs()


@pytest.fixture
def level_grandmaster_checker(achievement_configs):
    """Create a LevelGrandmasterChecker instance."""
    return LevelGrandmasterChecker(achievement_configs)


def test_check_requires_level_master_bronze_first(app, test_user, level_grandmaster_checker):
    """Test that Level Master (Bronze) with metadata is required before Level Grandmaster."""
    with app.app_context():
        from app import db
        from app.config.levels_config import LEVELS_CONFIG
        
        # User does not have math-master-bronze achievements with metadata
        # (may have old global achievement, but that doesn't count)
        result = level_grandmaster_checker.check(test_user)
        
        # Should not award Level Grandmaster
        assert len(result) == 0


def test_check_awards_when_all_levels_qualified(app, test_user, level_grandmaster_checker):
    """Test that Level Grandmaster is awarded when user has Level Master (Bronze) at all levels.
    
    This test verifies that Level Grandmaster checks for existing Level Master achievements
    with metadata, not recalculating consecutive counts.
    """
    with app.app_context():
        from app import db
        from app.config.levels_config import LEVELS_CONFIG
        from app.services.achievements.achievement_utils import create_achievement
        
        # Create Level Master (Bronze) achievements with metadata for ALL levels
        all_levels = sorted(LEVELS_CONFIG.keys())
        for level in all_levels:
            metadata = {"concept_id": f"c_concept_{level:03d}"}
            create_achievement(
                user_id=test_user.id,
                code="math-master-bronze",
                title="Math Master (Bronze)",
                description="30 consecutive correct",
                icon="🏆",
                category="accuracy",
                metadata=metadata,
            )
        
        db.session.commit()
        
        # Check Level Grandmaster
        result = level_grandmaster_checker.check(test_user)
        
        # Should award math-grandmaster (all levels have Level Master Bronze)
        assert len(result) == 1, "Should award math-grandmaster when all levels have Level Master (Bronze)"
        assert result[0].code == "math-grandmaster", "Should award math-grandmaster achievement"


def test_check_does_not_award_if_level_missing_consecutive(app, test_user, level_grandmaster_checker):
    """Test that Level Grandmaster is not awarded if any level lacks Level Master (Bronze) achievement."""
    with app.app_context():
        from app import db
        from app.config.levels_config import LEVELS_CONFIG
        from app.services.achievements.achievement_utils import create_achievement
        
        # Use a small subset of levels for testing (levels 1-3)
        test_levels = sorted(LEVELS_CONFIG.keys())[:3]
        
        if len(test_levels) < 2:
            pytest.skip("Need at least 2 levels for this test")
        
        # Create Level Master (Bronze) achievements with metadata for all but one level
        all_levels = sorted(LEVELS_CONFIG.keys())
        missing_level = all_levels[-1]  # Use the last level as the missing one
        
        for level in all_levels:
            if level != missing_level:
                metadata = {"concept_id": f"c_concept_{level:03d}"}
                create_achievement(
                    user_id=test_user.id,
                    code="math-master-bronze",
                    title="Level Master (Bronze)",
                    description="30 consecutive correct at level",
                    icon="🏆",
                    category="accuracy",
                    metadata=metadata,
                )
        
        db.session.commit()
        
        # Check Level Grandmaster
        result = level_grandmaster_checker.check(test_user)
        
        # Should not award math-grandmaster (one level is missing Level Master achievement)
        assert len(result) == 0, "Should not award math-grandmaster when one level lacks Level Master (Bronze) achievement"


def test_check_does_not_duplicate_achievement(app, test_user, level_grandmaster_checker):
    """Test that Level Grandmaster is not awarded twice."""
    with app.app_context():
        from app import db
        
        # User already has math-grandmaster
        existing = Achievement(
            user_id=test_user.id,
            code="math-grandmaster",
            title="Math Grandmaster",
            description="Math Master Bronze on all descriptive concepts",
            icon="👑",
            category="milestone",
        )
        db.session.add(existing)
        db.session.commit()
        
        result = level_grandmaster_checker.check(test_user)
        
        # Should not award duplicate
        assert len(result) == 0
        assert Achievement.query.filter_by(user_id=test_user.id, code="math-grandmaster").count() == 1


def test_check_tier_substitution(app, test_user, level_grandmaster_checker):
    """Test that Level Grandmaster accepts higher tier Level Master achievements (Silver/Gold qualify for Bronze requirement)."""
    with app.app_context():
        from app import db
        from app.config.levels_config import LEVELS_CONFIG
        from app.services.achievements.achievement_utils import create_achievement
        
        all_levels = sorted(LEVELS_CONFIG.keys())
        
        # Create Level Master achievements for all levels
        # Mix: Bronze for most levels, Silver for level 1, Gold for level 2
        for level in all_levels:
            if level == 1:
                # Level 1: Silver (higher tier qualifies)
                metadata = {"concept_id": f"c_concept_{level:03d}"}
                create_achievement(
                    user_id=test_user.id,
                    code="math-master-silver",
                    title="Math Master (Silver)",
                    description="60 consecutive correct",
                    icon="🏆",
                    category="accuracy",
                    metadata=metadata,
                )
            elif level == 2:
                # Level 2: Gold (higher tier qualifies)
                metadata = {"concept_id": f"c_concept_{level:03d}"}
                create_achievement(
                    user_id=test_user.id,
                    code="math-master-gold",
                    title="Math Master (Gold)",
                    description="120 consecutive correct",
                    icon="🏆",
                    category="accuracy",
                    metadata=metadata,
                )
            else:
                # Other levels: Bronze
                metadata = {"concept_id": f"c_concept_{level:03d}"}
                create_achievement(
                    user_id=test_user.id,
                    code="math-master-bronze",
                    title="Level Master (Bronze)",
                    description="30 consecutive correct at level",
                    icon="🏆",
                    category="accuracy",
                    metadata=metadata,
                )
        
        db.session.commit()
        
        # Check Level Grandmaster
        result = level_grandmaster_checker.check(test_user)
        
        # Should award math-grandmaster (all levels have Level Master Bronze or higher)
        assert len(result) == 1, "Should award math-grandmaster when all levels have Level Master (Bronze or higher)"
        assert result[0].code == "math-grandmaster", "Should award math-grandmaster achievement"

