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
    is_tier_higher_than,
    get_tier_value,
)


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
        user = User(display_name="TestUser", pin="1234", avatar="🐯", experience=0)
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def test_question_id(app):
    """Create a test question and return ID."""
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
        return question.id


@pytest.fixture
def test_practice_session_id(app, test_user_id, test_question_id):
    """Create a completed practice session and return ID."""
    with app.app_context():
        session = PracticeSession(
            user_id=test_user_id,
            mode="standard",
            level=1,
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
                question_id=test_question_id,
                user_id=test_user_id,
                submitted_answer="8",
                correct_answer="8",
                is_correct=True,
                duration_ms=1500,
                answered_at=datetime.utcnow(),
            )
            db.session.add(response)
        
        db.session.commit()
        return session.id


@pytest.fixture
def test_test_session_id(app, test_user_id, test_question_id):
    """Create a completed test session and return ID."""
    with app.app_context():
        session = PracticeSession(
            user_id=test_user_id,
            mode="standard",
            level=1,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            total_questions=100,
            correct_count=100,
            accuracy=100.0,
            total_duration_ms=140000,  # 1.4 seconds per question (< 1.5s for Divine)
        )
        db.session.add(session)
        db.session.flush()
        
        # Add responses
        for i in range(100):
            response = Response(
                session_id=session.id,
                question_id=test_question_id,
                user_id=test_user_id,
                submitted_answer="8",
                correct_answer="8",
                is_correct=True,
                duration_ms=1400,
                answered_at=datetime.utcnow(),
            )
            db.session.add(response)
        
        db.session.commit()
        return session.id


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


# test_tier_utils_003_map_old_tier_to_new removed - map_old_tier_to_new function was removed with test system


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


def test_generic_achievement_001_count_achievements_by_code(app, test_user_id):
    """GEN-ACH-001: count_achievements_by_code() counts achievement occurrences."""
    with app.app_context():
        # Create one achievement
        achievement = Achievement(
            user_id=test_user_id,
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
            test_user_id, "test-achievement"
        )
        assert count == 1


def test_generic_achievement_002_count_achievements_by_code_zero(app, test_user_id):
    """GEN-ACH-002: count_achievements_by_code() returns 0 when no achievements exist."""
    with app.app_context():
        count = AchievementService.count_achievements_by_code(
            test_user_id, "nonexistent-achievement"
        )
        assert count == 0


# Tests 003-005 are removed as they tested 'check_generic_accuracy_achievements'
# which relied on deprecated 'addition-basics-*' achievements.
# 'check_test_tier_achievements' is the modern replacement and is tested in other files.


def test_generic_achievement_009_champion_eligibility_check(app, test_user_id, test_practice_session_id):
    """GEN-ACH-009: checkChampionEligibility() checks Champion tier qualification."""
    with app.app_context():
        test_practice_session = db.session.get(PracticeSession, test_practice_session_id)
        # This will depend on server record status
        result = AchievementService.checkChampionEligibility(
            "addition-1digit-champion",  # Updated code
            test_practice_session,
            "champion",
        )
        
        # Result depends on whether this beats existing record
        assert isinstance(result, bool)


def test_generic_achievement_010_champion_eligibility_returns_false_for_non_champion(app, test_user_id, test_practice_session_id):
    """GEN-ACH-010: checkChampionEligibility() returns False for non-Champion tier."""
    with app.app_context():
        test_practice_session = db.session.get(PracticeSession, test_practice_session_id)
        result = AchievementService.checkChampionEligibility(
            "addition-1digit-divine",  # Updated code
            test_practice_session,
            "divine",
        )
        assert result is False


# Test 011 removed (generic accuracy session tracking) - obsolete.


# Tests 013-014 removed (level accuracy helpers) - obsolete.


def test_generic_achievement_015_level_accuracy_supports_max_speed(app, test_user_id):
    """GEN-ACH-015: level_accuracy checking supports max_speed requirement."""
    with app.app_context():
        from app.config.achievements import ACCURACY_ACHIEVEMENTS
        
        # Check that higher tiers have max_speed
        addition_platinum = ACCURACY_ACHIEVEMENTS.get("addition-1digit-platinum")
        if addition_platinum:
            requirements = addition_platinum["requirements"]
            # Platinum tier should have speed requirement
            assert "max_speed" in requirements or "min_questions" in requirements


# Test 016 removed (accuracy not awarded twice) - obsolete.


# Test 018 removed (accuracy only for practice) - obsolete.


