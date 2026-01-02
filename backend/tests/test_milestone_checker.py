"""Tests for milestone achievement checker."""

import pytest

from app import create_app, db
from app.models import Achievement, User
from app.services.achievements.achievement_checkers.milestone_checker import MilestoneChecker
from app.services.level_config_service import LevelConfigService


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
        _ = user.id
        return user


@pytest.fixture
def achievement_configs():
    """Get achievement configs."""
    return LevelConfigService.get_all_achievement_configs()


@pytest.fixture
def milestone_checker(achievement_configs):
    """Create a milestone checker instance."""
    return MilestoneChecker(achievement_configs)


def test_question_master_bronze_achievement(app, test_user, milestone_checker):
    """Test that question-master bronze is awarded for 100 questions."""
    with app.app_context():
        # Create metrics with 100 questions answered
        # Use slow speed and no streak to avoid qualifying for other milestone types
        metrics = {
            "questions_answered": 100,
            "average_speed_seconds": 10.0,  # Too slow for speed-demon
            "operation_stats": {
                "currentStreak": 0,  # No streak for week-warrior
            }
        }
        
        achievements = milestone_checker.check(test_user, metrics)
    
        # Verify achievement was awarded
        achievement = Achievement.query.filter_by(
            user_id=test_user.id,
            code="question-master-bronze"
        ).first()
        
        assert achievement is not None, "Question Master (Bronze) should be awarded for 100 questions"
        assert achievement.title == "Question Master (Bronze)"
        assert len(achievements) == 1
        assert achievements[0].code == "question-master-bronze"


def test_question_master_silver_achievement(app, test_user, milestone_checker):
    """Test that question-master silver is awarded for 500 questions."""
    with app.app_context():
        # Create metrics with 500 questions answered
        # Use slow speed and no streak to avoid qualifying for other milestone types
        metrics = {
            "questions_answered": 500,
            "average_speed_seconds": 10.0,  # Too slow for speed-demon
            "operation_stats": {
                "currentStreak": 0,  # No streak for week-warrior
            }
        }
        
        achievements = milestone_checker.check(test_user, metrics)
        
        # Verify achievement was awarded
        achievement = Achievement.query.filter_by(
            user_id=test_user.id,
            code="question-master-silver"
        ).first()
        
        assert achievement is not None, "Question Master (Silver) should be awarded for 500 questions"
        assert achievement.title == "Question Master (Silver)"
        assert len(achievements) == 1
        assert achievements[0].code == "question-master-silver"


def test_question_master_highest_tier_only(app, test_user, milestone_checker):
    """Test that only the highest qualifying tier is awarded."""
    with app.app_context():
        # Create metrics with 1000 questions (qualifies for bronze, silver, gold)
        # Use slow speed and no streak to avoid qualifying for other milestone types
        metrics = {
            "questions_answered": 1000,
            "average_speed_seconds": 10.0,  # Too slow for speed-demon
            "operation_stats": {
                "currentStreak": 0,  # No streak for week-warrior
            }
        }
        
        achievements = milestone_checker.check(test_user, metrics)
        
        # Should only award gold (highest tier)
        bronze = Achievement.query.filter_by(
            user_id=test_user.id,
            code="question-master-bronze"
        ).first()
        silver = Achievement.query.filter_by(
            user_id=test_user.id,
            code="question-master-silver"
        ).first()
        gold = Achievement.query.filter_by(
            user_id=test_user.id,
            code="question-master-gold"
        ).first()
        
        assert bronze is None, "Bronze should not be awarded when higher tier qualifies"
        assert silver is None, "Silver should not be awarded when higher tier qualifies"
        assert gold is not None, "Gold should be awarded (highest qualifying tier)"
        assert len(achievements) == 1
        assert achievements[0].code == "question-master-gold"


def test_speed_demon_bronze_achievement(app, test_user, milestone_checker):
    """Test that speed-demon bronze is awarded for fast average speed."""
    with app.app_context():
        # Create metrics with fast average speed
        # Use speed that qualifies for bronze (max 5.0) but not higher tiers
        # Bronze: max 5.0, Silver: max 4.0, so use 4.5 seconds
        metrics = {
            "questions_answered": 100,  # Qualifies for question-master-bronze too
            "average_speed_seconds": 4.5,  # Fast enough for bronze (max 5.0) but not silver (max 4.0)
            "operation_stats": {
                "currentStreak": 0,  # No streak for week-warrior
            }
        }
        
        achievements = milestone_checker.check(test_user, metrics)
        
        # Verify achievement was awarded (may also get question-master)
        achievement = Achievement.query.filter_by(
            user_id=test_user.id,
            code="speed-demon-bronze"
        ).first()
        
        assert achievement is not None, f"Speed Demon (Bronze) should be awarded. Got achievements: {[a.code for a in achievements]}"
        assert achievement.title == "Speed Demon (Bronze)"
        assert any(a.code == "speed-demon-bronze" for a in achievements)


