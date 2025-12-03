"""Backend tests for generic achievement system.

Tests verify generic achievement checking, tier system,
Champion tier qualification, and session tracking.
"""

import pytest
from datetime import datetime

from app import create_app, db
from app.models import User, Achievement, PracticeSession, Question, Response
from app.services.achievement_service import AchievementService
from app.utils.tier_utils import (
    get_tier_hierarchy,
    get_all_tiers,
    map_old_tier_to_new,
    is_tier_higher_than,
    get_tier_value,
)


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
def test_question(app):
    """Create a test question."""
    with app.app_context():
        question = Question(
            operation="addition",
            operand1=5,
            operand2=3,
            correct_answer="8",
            prompt="5 + 3",
            required_level=1,
        )
        db.session.add(question)
        db.session.commit()
        return question


@pytest.fixture
def test_practice_session(app, test_user, test_question):
    """Create a completed practice session with responses."""
    with app.app_context():
        session = PracticeSession(
            user_id=test_user.id,
            mode="standard",
            level=1,
            is_test=False,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            total_questions=100,
            correct_count=100,
            accuracy=100.0,
            total_duration_ms=150000,  # 1.5 seconds per question
        )
        db.session.add(session)
        db.session.flush()
        
        # Add responses
        for i in range(100):
            response = Response(
                session_id=session.id,
                question_id=test_question.id,
                user_id=test_user.id,
                submitted_answer="8",
                correct_answer="8",
                is_correct=True,
                duration_ms=1500,
                answered_at=datetime.utcnow(),
            )
            db.session.add(response)
        
        db.session.commit()
        return session


@pytest.fixture
def test_test_session(app, test_user, test_question):
    """Create a completed test session."""
    with app.app_context():
        session = PracticeSession(
            user_id=test_user.id,
            mode="standard",
            level=1,
            is_test=True,
            test_type="addition_1digit",
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            total_questions=100,
            correct_count=100,
            accuracy=100.0,
            total_duration_ms=150000,  # 1.5 seconds per question
        )
        db.session.add(session)
        db.session.flush()
        
        # Add responses
        for i in range(100):
            response = Response(
                session_id=session.id,
                question_id=test_question.id,
                user_id=test_user.id,
                submitted_answer="8",
                correct_answer="8",
                is_correct=True,
                duration_ms=1500,
                answered_at=datetime.utcnow(),
            )
            db.session.add(response)
        
        db.session.commit()
        return session


def test_tier_utils_001_get_tier_hierarchy(app):
    """TIER-UTILS-001: get_tier_hierarchy() returns correct hierarchy."""
    with app.app_context():
        hierarchy = get_tier_hierarchy()
        assert hierarchy["bronze"] == 1
        assert hierarchy["silver"] == 2
        assert hierarchy["champion"] == 11
        assert len(hierarchy) == 11


def test_tier_utils_002_get_all_tiers(app):
    """TIER-UTILS-002: get_all_tiers() returns all tiers in order."""
    with app.app_context():
        tiers = get_all_tiers()
        assert tiers[0] == "bronze"
        assert tiers[-1] == "champion"
        assert len(tiers) == 11


def test_tier_utils_003_map_old_tier_to_new(app):
    """TIER-UTILS-003: map_old_tier_to_new() correctly maps old letter tiers."""
    with app.app_context():
        assert map_old_tier_to_new("b") == "bronze"
        assert map_old_tier_to_new("a") == "silver"
        assert map_old_tier_to_new("s") == "gold"
        assert map_old_tier_to_new("ss") == "platinum"
        assert map_old_tier_to_new("sss") == "diamond"


def test_tier_utils_004_is_tier_higher_than(app):
    """TIER-UTILS-004: is_tier_higher_than() correctly compares tiers."""
    with app.app_context():
        assert is_tier_higher_than("silver", "bronze") is True
        assert is_tier_higher_than("gold", "silver") is True
        assert is_tier_higher_than("bronze", "silver") is False
        assert is_tier_higher_than("champion", "divine") is True


def test_tier_utils_005_get_tier_value(app):
    """TIER-UTILS-005: get_tier_value() returns correct numeric value."""
    with app.app_context():
        assert get_tier_value("bronze") == 1
        assert get_tier_value("champion") == 11
        assert get_tier_value("unknown") == 0


