"""Tests for LevelGrandmasterChecker."""

import json
import pytest
from app.models import Achievement, Question, Response, User
from app.services.achievements.achievement_checkers.level_grandmaster_checker import LevelGrandmasterChecker
from app.services.level_config_service import LevelConfigService
from app.config.concepts_config import CONCEPTS_CONFIG


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
        
        # User does not have math-master-bronze achievements with metadata
        # (may have old global achievement, but that doesn't count)
        result = level_grandmaster_checker.check(test_user)
        
        # Should not award Level Grandmaster
        assert len(result) == 0


def test_check_awards_when_all_levels_qualified(app, test_user, level_grandmaster_checker):
    """Test that Level Grandmaster is awarded when user has Level Master (Bronze) at all descriptive concepts.
    
    This test verifies that Level Grandmaster checks for existing Level Master achievements
    with metadata, not recalculating consecutive counts.
    """
    with app.app_context():
        from app import db
        from app.services.achievements.achievement_utils import create_achievement
        
        # Get all descriptive concepts (not c_concept_###)
        descriptive_concepts = [
            concept_id for concept_id in CONCEPTS_CONFIG.keys()
            if not concept_id.startswith("c_concept_")
        ]
        
        # Create Level Master (Bronze) achievements with metadata for ALL descriptive concepts
        for concept_id in descriptive_concepts:
            metadata = {"concept_id": concept_id}
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
        
        # Should award math-grandmaster (all descriptive concepts have Level Master Bronze)
        assert len(result) == 1, "Should award math-grandmaster when all descriptive concepts have Level Master (Bronze)"
        assert result[0].code == "math-grandmaster", "Should award math-grandmaster achievement"


def test_check_does_not_award_if_level_missing_consecutive(app, test_user, level_grandmaster_checker):
    """Test that Level Grandmaster is not awarded if any descriptive concept lacks Level Master (Bronze) achievement."""
    with app.app_context():
        from app import db
        from app.services.achievements.achievement_utils import create_achievement
        
        # Get all descriptive concepts (not c_concept_###)
        descriptive_concepts = [
            concept_id for concept_id in CONCEPTS_CONFIG.keys()
            if not concept_id.startswith("c_concept_")
        ]
        
        if len(descriptive_concepts) < 2:
            pytest.skip("Need at least 2 descriptive concepts for this test")
        
        # Create Level Master (Bronze) achievements with metadata for all but one concept
        missing_concept = descriptive_concepts[-1]  # Use the last concept as the missing one
        
        for concept_id in descriptive_concepts:
            if concept_id != missing_concept:
                metadata = {"concept_id": concept_id}
                create_achievement(
                    user_id=test_user.id,
                    code="math-master-bronze",
                    title="Level Master (Bronze)",
                    description="30 consecutive correct at concept",
                    icon="🏆",
                    category="accuracy",
                    metadata=metadata,
                )
        
        db.session.commit()
        
        # Check Level Grandmaster
        result = level_grandmaster_checker.check(test_user)
        
        # Should not award math-grandmaster (one concept is missing Level Master achievement)
        assert len(result) == 0, "Should not award math-grandmaster when one descriptive concept lacks Level Master (Bronze) achievement"


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
        from app.services.achievements.achievement_utils import create_achievement
        
        # Get all descriptive concepts (not c_concept_###)
        descriptive_concepts = sorted([
            concept_id for concept_id in CONCEPTS_CONFIG.keys()
            if not concept_id.startswith("c_concept_")
        ])
        
        # Create Level Master achievements for all descriptive concepts
        # Mix: Bronze for most concepts, Silver for first concept, Gold for second concept
        for idx, concept_id in enumerate(descriptive_concepts):
            if idx == 0:
                # First concept: Silver (higher tier qualifies)
                metadata = {"concept_id": concept_id}
                create_achievement(
                    user_id=test_user.id,
                    code="math-master-silver",
                    title="Math Master (Silver)",
                    description="60 consecutive correct",
                    icon="🏆",
                    category="accuracy",
                    metadata=metadata,
                )
            elif idx == 1:
                # Second concept: Gold (higher tier qualifies)
                metadata = {"concept_id": concept_id}
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
                # Other concepts: Bronze
                metadata = {"concept_id": concept_id}
                create_achievement(
                    user_id=test_user.id,
                    code="math-master-bronze",
                    title="Level Master (Bronze)",
                    description="30 consecutive correct at concept",
                    icon="🏆",
                    category="accuracy",
                    metadata=metadata,
                )
        
        db.session.commit()
        
        # Check Level Grandmaster
        result = level_grandmaster_checker.check(test_user)
        
        # Should award math-grandmaster (all descriptive concepts have Level Master Bronze or higher)
        assert len(result) == 1, "Should award math-grandmaster when all descriptive concepts have Level Master (Bronze or higher)"
        assert result[0].code == "math-grandmaster", "Should award math-grandmaster achievement"


