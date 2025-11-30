"""Backend tests for Tests Tab functionality.

Tests cover test definitions, attempts, tier calculation, and backward compatibility.
"""

import pytest
from datetime import datetime

from app import create_app, db
from app.models import User, TestAttempt, PracticeSession, Response, Question
from app.services.test_service import TestService
from app.services.session_engine_service import SessionEngineService
from app.config.tests.test_definitions import NEW_TEST_DEFINITIONS


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
def test_questions(app):
    """Create test questions."""
    with app.app_context():
        questions = []
        for i in range(10):
            question = Question(
                operation="addition",
                operand1=1 + i,
                operand2=1,
                correct_answer=str(2 + i),
                prompt=f"{1+i} + 1",
                required_level=1,
                level_tag="Level 1"
            )
            db.session.add(question)
            questions.append(question)
        db.session.commit()
        return questions


def test_tst_be_001_get_all_test_definitions(app, test_user):
    """TST-BE-001: Get all test definitions returns merged legacy+new catalog."""
    with app.app_context():
        definitions = TestService.get_all_test_definitions(user_level=test_user.level)
        
        # Should return both legacy and new test definitions
        assert len(definitions) > 0
        
        # Check for legacy test types
        legacy_tests = [d for d in definitions if d.get("is_legacy", False)]
        assert len(legacy_tests) > 0
        
        # Check for new test types
        new_tests = [d for d in definitions if not d.get("is_legacy", False)]
        assert len(new_tests) > 0
        
        # Verify test metadata is correct
        for test_def in definitions:
            assert "test_type" in test_def
            assert "operation" in test_def
            assert "level_requirement" in test_def
            assert "question_count" in test_def


def test_tst_be_002_get_test_attempts(app, test_user, test_questions):
    """TST-BE-002: Get test attempts for user returns correct data."""
    with app.app_context():
        # Create a test attempt
        test_attempt = TestAttempt(
            user_id=test_user.id,
            level=1,
            test_type="level_1",
            score=0.85,
            avg_time_per_question_ms=3000,
            total_duration_ms=75000,
            passed=True,
        )
        db.session.add(test_attempt)
        db.session.commit()
        
        # Get attempts
        attempts = TestService.get_test_attempts(test_user.id, test_type="level_1")
        
        assert len(attempts) == 1
        attempt = attempts[0]
        assert attempt["attempt_id"] == test_attempt.id
        assert attempt["test_type"] == "level_1"
        assert attempt["score"] == 0.85
        assert attempt["accuracy"] == 85.0
        assert attempt["passed"] is True
        assert "tier" in attempt


def test_tst_be_003_get_test_attempt_detail(app, test_user, test_questions):
    """TST-BE-003: Get test attempt detail includes all questions and responses."""
    with app.app_context():
        # Create a test session
        session = PracticeSession(
            user_id=test_user.id,
            mode="standard",
            level=1,
            is_test=True,
            test_type="level_1",
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            total_questions=10,
            correct_count=8,
            accuracy=80.0,
        )
        db.session.add(session)
        db.session.flush()
        
        # Create responses
        for i, question in enumerate(test_questions[:10]):
            response = Response(
                session_id=session.id,
                user_id=test_user.id,
                question_id=question.id,
                submitted_answer=question.correct_answer if i < 8 else "999",
                is_correct=i < 8,
                duration_ms=3000,
                answered_at=datetime.utcnow(),
            )
            db.session.add(response)
        
        # Create test attempt
        test_attempt = TestAttempt(
            user_id=test_user.id,
            level=1,
            test_type="level_1",
            score=0.80,
            avg_time_per_question_ms=3000,
            total_duration_ms=30000,
            passed=True,
        )
        db.session.add(test_attempt)
        db.session.commit()
        
        # Get attempt detail
        detail = TestService.get_test_attempt_detail(test_attempt.id)
        
        assert detail is not None
        assert detail["attempt_id"] == test_attempt.id
        assert len(detail["questions"]) == 10
        assert all("question_id" in q for q in detail["questions"])
        assert all("user_answer" in q for q in detail["questions"])
        assert all("is_correct" in q for q in detail["questions"])


def test_tst_be_004_tier_calculation(app):
    """TST-BE-004: Test tier calculation thresholds match requirements."""
    with app.app_context():
        # Test B tier: not 100% accurate
        tier = TestService._calculate_tier(0.90, 2000, 50)
        assert tier == "B"
        
        # Test A tier: 100% accuracy, <30 questions
        tier = TestService._calculate_tier(1.0, 2000, 25)
        assert tier == "A"
        
        # Test S tier: 100% accuracy, 31-59 questions, <6s/question
        tier = TestService._calculate_tier(1.0, 5000, 50)
        assert tier == "S"
        
        # Test SS tier: 100% accuracy, <90 questions, <4s/question
        tier = TestService._calculate_tier(1.0, 3500, 80)
        assert tier == "SS"
        
        # Test SSS tier: 100% accuracy, 90+ questions, <3s/question
        tier = TestService._calculate_tier(1.0, 2500, 100)
        assert tier == "SSS"


def test_tst_be_005_test_discovery_logic(app, test_user):
    """TST-BE-005: Test discovery logic locks/unlocks based on level."""
    with app.app_context():
        # Get definitions for level 1 user
        definitions = TestService.get_all_test_definitions(user_level=1)
        
        # All definitions should have level_requirement <= 1
        for test_def in definitions:
            assert test_def["level_requirement"] <= 1
        
        # Update user to level 5
        test_user.level = 5
        db.session.commit()
        
        # Get definitions for level 5 user
        definitions_level_5 = TestService.get_all_test_definitions(user_level=5)
        
        # Should have more definitions available
        assert len(definitions_level_5) >= len(definitions)
        
        # All definitions should have level_requirement <= 5
        for test_def in definitions_level_5:
            assert test_def["level_requirement"] <= 5