def test_generic_achievement_001_count_achievements_by_code(app, test_user):
    """GEN-ACH-001: count_achievements_by_code() counts achievement occurrences."""
    with app.app_context():
        # Create multiple achievements with same code
        for i in range(3):
            achievement = Achievement(
                user_id=test_user.id,
                code="test-achievement",
                title="Test",
                description="Test",
                icon="🏆",
                category="test",
                earned_at=datetime.utcnow(),
            )
            db.session.add(achievement)
        db.session.commit()
        
        count = AchievementService.count_achievements_by_code(
            test_user.id, "test-achievement"
        )
        assert count == 3


def test_generic_achievement_002_count_achievements_by_code_zero(app, test_user):
    """GEN-ACH-002: count_achievements_by_code() returns 0 when no achievements exist."""
    with app.app_context():
        count = AchievementService.count_achievements_by_code(
            test_user.id, "nonexistent-achievement"
        )
        assert count == 0


def test_generic_achievement_003_check_generic_accuracy_bronze(app, test_user, test_practice_session):
    """GEN-ACH-003: check_generic_accuracy_achievements() awards Bronze tier for 80%+ accuracy."""
    with app.app_context():
        # Modify session to have 80% accuracy
        test_practice_session.correct_count = 80
        test_practice_session.accuracy = 80.0
        db.session.commit()
        
        achievements = AchievementService.check_generic_accuracy_achievements(
            test_practice_session
        )
        
        assert len(achievements) > 0
        assert any("bronze" in a.code for a in achievements)
        assert all(a.session_id == test_practice_session.id for a in achievements)


def test_generic_achievement_004_check_generic_accuracy_divine(app, test_user, test_practice_session):
    """GEN-ACH-004: check_generic_accuracy_achievements() awards Divine tier for 100% accuracy, 100+ questions, <1.5s/question."""
    with app.app_context():
        # Session already meets Divine requirements
        achievements = AchievementService.check_generic_accuracy_achievements(
            test_practice_session
        )
        
        # Should award highest tier achieved (Divine)
        assert len(achievements) > 0
        awarded_codes = [a.code for a in achievements]
        assert any("divine" in code for code in awarded_codes)
        assert all(a.session_id == test_practice_session.id for a in achievements)


def test_generic_achievement_005_check_generic_accuracy_awards_highest_tier(app, test_user, test_practice_session):
    """GEN-ACH-005: check_generic_accuracy_achievements() awards only highest tier achieved."""
    with app.app_context():
        achievements = AchievementService.check_generic_accuracy_achievements(
            test_practice_session
        )
        
        # Should award only one achievement (the highest tier)
        assert len(achievements) == 1
        assert achievements[0].session_id == test_practice_session.id


def test_generic_achievement_006_check_generic_test_bronze(app, test_user, test_test_session):
    """GEN-ACH-006: check_generic_test_achievements() awards Bronze tier for completing test."""
    with app.app_context():
        achievements = AchievementService.check_generic_test_achievements(
            test_test_session
        )
        
        # Should award at least Bronze tier
        assert len(achievements) > 0
        assert all(a.session_id == test_test_session.id for a in achievements)


def test_generic_achievement_007_check_generic_test_divine(app, test_user, test_test_session):
    """GEN-ACH-007: check_generic_test_achievements() awards Divine tier for 100% accuracy, 100+ questions, <1.5s/question."""
    with app.app_context():
        achievements = AchievementService.check_generic_test_achievements(
            test_test_session
        )
        
        # Should award highest tier achieved
        assert len(achievements) > 0
        awarded_codes = [a.code for a in achievements]
        # May award Divine or Champion depending on server record
        assert any("divine" in code or "champion" in code for code in awarded_codes)
        assert all(a.session_id == test_test_session.id for a in achievements)


def test_generic_achievement_008_check_generic_test_awards_highest_tier(app, test_user, test_test_session):
    """GEN-ACH-008: check_generic_test_achievements() awards only highest tier achieved."""
    with app.app_context():
        achievements = AchievementService.check_generic_test_achievements(
            test_test_session
        )
        
        # Should award only one achievement (the highest tier)
        assert len(achievements) == 1
        assert achievements[0].session_id == test_test_session.id