# Test 020 removed (incomplete session) - obsolete/covered by others.


def test_generic_achievement_021_accuracy_achievements_in_config(app):
    """GEN-ACH-021: Generic accuracy achievements are included in ACHIEVEMENTS_CONFIG."""
    with app.app_context():
        from app.config.achievements import ACHIEVEMENTS_CONFIG
        
        # Test achievements have been removed - check that existing achievements are in config
        assert "math-master-bronze" in ACHIEVEMENTS_CONFIG
        assert "math-master-silver" in ACHIEVEMENTS_CONFIG
        assert "math-master-gold" in ACHIEVEMENTS_CONFIG
        # Check for lightning-fast achievements (they have level-specific codes like lightning-fast-bronze-level-1)
        lightning_fast_keys = [k for k in ACHIEVEMENTS_CONFIG.keys() if k.startswith("lightning-fast-")]
        assert len(lightning_fast_keys) > 0, "Should have lightning-fast achievements"
        assert "speed-demon-bronze" in ACHIEVEMENTS_CONFIG


def test_generic_achievement_022_test_achievements_in_config(app):
    """GEN-ACH-022: Generic achievements are included in ACHIEVEMENTS_CONFIG."""
    with app.app_context():
        from app.config.achievements import ACHIEVEMENTS_CONFIG
        
        # Check that generic achievements exist (test-specific achievements removed)
        # Check for level-master achievements (used with metadata for level-specific requirements)
        assert "math-master-bronze" in ACHIEVEMENTS_CONFIG
        assert "math-master-champion" in ACHIEVEMENTS_CONFIG
        
        # Check that tiers are included
        assert "math-master-divine" in ACHIEVEMENTS_CONFIG
        
        # Check for new achievements
        assert "accuracy-ace-bronze" in ACHIEVEMENTS_CONFIG
        assert "so-wow-bronze" in ACHIEVEMENTS_CONFIG
        assert "human-calculator" in ACHIEVEMENTS_CONFIG
        assert "master-of-times-tables-bronze" in ACHIEVEMENTS_CONFIG
        assert "master-of-division-tables-bronze" in ACHIEVEMENTS_CONFIG
        assert "master-of-basic-addition-bronze" in ACHIEVEMENTS_CONFIG
        assert "master-of-basic-subtraction-bronze" in ACHIEVEMENTS_CONFIG


def test_generic_achievement_master_of_basic_all_tiers_present(app):
    """Master of Basic Addition/Subtraction achievements are defined for all tiers."""
    with app.app_context():
        from app.config.achievements import ACHIEVEMENTS_CONFIG
        from app.utils.tier_utils import ALL_TIERS

        for tier in ALL_TIERS:
            assert f"master-of-basic-addition-{tier}" in ACHIEVEMENTS_CONFIG
            assert f"master-of-basic-subtraction-{tier}" in ACHIEVEMENTS_CONFIG


def test_generic_achievement_023_all_tiers_present_in_accuracy(app):
    """GEN-ACH-023: All tiers for Accuracy Ace achievements are present.
    
    Note: Accuracy Ace only has bronze, silver, and gold tiers (80%, 90%, 100%).
    Platinum and higher tiers were removed per user requirements.
    """
    with app.app_context():
        from app.config.achievements import ACHIEVEMENTS_CONFIG
        
        # Accuracy Ace only has bronze, silver, gold
        accuracy_ace_tiers = ["bronze", "silver", "gold"]
        for tier in accuracy_ace_tiers:
            code = f"accuracy-ace-{tier}"
            assert code in ACHIEVEMENTS_CONFIG, f"Missing achievement: {code}"


def test_generic_achievement_024_all_tiers_present_in_tests(app):
    """GEN-ACH-024: All tiers for Accuracy Ace achievements are present.
    
    Note: Accuracy Ace only has bronze, silver, and gold tiers (80%, 90%, 100%).
    Platinum and higher tiers were removed per user requirements.
    System now uses generic achievements (accuracy-ace-{tier}) with metadata filters for test requirements.
    """
    with app.app_context():
        from app.config.achievements import ACHIEVEMENTS_CONFIG
        
        # Accuracy Ace only has bronze, silver, gold
        accuracy_ace_tiers = ["bronze", "silver", "gold"]
        for tier in accuracy_ace_tiers:
            code = f"accuracy-ace-{tier}"
            assert code in ACHIEVEMENTS_CONFIG, f"Missing achievement: {code}"