def test_speed_demon_not_awarded_below_minimum_questions(app, milestone_checker):
    """Test that speed-demon is not awarded below minimum questions."""
    with app.app_context():
        # Create a fresh user for this test to avoid interference from other tests
        user = User(display_name="TestUser2", pin="1234", avatar="🐯", experience=0)
        db.session.add(user)
        db.session.commit()
        
        # Create metrics with fast speed but not enough questions (below min_questions: 10)
        metrics = {
            "questions_answered": 5,  # Below speed-demon minimum (10)
            "average_speed_seconds": 4.5,  # Fast enough for speed-demon-bronze if it had enough questions
            "operation_stats": {
                "currentStreak": 0,  # No streak
            }
        }
        
        achievements = milestone_checker.check(user, metrics)
        
        # Verify no speed-demon achievement was awarded
        speed_demon = Achievement.query.filter(
            Achievement.user_id == user.id,
            Achievement.code.like("speed-demon-%")
        ).first()
        
        assert speed_demon is None, f"Speed Demon should not be awarded below minimum questions. Got: {[a.code for a in achievements]}"
        assert not any("speed-demon" in a.code for a in achievements), "No speed-demon achievements should be awarded"


def test_week_warrior_bronze_achievement(app, test_user, milestone_checker):
    """Test that week-warrior bronze is awarded for 7 day streak."""
    with app.app_context():
        # Create metrics with 7 day streak
        # Use low question count and slow speed to avoid qualifying for other milestone types
        metrics = {
            "questions_answered": 50,  # Below question-master threshold (100)
            "average_speed_seconds": 10.0,  # Too slow for speed-demon
            "operation_stats": {
                "currentStreak": 7,  # 7 days
            }
        }
        
        achievements = milestone_checker.check(test_user, metrics)
        
        # Verify achievement was awarded
        achievement = Achievement.query.filter_by(
            user_id=test_user.id,
            code="week-warrior-bronze"
        ).first()
        
        assert achievement is not None, "Week Warrior (Bronze) should be awarded for 7 day streak"
        assert achievement.title == "Week Warrior (Bronze)"
        assert len(achievements) == 1
        assert achievements[0].code == "week-warrior-bronze"


def test_week_warrior_not_awarded_below_streak(app, test_user, milestone_checker):
    """Test that week-warrior is not awarded below required streak."""
    with app.app_context():
        # Create metrics with insufficient streak
        # Use low question count and slow speed to avoid qualifying for other milestone types
        metrics = {
            "questions_answered": 50,  # Below question-master threshold (100)
            "average_speed_seconds": 10.0,  # Too slow for speed-demon
            "operation_stats": {
                "currentStreak": 5,  # Below 7 day requirement
            }
        }
        
        achievements = milestone_checker.check(test_user, metrics)
        
        # Verify no achievement was awarded
        achievement = Achievement.query.filter_by(
            user_id=test_user.id,
            code="week-warrior-bronze"
        ).first()
        
        assert achievement is None, "Week Warrior should not be awarded below required streak"
        assert len(achievements) == 0


def test_multiple_milestone_types(app, test_user, milestone_checker):
    """Test that multiple milestone types can be awarded in one check."""
    with app.app_context():
        # Create metrics that qualify for multiple milestone types
        # Use speeds that qualify for bronze tiers only
        metrics = {
            "questions_answered": 500,  # Qualifies for question-master-silver
            "average_speed_seconds": 4.5,  # Qualifies for speed-demon-bronze (max 5.0) but not silver (max 4.0)
            "operation_stats": {
                "currentStreak": 7,  # Qualifies for week-warrior-bronze
            }
        }
        
        achievements = milestone_checker.check(test_user, metrics)
        
        # Verify all three types were awarded
        question_master = Achievement.query.filter_by(
            user_id=test_user.id,
            code="question-master-silver"
        ).first()
        speed_demon = Achievement.query.filter_by(
            user_id=test_user.id,
            code="speed-demon-bronze"
        ).first()
        week_warrior = Achievement.query.filter_by(
            user_id=test_user.id,
            code="week-warrior-bronze"
        ).first()
        
        assert question_master is not None, "Question Master should be awarded"
        assert speed_demon is not None, "Speed Demon should be awarded"
        assert week_warrior is not None, "Week Warrior should be awarded"
        assert len(achievements) == 3


def test_no_metrics_returns_empty(app, test_user, milestone_checker):
    """Test that no achievements are awarded when metrics are None."""
    with app.app_context():
        achievements = milestone_checker.check(test_user, None)
        
        assert len(achievements) == 0


def test_already_earned_achievement_not_awarded_again(app, test_user, milestone_checker):
    """Test that already earned achievements are not awarded again."""
    with app.app_context():
        from app.services.achievement_service import AchievementService
        
        # Award bronze first
        AchievementService.create_achievement(
            user_id=test_user.id,
            code="question-master-bronze",
            title="Question Master (Bronze)",
            description="Test",
            icon="🏆",
            category="milestone",
        )
        
        # Create metrics that would qualify for bronze
        # Use slow speed and no streak to avoid qualifying for other milestone types
        metrics = {
            "questions_answered": 100,
            "average_speed_seconds": 10.0,  # Too slow for speed-demon
            "operation_stats": {
                "currentStreak": 0,  # No streak for week-warrior
            }
        }
        
        achievements = milestone_checker.check(test_user, metrics)
        
        # Should not award bronze again, but might award higher tier
        bronze_count = Achievement.query.filter_by(
            user_id=test_user.id,
            code="question-master-bronze"
        ).count()
        
        assert bronze_count == 1, "Bronze should not be awarded again"