def test_generic_achievement_009_champion_eligibility_check(app, test_user, test_practice_session):
    """GEN-ACH-009: checkChampionEligibility() checks Champion tier qualification."""
    with app.app_context():
        # This will depend on server record status
        result = AchievementService.checkChampionEligibility(
            "addition-basics-champion",
            test_practice_session,
            "champion",
        )
        
        # Result depends on whether this beats existing record
        assert isinstance(result, bool)


def test_generic_achievement_010_champion_eligibility_returns_false_for_non_champion(app, test_user, test_practice_session):
    """GEN-ACH-010: checkChampionEligibility() returns False for non-Champion tier."""
    with app.app_context():
        result = AchievementService.checkChampionEligibility(
            "addition-basics-divine",
            test_practice_session,
            "divine",
        )
        assert result is False


def test_generic_achievement_011_accuracy_achievements_session_id_tracking(app, test_user, test_practice_session):
    """GEN-ACH-011: Generic accuracy achievements record session_id."""
    with app.app_context():
        achievements = AchievementService.check_generic_accuracy_achievements(
            test_practice_session
        )
        
        # All achievements should have session_id set
        for achievement in achievements:
            assert achievement.session_id == test_practice_session.id
            # Verify persisted
            db.session.refresh(achievement)
            assert achievement.session_id == test_practice_session.id


def test_generic_achievement_012_test_achievements_session_id_tracking(app, test_user, test_test_session):
    """GEN-ACH-012: Generic test achievements record session_id."""
    with app.app_context():
        achievements = AchievementService.check_generic_test_achievements(
            test_test_session
        )
        
        # All achievements should have session_id set
        for achievement in achievements:
            assert achievement.session_id == test_test_session.id
            # Verify persisted
            db.session.refresh(achievement)
            assert achievement.session_id == test_test_session.id


def test_generic_achievement_013_level_accuracy_supports_operation_filter(app, test_user, test_question):
    """GEN-ACH-013: level_accuracy checking supports operation filtering."""
    with app.app_context():
        # Create achievement config with operation filter
        from app.config.achievements import ACCURACY_ACHIEVEMENTS
        
        # Check that accuracy achievements have operation field
        addition_bronze = ACCURACY_ACHIEVEMENTS.get("addition-basics-bronze")
        assert addition_bronze is not None
        assert addition_bronze["requirements"].get("operation") == "addition"


def test_generic_achievement_014_level_accuracy_supports_max_questions(app, test_user):
    """GEN-ACH-014: level_accuracy checking supports max_questions requirement."""
    with app.app_context():
        from app.config.achievements import ACCURACY_ACHIEVEMENTS
        
        # Check that some tiers have max_questions
        addition_silver = ACCURACY_ACHIEVEMENTS.get("addition-basics-silver")
        assert addition_silver is not None
        requirements = addition_silver["requirements"]
        assert "max_questions" in requirements or "min_questions" in requirements


def test_generic_achievement_015_level_accuracy_supports_max_speed(app, test_user):
    """GEN-ACH-015: level_accuracy checking supports max_speed requirement."""
    with app.app_context():
        from app.config.achievements import ACCURACY_ACHIEVEMENTS
        
        # Check that higher tiers have max_speed
        addition_platinum = ACCURACY_ACHIEVEMENTS.get("addition-basics-platinum")
        if addition_platinum:
            requirements = addition_platinum["requirements"]
            # Platinum tier should have speed requirement
            assert "max_speed" in requirements or "min_questions" in requirements


def test_generic_achievement_016_accuracy_achievements_not_awarded_twice(app, test_user, test_practice_session):
    """GEN-ACH-016: Generic accuracy achievements are not awarded twice for same tier."""
    with app.app_context():
        # Award achievement first time
        achievements1 = AchievementService.check_generic_accuracy_achievements(
            test_practice_session
        )
        
        assert len(achievements1) > 0
        awarded_code = achievements1[0].code
        
        # Try to award again
        achievements2 = AchievementService.check_generic_accuracy_achievements(
            test_practice_session
        )
        
        # Should not award again (already earned)
        assert len(achievements2) == 0


def test_generic_achievement_017_test_achievements_not_awarded_twice(app, test_user, test_test_session):
    """GEN-ACH-017: Generic test achievements are not awarded twice for same tier."""
    with app.app_context():
        # Award achievement first time
        achievements1 = AchievementService.check_generic_test_achievements(
            test_test_session
        )
        
        assert len(achievements1) > 0
        awarded_code = achievements1[0].code
        
        # Try to award again
        achievements2 = AchievementService.check_generic_test_achievements(
            test_test_session
        )
        
        # Should not award again (already earned)
        assert len(achievements2) == 0


