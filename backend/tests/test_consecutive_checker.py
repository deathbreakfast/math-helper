"""Comprehensive tests for ConsecutiveChecker.

Tests cover all methods in ConsecutiveChecker to achieve >80% coverage.
"""

import pytest
from datetime import datetime, timedelta

from app import create_app, db
from app.models import Achievement, PracticeSession, Question, Response, User
from app.services.achievements.achievement_checkers.consecutive_checker import ConsecutiveChecker
from app.services.level_config_service import LevelConfigService
from app.services.practice_service import PracticeService


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
        user = User(display_name="Test User", pin="1234", avatar="🐯", level=1)
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user


@pytest.fixture
def achievement_configs():
    """Get achievement configs for testing."""
    return LevelConfigService.get_all_achievement_configs()


@pytest.fixture
def consecutive_checker(achievement_configs):
    """Create a ConsecutiveChecker instance."""
    return ConsecutiveChecker(achievement_configs)


class TestConsecutiveChecker:
    """Test suite for ConsecutiveChecker."""

    def test_init(self, achievement_configs):
        """Test __init__ initializes checker."""
        checker = ConsecutiveChecker(achievement_configs)
        assert checker.achievement_configs == achievement_configs

    def test_check_no_test_type(self, app, test_user, consecutive_checker):
        """Test check with no test_type provided."""
        with app.app_context():
            result = consecutive_checker.check(test_user)
            assert result == []

    def test_check_unknown_test_type(self, app, test_user, consecutive_checker):
        """Test check with unknown test_type."""
        with app.app_context():
            result = consecutive_checker.check(test_user, test_type="unknown-test-type")
            assert result == []

    def test_check_no_attempts(self, app, test_user, consecutive_checker):
        """Test check when user has never attempted the test type."""
        with app.app_context():
            # Use a valid test type from TEST_TYPES
            from app.services.session_engine_service import SessionEngineService
            test_type = list(SessionEngineService.TEST_TYPES.keys())[0] if SessionEngineService.TEST_TYPES else None
            
            if test_type:
                result = consecutive_checker.check(test_user, test_type=test_type)
                assert result == []

    def test_check_already_earned(self, app, test_user, consecutive_checker):
        """Test check when achievement already earned."""
        with app.app_context():
            from app.services.session_engine_service import SessionEngineService
            test_type = list(SessionEngineService.TEST_TYPES.keys())[0] if SessionEngineService.TEST_TYPES else None
            
            if test_type:
                achievement_code = f"{test_type}_mastery"
                achievement = Achievement(
                    user_id=test_user.id,
                    code=achievement_code,
                    title="Test Mastery",
                    description="30 consecutive correct",
                    icon="🏆",
                    category="mastery"
                )
                db.session.add(achievement)
                db.session.commit()
                
                result = consecutive_checker.check(test_user, test_type=test_type)
                assert result == []

    def test_check_less_than_30_correct(self, app, test_user, consecutive_checker):
        """Test check when user has less than 30 correct answers."""
        with app.app_context():
            from app.services.session_engine_service import SessionEngineService
            test_type = list(SessionEngineService.TEST_TYPES.keys())[0] if SessionEngineService.TEST_TYPES else None
            
            if test_type:
                operation, required_level, _, _ = SessionEngineService.TEST_TYPES[test_type]
                
                session = PracticeService.create_session(user_id=test_user.id)
                
                # Create 29 correct responses
                for i in range(29):
                    question = PracticeService.create_question(
                        operation=operation,
                        operand1=1,
                        operand2=1,
                        correct_answer="2",
                        prompt="1 + 1",
                        required_level=required_level
                    )
                    
                    response = PracticeService.record_response(
                        session_id=session.id,
                        question_id=question.id,
                        user_id=test_user.id,
                        submitted_answer="2",
                        correct_answer="2",
                        is_correct=True,
                        duration_ms=2000
                    )
                    response.answered_at = datetime.utcnow() - timedelta(seconds=i)
                    db.session.add(response)
                
                db.session.commit()
                
                result = consecutive_checker.check(test_user, test_type=test_type)
                assert result == []

    def test_check_30_consecutive_correct(self, app, test_user, consecutive_checker):
        """Test check awards achievement for 30 consecutive correct."""
        with app.app_context():
            from app.services.session_engine_service import SessionEngineService
            test_type = list(SessionEngineService.TEST_TYPES.keys())[0] if SessionEngineService.TEST_TYPES else None
            
            if test_type:
                operation, required_level, _, _ = SessionEngineService.TEST_TYPES[test_type]
                
                session = PracticeService.create_session(user_id=test_user.id)
                
                # Create 30 consecutive correct responses
                for i in range(30):
                    question = PracticeService.create_question(
                        operation=operation,
                        operand1=1,
                        operand2=1,
                        correct_answer="2",
                        prompt="1 + 1",
                        required_level=required_level
                    )
                    
                    response = PracticeService.record_response(
                        session_id=session.id,
                        question_id=question.id,
                        user_id=test_user.id,
                        submitted_answer="2",
                        correct_answer="2",
                        is_correct=True,
                        duration_ms=2000
                    )
                    response.answered_at = datetime.utcnow() - timedelta(seconds=30-i)
                    db.session.add(response)
                
                db.session.commit()
                
                result = consecutive_checker.check(test_user, test_type=test_type)
                
                assert len(result) == 1
                assert result[0].code == f"{test_type}_mastery"
                assert result[0].user_id == test_user.id

    def test_check_not_consecutive(self, app, test_user, consecutive_checker):
        """Test check does not award if 30 correct but not consecutive."""
        with app.app_context():
            from app.services.session_engine_service import SessionEngineService
            test_type = list(SessionEngineService.TEST_TYPES.keys())[0] if SessionEngineService.TEST_TYPES else None
            
            if test_type:
                operation, required_level, _, _ = SessionEngineService.TEST_TYPES[test_type]
                
                session = PracticeService.create_session(user_id=test_user.id)
                
                # Create 30 responses: 29 correct, 1 incorrect in the middle
                for i in range(30):
                    question = PracticeService.create_question(
                        operation=operation,
                        operand1=1,
                        operand2=1,
                        correct_answer="2",
                        prompt="1 + 1",
                        required_level=required_level
                    )
                    
                    is_correct = i != 15  # One incorrect in the middle
                    response = PracticeService.record_response(
                        session_id=session.id,
                        question_id=question.id,
                        user_id=test_user.id,
                        submitted_answer="2" if is_correct else "3",
                        correct_answer="2",
                        is_correct=is_correct,
                        duration_ms=2000
                    )
                    response.answered_at = datetime.utcnow() - timedelta(seconds=30-i)
                    db.session.add(response)
                
                db.session.commit()
                
                result = consecutive_checker.check(test_user, test_type=test_type)
                assert result == []

    def test_check_more_than_30_correct(self, app, test_user, consecutive_checker):
        """Test check awards achievement when user has more than 30 consecutive correct."""
        with app.app_context():
            from app.services.session_engine_service import SessionEngineService
            test_type = list(SessionEngineService.TEST_TYPES.keys())[0] if SessionEngineService.TEST_TYPES else None
            
            if test_type:
                operation, required_level, _, _ = SessionEngineService.TEST_TYPES[test_type]
                
                session = PracticeService.create_session(user_id=test_user.id)
                
                # Create 35 consecutive correct responses
                for i in range(35):
                    question = PracticeService.create_question(
                        operation=operation,
                        operand1=1,
                        operand2=1,
                        correct_answer="2",
                        prompt="1 + 1",
                        required_level=required_level
                    )
                    
                    response = PracticeService.record_response(
                        session_id=session.id,
                        question_id=question.id,
                        user_id=test_user.id,
                        submitted_answer="2",
                        correct_answer="2",
                        is_correct=True,
                        duration_ms=2000
                    )
                    response.answered_at = datetime.utcnow() - timedelta(seconds=35-i)
                    db.session.add(response)
                
                db.session.commit()
                
                result = consecutive_checker.check(test_user, test_type=test_type)
                
                assert len(result) == 1
                assert result[0].code == f"{test_type}_mastery"

    def test_check_with_session_id(self, app, test_user, consecutive_checker):
        """Test check can accept session_id parameter."""
        with app.app_context():
            from app.services.session_engine_service import SessionEngineService
            test_type = list(SessionEngineService.TEST_TYPES.keys())[0] if SessionEngineService.TEST_TYPES else None
            
            if test_type:
                operation, required_level, _, _ = SessionEngineService.TEST_TYPES[test_type]
                
                session = PracticeService.create_session(user_id=test_user.id)
                
                # Create 30 consecutive correct responses
                for i in range(30):
                    question = PracticeService.create_question(
                        operation=operation,
                        operand1=1,
                        operand2=1,
                        correct_answer="2",
                        prompt="1 + 1",
                        required_level=required_level
                    )
                    
                    response = PracticeService.record_response(
                        session_id=session.id,
                        question_id=question.id,
                        user_id=test_user.id,
                        submitted_answer="2",
                        correct_answer="2",
                        is_correct=True,
                        duration_ms=2000
                    )
                    response.answered_at = datetime.utcnow() - timedelta(seconds=30-i)
                    db.session.add(response)
                
                db.session.commit()
                
                result = consecutive_checker.check(test_user, session_id=session.id, test_type=test_type)
                
                # Should still work with session_id (though not used in logic)
                assert len(result) == 1



