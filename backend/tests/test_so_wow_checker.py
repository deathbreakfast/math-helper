"""Tests for SoWowChecker."""

import pytest
from app.models import Achievement, User
from app.services.achievements.achievement_checkers.so_wow_checker import SoWowChecker
from app.services.level_config_service import LevelConfigService


@pytest.fixture
def achievement_configs():
    """Get achievement configs for testing."""
    return LevelConfigService.get_all_achievement_configs()


@pytest.fixture
def so_wow_checker(achievement_configs):
    """Create a SoWowChecker instance."""
    return SoWowChecker(achievement_configs)


def test_check_awards_so_wow_for_first_tier_achievement(app, test_user, so_wow_checker):
    """Test that So, Wow! achievement is awarded when user earns first tier achievement."""
    with app.app_context():
        # User has no achievements yet
        assert Achievement.query.filter_by(user_id=test_user.id).count() == 0
        
        # Create a newly awarded bronze tier achievement
        new_achievement = Achievement(
            user_id=test_user.id,
            code="question-master-bronze",
            title="Question Master (Bronze)",
            description="Answered 100 questions",
            icon="🏆",
            category="milestone",
        )
        from app import db
        db.session.add(new_achievement)
        db.session.commit()
        
        # Check So, Wow! achievements
        result = so_wow_checker.check(test_user, [new_achievement])
        
        # Should award "so-wow-bronze"
        assert len(result) == 1
        assert result[0].code == "so-wow-bronze"
        assert Achievement.query.filter_by(user_id=test_user.id, code="so-wow-bronze").first() is not None


def test_check_does_not_award_if_user_already_has_tier_achievements(app, test_user, so_wow_checker):
    """Test that So, Wow! is not awarded if user already has achievements of that tier."""
    with app.app_context():
        from app import db
        
        # User already has a bronze tier achievement
        existing_achievement = Achievement(
            user_id=test_user.id,
            code="speed-demon-bronze",
            title="Speed Demon (Bronze)",
            description="Fast speed",
            icon="⚡",
            category="speed",
        )
        db.session.add(existing_achievement)
        db.session.commit()
        
        # Create a new bronze tier achievement
        new_achievement = Achievement(
            user_id=test_user.id,
            code="question-master-bronze",
            title="Question Master (Bronze)",
            description="Answered 100 questions",
            icon="🏆",
            category="milestone",
        )
        db.session.add(new_achievement)
        db.session.commit()
        
        # Check So, Wow! achievements
        result = so_wow_checker.check(test_user, [new_achievement])
        
        # Should NOT award "so-wow-bronze" since user already has bronze tier achievements
        assert len(result) == 0


def test_check_awards_multiple_tiers_in_one_session(app, test_user, so_wow_checker):
    """Test that multiple So, Wow! achievements can be awarded for different tiers."""
    with app.app_context():
        from app import db
        
        # User has no achievements yet
        assert Achievement.query.filter_by(user_id=test_user.id).count() == 0
        
        # Create newly awarded achievements for different tiers
        bronze_achievement = Achievement(
            user_id=test_user.id,
            code="question-master-bronze",
            title="Question Master (Bronze)",
            description="Answered 100 questions",
            icon="🏆",
            category="milestone",
        )
        silver_achievement = Achievement(
            user_id=test_user.id,
            code="speed-demon-silver",
            title="Speed Demon (Silver)",
            description="Faster speed",
            icon="⚡",
            category="speed",
        )
        db.session.add(bronze_achievement)
        db.session.add(silver_achievement)
        db.session.commit()
        
        # Check So, Wow! achievements
        result = so_wow_checker.check(test_user, [bronze_achievement, silver_achievement])
        
        # Should award both "so-wow-bronze" and "so-wow-silver"
        assert len(result) == 2
        codes = {ach.code for ach in result}
        assert "so-wow-bronze" in codes
        assert "so-wow-silver" in codes


def test_check_skips_non_tiered_achievements(app, test_user, so_wow_checker):
    """Test that non-tiered achievements are skipped."""
    with app.app_context():
        from app import db
        
        # Create a non-tiered achievement
        new_achievement = Achievement(
            user_id=test_user.id,
            code="first-steps",
            title="First Steps",
            description="Answered first question",
            icon="👣",
            category="milestone",
        )
        db.session.add(new_achievement)
        db.session.commit()
        
        # Check So, Wow! achievements
        result = so_wow_checker.check(test_user, [new_achievement])
        
        # Should not award anything for non-tiered achievements
        assert len(result) == 0


def test_check_does_not_duplicate_so_wow_achievements(app, test_user, so_wow_checker):
    """Test that So, Wow! achievements are not duplicated."""
    with app.app_context():
        from app import db
        
        # User already has "so-wow-bronze"
        existing_so_wow = Achievement(
            user_id=test_user.id,
            code="so-wow-bronze",
            title="So, Wow! (Bronze)",
            description="First bronze achievement",
            icon="🌟",
            category="milestone",
        )
        db.session.add(existing_so_wow)
        db.session.commit()
        
        # Create a new bronze tier achievement
        new_achievement = Achievement(
            user_id=test_user.id,
            code="question-master-bronze",
            title="Question Master (Bronze)",
            description="Answered 100 questions",
            icon="🏆",
            category="milestone",
        )
        db.session.add(new_achievement)
        db.session.commit()
        
        # Check So, Wow! achievements
        result = so_wow_checker.check(test_user, [new_achievement])
        
        # Should not award duplicate "so-wow-bronze"
        assert len(result) == 0
        assert Achievement.query.filter_by(user_id=test_user.id, code="so-wow-bronze").count() == 1