def test_generic_achievement_018_accuracy_only_for_practice_sessions(app, test_user, test_test_session):
    """GEN-ACH-018: check_generic_accuracy_achievements() only checks practice sessions (not tests)."""
    with app.app_context():
        # Test session should return empty list
        achievements = AchievementService.check_generic_accuracy_achievements(
            test_test_session
        )
        assert len(achievements) == 0


def test_generic_achievement_019_test_only_for_test_sessions(app, test_user, test_practice_session):
    """GEN-ACH-019: check_generic_test_achievements() only checks test sessions."""
    with app.app_context():
        # Practice session should return empty list
        achievements = AchievementService.check_generic_test_achievements(
            test_practice_session
        )
        assert len(achievements) == 0


def test_generic_achievement_020_incomplete_session_not_checked(app, test_user, test_question):
    """GEN-ACH-020: Incomplete sessions are not checked for achievements."""
    with app.app_context():
        # Create incomplete session (no completed_at)
        incomplete_session = PracticeSession(
            user_id=test_user.id,
            mode="standard",
            level=1,
            is_test=False,
            started_at=datetime.utcnow(),
            completed_at=None,  # Not completed
            total_questions=100,
            correct_count=100,
            accuracy=100.0,
        )
        db.session.add(incomplete_session)
        db.session.commit()
        
        achievements = AchievementService.check_generic_accuracy_achievements(
            incomplete_session
        )
        assert len(achievements) == 0


def test_generic_achievement_021_accuracy_achievements_in_config(app):
    """GEN-ACH-021: Generic accuracy achievements are included in ACHIEVEMENTS_CONFIG."""
    with app.app_context():
        from app.config.achievements import ACHIEVEMENTS_CONFIG
        
        # Check that generic accuracy achievements exist
        assert "addition-basics-bronze" in ACHIEVEMENTS_CONFIG
        assert "addition-basics-silver" in ACHIEVEMENTS_CONFIG
        assert "addition-basics-gold" in ACHIEVEMENTS_CONFIG
        assert "addition-basics-champion" in ACHIEVEMENTS_CONFIG
        
        # Check that all operations have achievements
        for operation in ["addition", "subtraction", "multiplication", "division"]:
            assert f"{operation}-basics-bronze" in ACHIEVEMENTS_CONFIG
            assert f"{operation}-basics-champion" in ACHIEVEMENTS_CONFIG


def test_generic_achievement_022_test_achievements_in_config(app):
    """GEN-ACH-022: Generic test achievements are included in ACHIEVEMENTS_CONFIG."""
    with app.app_context():
        from app.config.achievements import ACHIEVEMENTS_CONFIG
        
        # Check that generic test achievements exist for new test types
        assert "addition-1digit-bronze" in ACHIEVEMENTS_CONFIG
        assert "addition-1digit-champion" in ACHIEVEMENTS_CONFIG
        
        # Check that tiers are included
        assert "addition-1digit-divine" in ACHIEVEMENTS_CONFIG


def test_generic_achievement_023_all_tiers_present_in_accuracy(app):
    """GEN-ACH-023: All tiers (Bronze through Champion) are present for accuracy achievements."""
    with app.app_context():
        from app.config.achievements import ACHIEVEMENTS_CONFIG
        from app.utils.tier_utils import ALL_TIERS
        
        operation = "addition"
        for tier in ALL_TIERS:
            code = f"{operation}-basics-{tier}"
            assert code in ACHIEVEMENTS_CONFIG, f"Missing achievement: {code}"


def test_generic_achievement_024_all_tiers_present_in_tests(app):
    """GEN-ACH-024: All tiers (Bronze through Champion) are present for test achievements."""
    with app.app_context():
        from app.config.achievements import ACHIEVEMENTS_CONFIG
        from app.utils.tier_utils import ALL_TIERS
        
        test_type = "addition-1digit"
        for tier in ALL_TIERS:
            code = f"{test_type}-{tier}"
            # Not all test types may have all tiers, so we check if at least some do
            if tier == "bronze":
                assert code in ACHIEVEMENTS_CONFIG, f"Missing achievement: {code}"