def test_math_grandmaster_not_awarded_when_missing_one_concept(app, test_user, level_grandmaster_checker):
    """Test that Math Grandmaster is NOT awarded when one descriptive concept is missing Math Master achievement."""
    with app.app_context():
        from app import db
        from app.services.achievements.achievement_utils import create_achievement
        
        # Get all descriptive concepts (not c_concept_###)
        descriptive_concepts = sorted([
            concept_id for concept_id in CONCEPTS_CONFIG.keys()
            if not concept_id.startswith("c_concept_")
        ])
        
        if len(descriptive_concepts) < 2:
            pytest.skip("Need at least 2 descriptive concepts for this test")
        
        # Create math-master-bronze achievements for all descriptive concepts except one
        missing_concept = descriptive_concepts[-1]  # Use the last concept as the missing one
        
        for concept_id in descriptive_concepts:
            if concept_id != missing_concept:
                metadata = {"concept_id": concept_id}
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
        
        # Should NOT award math-grandmaster (one concept is missing)
        assert len(result) == 0, "Should NOT award math-grandmaster when one descriptive concept lacks Math Master achievement"
        
        # Now create achievement for the missing concept
        metadata = {"concept_id": missing_concept}
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
        
        # Check Level Grandmaster again
        result = level_grandmaster_checker.check(test_user)
        
        # Should NOW award math-grandmaster (all concepts have Math Master)
        assert len(result) == 1, "Should award math-grandmaster when all descriptive concepts have Math Master achievement"
        assert result[0].code == "math-grandmaster", "Should award math-grandmaster achievement"


def test_math_grandmaster_tier_substitution_explicit(app, test_user, level_grandmaster_checker):
    """Test that Math Grandmaster IS awarded when all concepts have Math Master, with mixed tiers (silver qualifies for bronze requirement)."""
    with app.app_context():
        from app import db
        from app.services.achievements.achievement_utils import create_achievement
        
        # Get all descriptive concepts (not c_concept_###)
        descriptive_concepts = sorted([
            concept_id for concept_id in CONCEPTS_CONFIG.keys()
            if not concept_id.startswith("c_concept_")
        ])
        
        if len(descriptive_concepts) < 2:
            pytest.skip("Need at least 2 descriptive concepts for this test")
        
        # Create math-master-silver for all descriptive concepts except one
        # Create math-master-bronze for the last concept
        last_concept = descriptive_concepts[-1]
        
        for concept_id in descriptive_concepts:
            if concept_id != last_concept:
                # Silver for most concepts (higher tier qualifies for bronze requirement)
                metadata = {"concept_id": concept_id}
                create_achievement(
                    user_id=test_user.id,
                    code="math-master-silver",
                    title="Math Master (Silver)",
                    description="60 consecutive correct",
                    icon="🏆",
                    category="accuracy",
                    metadata=metadata,
                )
            else:
                # Bronze for the last concept
                metadata = {"concept_id": concept_id}
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
        
        # Should award math-grandmaster (silver qualifies for bronze requirement)
        assert len(result) == 1, "Should award math-grandmaster when all descriptive concepts have Math Master (silver qualifies for bronze requirement)"
        assert result[0].code == "math-grandmaster", "Should award math-grandmaster achievement"

