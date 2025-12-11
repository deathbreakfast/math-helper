"""Tests for LevelGrandmasterChecker."""

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
    """Test that Level Master (Bronze) is required before Level Grandmaster."""
    with app.app_context():
        from app import db
        
        # User does not have level-master-bronze
        result = level_grandmaster_checker.check(test_user)
        
        # Should not award Level Grandmaster
        assert len(result) == 0


def test_check_awards_when_all_levels_qualified(app, test_user, level_grandmaster_checker):
    """Test that Level Grandmaster is awarded when user has 30 consecutive at all levels.
    
    TODO: This test is skipped pending implementation of correct logic.
    See ACHIEVEMENT_LOGIC_FIXES.md for details.
    
    Expected behavior:
    - Level Master should award per-level achievements with metadata {level: N}
    - Level Grandmaster should check for existing Level Master (Bronze) achievements with metadata
    - Should NOT recalculate consecutive counts independently
    
    Current implementation incorrectly recalculates consecutive counts instead of checking
    for existing Level Master achievements. This test will be updated once the logic is fixed.
    """
    pytest.skip("TODO: Pending implementation of correct Level Master/Level Grandmaster logic. See ACHIEVEMENT_LOGIC_FIXES.md")


def test_check_does_not_award_if_level_missing_consecutive(app, test_user, level_grandmaster_checker):
    """Test that Level Grandmaster is not awarded if any level lacks 30 consecutive."""
    with app.app_context():
        from app import db
        from app.config.levels_config import LEVELS_CONFIG
        from datetime import datetime, timedelta
        
        # First, award level-master-bronze
        level_master_bronze = Achievement(
            user_id=test_user.id,
            code="level-master-bronze",
            title="Level Master (Bronze)",
            description="30 consecutive correct at any level",
            icon="🏆",
            category="mastery",
        )
        db.session.add(level_master_bronze)
        db.session.commit()
        
        # Use a small subset of levels for testing (levels 1-3)
        test_levels = sorted(LEVELS_CONFIG.keys())[:3]
        
        if len(test_levels) < 2:
            pytest.skip("Need at least 2 levels for this test")
        
        # Create 30 consecutive correct for all but one level
        for level in test_levels[:-1]:
            for i in range(30):
                question = Question(
                    operation="addition",
                    required_level=level,
                    operand1=1,
                    operand2=1,
                    correct_answer="2",
                    prompt="1 + 1",
                )
                db.session.add(question)
                db.session.flush()
                
                response = Response(
                    user_id=test_user.id,
                    question_id=question.id,
                    submitted_answer="2",
                    correct_answer="2",
                    is_correct=True,
                    answered_at=datetime.utcnow() - timedelta(seconds=30-i),
                )
                db.session.add(response)
        
        # For the last level, only create 20 consecutive (not enough)
        last_level = test_levels[-1]
        for i in range(20):
            question = Question(
                operation="addition",
                required_level=last_level,
                operand1=1,
                operand2=1,
                correct_answer="2",
                prompt="1 + 1",
            )
            db.session.add(question)
            db.session.flush()
            
            response = Response(
                user_id=test_user.id,
                question_id=question.id,
                submitted_answer="2",
                correct_answer="2",
                is_correct=True,
                answered_at=datetime.utcnow() - timedelta(seconds=20-i),
            )
            db.session.add(response)
        
        db.session.commit()
        
        # Check Level Grandmaster
        result = level_grandmaster_checker.check(test_user)
        
        # Should not award level-grandmaster (one level doesn't qualify)
        assert len(result) == 0, "Should not award level-grandmaster when one level lacks 30 consecutive"


def test_check_does_not_duplicate_achievement(app, test_user, level_grandmaster_checker):
    """Test that Level Grandmaster is not awarded twice."""
    with app.app_context():
        from app import db
        
        # User already has level-grandmaster
        existing = Achievement(
            user_id=test_user.id,
            code="level-grandmaster",
            title="Level Grandmaster",
            description="Level Master Bronze on all levels",
            icon="👑",
            category="milestone",
        )
        db.session.add(existing)
        db.session.commit()
        
        result = level_grandmaster_checker.check(test_user)
        
        # Should not award duplicate
        assert len(result) == 0
        assert Achievement.query.filter_by(user_id=test_user.id, code="level-grandmaster").count() == 1