def test_tst_be_006_test_attempts_api_endpoint(app, test_user, test_questions):
    """TST-BE-006: Test attempts API endpoint returns correct format."""
    with app.app_context():
        # Create test attempt
        test_attempt = TestAttempt(
            user_id=test_user.id,
            level=1,
            test_type="addition-1digit",
            score=0.90,
            avg_time_per_question_ms=4000,
            total_duration_ms=200000,
            passed=True,
        )
        db.session.add(test_attempt)
        db.session.commit()
        
        # Test the service method (API endpoint would call this)
        attempts = TestService.get_test_attempts(test_user.id, test_type="addition-1digit")
        
        assert len(attempts) == 1
        attempt = attempts[0]
        assert "attempt_id" in attempt
        assert "test_type" in attempt
        assert "accuracy" in attempt
        assert "tier" in attempt
        assert "passed" in attempt


def test_tst_be_007_test_attempt_detail_api_endpoint(app, test_user, test_questions):
    """TST-BE-007: Test attempt detail API endpoint includes all data."""
    with app.app_context():
        # Create session and attempt (similar to TST-BE-003)
        session = PracticeSession(
            user_id=test_user.id,
            mode="standard",
            level=1,
            is_test=True,
            test_type="addition-1digit",
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            total_questions=10,
            correct_count=10,
            accuracy=100.0,
        )
        db.session.add(session)
        db.session.flush()
        
        for question in test_questions[:10]:
            response = Response(
                session_id=session.id,
                user_id=test_user.id,
                question_id=question.id,
                submitted_answer=question.correct_answer,
                is_correct=True,
                duration_ms=3000,
                answered_at=datetime.utcnow(),
            )
            db.session.add(response)
        
        test_attempt = TestAttempt(
            user_id=test_user.id,
            level=1,
            test_type="addition-1digit",
            score=1.0,
            avg_time_per_question_ms=3000,
            total_duration_ms=30000,
            passed=True,
        )
        db.session.add(test_attempt)
        db.session.commit()
        
        # Get detail
        detail = TestService.get_test_attempt_detail(test_attempt.id)
        
        assert detail is not None
        assert "questions" in detail
        assert len(detail["questions"]) == 10
        assert all("prompt" in q for q in detail["questions"])
        assert all("correct_answer" in q for q in detail["questions"])
        assert all("user_answer" in q for q in detail["questions"])
        assert all("is_correct" in q for q in detail["questions"])


def test_tst_be_008_test_definitions_api_endpoint(app, test_user):
    """TST-BE-008: Test definitions API endpoint returns all definitions."""
    with app.app_context():
        definitions = TestService.get_all_test_definitions(user_level=test_user.level)
        
        # Should return definitions
        assert len(definitions) > 0
        
        # Verify response format
        for test_def in definitions:
            assert "test_type" in test_def
            assert "operation" in test_def
            assert "level_requirement" in test_def
            assert "question_count" in test_def
            assert "display_name" in test_def or "test_type" in test_def


def test_tst_be_009_test_tier_achievements_for_new_tests(app, test_user, test_questions):
    """TST-BE-009: Test tier achievements for new tests (B→SSS) still function."""
    with app.app_context():
        # This test verifies that tier calculation works for new test types
        # Create a test attempt with specific accuracy/speed for a new test type
        test_attempt = TestAttempt(
            user_id=test_user.id,
            level=1,
            test_type="addition-1digit",
            score=1.0,  # 100% accuracy
            avg_time_per_question_ms=2500,  # 2.5s per question
            total_duration_ms=125000,  # 50 questions * 2.5s
            passed=True,
        )
        db.session.add(test_attempt)
        db.session.commit()
        
        # Calculate tier
        tier = TestService._calculate_tier(
            test_attempt.score,
            test_attempt.avg_time_per_question_ms,
            50  # question_count
        )
        
        # Should be SSS tier (100% accuracy, 50 questions, <3s/question)
        assert tier == "SSS"


def test_tst_be_010_backward_compatibility_with_old_test_types(app, test_user):
    """TST-BE-010: Backward compatibility - old test types still work."""
    with app.app_context():
        # Verify old test types are still in TEST_TYPES
        assert "multiplication_1" in SessionEngineService.TEST_TYPES
        assert "division_1" in SessionEngineService.TEST_TYPES
        assert "level_1" in SessionEngineService.LEVEL_TEST_TYPES or "level_1" in SessionEngineService.TEST_TYPES
        
        # Verify old test types can be retrieved in definitions
        definitions = TestService.get_all_test_definitions()
        old_test_types = [d for d in definitions if d.get("is_legacy", False)]
        assert len(old_test_types) > 0
        
        # Verify old test types can be used for test attempts
        test_attempt = TestAttempt(
            user_id=test_user.id,
            level=9,
            test_type="multiplication_1",  # Old test type
            score=0.90,
            avg_time_per_question_ms=4000,
            total_duration_ms=80000,
            passed=True,
        )
        db.session.add(test_attempt)
        db.session.commit()
        
        # Should be able to retrieve the attempt
        attempts = TestService.get_test_attempts(test_user.id, test_type="multiplication_1")
        assert len(attempts) == 1
        assert attempts[0]["test_type"] == "multiplication_1"

