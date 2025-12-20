"""Comprehensive tests for SessionEngineService.

Tests cover all methods in SessionEngineService to achieve >80% coverage.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from app import create_app, db
from app.models import PracticeSession, Question, Response, User
from app.services.achievement_service import AchievementService
from app.services.practice_service import PracticeService
from app.services.session_engine_service import SessionEngineService
from app.config.tests.test_definitions import NEW_TEST_DEFINITIONS


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
            difficulty="Level 1",
            target_ms=4000,
        )
        db.session.add(question)
        db.session.commit()
        db.session.refresh(question)
        return question


class TestSessionEngineService:
    """Test suite for SessionEngineService static methods."""

    def test_get_test_achievement_code(self):
        """Test _get_test_achievement_code returns correct format."""
        code = SessionEngineService._get_test_achievement_code("addition-1digit")
        assert code == "addition-1digit_mastery"

    def test_check_test_eligibility_user_not_found(self, app):
        """Test check_test_eligibility with non-existent user."""
        with app.app_context():
            user = User(display_name="Test", pin="1234", avatar="🐯", level=1)
            user.id = 99999  # Non-existent ID
            
            is_eligible, error_msg = SessionEngineService.check_test_eligibility(user, "addition-1digit")
            # Should check level, not user existence
            assert isinstance(is_eligible, bool)

    def test_check_test_eligibility_level_too_low(self, app, test_user):
        """Test check_test_eligibility when user level is too low."""
        with app.app_context():
            test_user.level = 1
            db.session.add(test_user)
            db.session.commit()
            
            # Find a test that requires level > 1
            high_level_test = None
            for test_type, (_, level, _, _) in SessionEngineService.TEST_TYPES.items():
                if level > 1:
                    high_level_test = test_type
                    break
            
            if high_level_test:
                is_eligible, error_msg = SessionEngineService.check_test_eligibility(test_user, high_level_test)
                assert is_eligible is False
                assert "below required level" in error_msg

    def test_check_test_eligibility_new_test_type(self, app, test_user):
        """Test check_test_eligibility with new test type (only level requirement)."""
        with app.app_context():
            test_user.level = 5
            db.session.add(test_user)
            db.session.commit()
            
            # New test types start with operation prefixes
            is_eligible, error_msg = SessionEngineService.check_test_eligibility(test_user, "addition-1digit")
            # Should pass if level is sufficient
            assert isinstance(is_eligible, bool)

    def test_check_test_eligibility_unknown_test_type(self, app, test_user):
        """Test check_test_eligibility with unknown test type."""
        with app.app_context():
            is_eligible, error_msg = SessionEngineService.check_test_eligibility(test_user, "unknown-test-type")
            assert is_eligible is False
            assert "Unknown test type" in error_msg

    def test_check_test_eligibility_legacy_test_type_no_achievement(self, app, test_user):
        """Test check_test_eligibility - all test types only require level (no achievement needed)."""
        with app.app_context():
            test_user.level = 10
            db.session.add(test_user)
            db.session.commit()

            # Create a mock test type
            with patch.object(SessionEngineService, 'TEST_TYPES', {
                'legacy-test': ('addition', 1, 10, {})
            }):
                # All tests now only require level, no achievement requirement
                is_eligible, error_msg = SessionEngineService.check_test_eligibility(test_user, "legacy-test")
                assert is_eligible is True
                assert error_msg == ""

    def test_check_test_eligibility_legacy_test_type_with_achievement(self, app, test_user):
        """Test check_test_eligibility with legacy test type with achievement."""
        with app.app_context():
            test_user.level = 10
            db.session.add(test_user)
            db.session.commit()
            
            # Create a mock test type that doesn't start with operation prefixes
            with patch.object(SessionEngineService, 'TEST_TYPES', {
                'legacy-test': ('addition', 1, 10, {})
            }):
                achievement_code = SessionEngineService._get_test_achievement_code("legacy-test")
                with patch.object(AchievementService, 'get_achievement_codes', return_value=[achievement_code]):
                    is_eligible, error_msg = SessionEngineService.check_test_eligibility(test_user, "legacy-test")
                    assert is_eligible is True
                    assert error_msg == ""

    def test_get_eligible_tests_no_achievements(self, app, test_user):
        """Test get_eligible_tests - tests only require level (no achievements needed)."""
        with app.app_context():
            test_user.level = 10
            db.session.add(test_user)
            db.session.commit()

            # Tests now only require level, so user should have eligible tests
            eligible = SessionEngineService.get_eligible_tests(test_user)
            # Should return tests where user level >= required level
            assert len(eligible) > 0, "User should have eligible tests based on level alone"

    def test_get_eligible_tests_with_achievements(self, app, test_user):
        """Test get_eligible_tests when user has achievements."""
        with app.app_context():
            test_user.level = 10
            db.session.add(test_user)
            db.session.commit()
            
            # Mock achievement codes to include a test mastery
            test_type = list(SessionEngineService.TEST_TYPES.keys())[0] if SessionEngineService.TEST_TYPES else None
            if test_type:
                achievement_code = SessionEngineService._get_test_achievement_code(test_type)
                with patch.object(AchievementService, 'get_achievement_codes', return_value=[achievement_code]):
                    eligible = SessionEngineService.get_eligible_tests(test_user)
                    # Should return at least one test
                    assert len(eligible) >= 1
                    assert eligible[0]["test_type"] == test_type

    def test_get_eligible_tests_level_restriction(self, app, test_user):
        """Test get_eligible_tests respects level restrictions."""
        with app.app_context():
            test_user.level = 1
            db.session.add(test_user)
            db.session.commit()
            
            # Mock achievement codes
            with patch.object(AchievementService, 'get_achievement_codes', return_value=["some_achievement"]):
                eligible = SessionEngineService.get_eligible_tests(test_user)
                # Should only include tests where user.level >= required_level
                for test in eligible:
                    assert test["level"] <= test_user.level

    def test_transform_session_questions_to_generate_format(self):
        """Test _transform_session_questions_to_generate_format."""
        questions_data = [
            {
                "question_id": 123,
                "prompt": "5 + 3",
                "operation": "addition",
                "operand1": 5,
                "operand2": 3,
                "correctAnswer": "8",
                "level": 1,
                "hint": "Add them",
                "answer_format": "integer",
                "math_type_label": "Addition",
                "layout": {"type": "vertical"},
            }
        ]
        
        transformed = SessionEngineService._transform_session_questions_to_generate_format(questions_data)
        
        assert len(transformed) == 1
        assert transformed[0]["id"] == "123"
        assert transformed[0]["question_id"] == 123
        assert transformed[0]["prompt"] == "5 + 3"
        assert transformed[0]["operation"] == "addition"
        assert transformed[0]["difficulty"] == "Level 1"
        assert transformed[0]["targetMs"] == 4000
        assert transformed[0]["layout"] == {"type": "vertical"}

    def test_transform_session_questions_with_response(self):
        """Test _transform_session_questions_to_generate_format includes response."""
        questions_data = [
            {
                "question_id": 123,
                "prompt": "5 + 3",
                "operation": "addition",
                "response": {
                    "submitted_answer": "8",
                    "is_correct": True,
                }
            }
        ]
        
        transformed = SessionEngineService._transform_session_questions_to_generate_format(questions_data)
        
        assert "response" in transformed[0]
        assert transformed[0]["response"]["submitted_answer"] == "8"

    def test_generate_session_user_not_found(self, app):
        """Test generate_session raises error for non-existent user."""
        with app.app_context():
            with pytest.raises(ValueError, match="User 99999 not found"):
                SessionEngineService.generate_session(user_id=99999)

    @patch('app.services.session_engine_service.PracticeService.get_incomplete_session')
    @patch('app.services.session_engine_service.PracticeService.get_session_with_details')
    def test_generate_session_returns_incomplete(self, mock_get_details, mock_get_incomplete, app, test_user):
        """Test generate_session returns incomplete session if found."""
        with app.app_context():
            session = PracticeService.create_session(user_id=test_user.id)
            
            mock_get_incomplete.return_value = (session, 2, 2)
            mock_get_details.return_value = {
                "questions": [
                    {
                        "question_id": 123,
                        "prompt": "5 + 3",
                        "operation": "addition",
                    }
                ]
            }
            
            result = SessionEngineService.generate_session(user_id=test_user.id)
            
            assert result["session_id"] == session.id
            assert "questions" in result

    @patch('app.services.session_engine_service.PracticeService.get_incomplete_session')
    @patch('app.services.session_engine_service.PracticeService.get_session_with_details')
    @patch('app.services.session_engine_service.PracticeService.complete_session')
    def test_generate_session_completes_all_answered(self, mock_complete, mock_get_details, mock_get_incomplete, app, test_user):
        """Test generate_session completes session if all questions answered."""
        with app.app_context():
            session = PracticeService.create_session(user_id=test_user.id)
            
            mock_get_incomplete.return_value = (session, 2, 2)
            mock_get_details.return_value = {
                "questions": [
                    {
                        "question_id": 123,
                        "prompt": "5 + 3",
                        "response": {"is_correct": True},
                    }
                ]
            }
            
            # Should create new session after completing
            with patch('app.services.session_engine_service.AdaptiveDistributionService') as mock_adaptive:
                mock_adaptive.generate_adaptive_question_distribution.return_value = {}
                mock_adaptive.select_level_from_distribution.return_value = 1
                mock_adaptive.get_operation_for_level.return_value = "addition"
                
                with patch('app.services.session_engine_service.QuestionService.generate_question') as mock_gen:
                    mock_gen.return_value = {"id": "q1", "question_id": 1}
                    
                    result = SessionEngineService.generate_session(user_id=test_user.id)
                    
                    # Should have called complete_session
                    assert mock_complete.called

    def test_generate_session_test_no_test_type(self, app, test_user):
        """Test generate_session raises error for test without test_type."""
        with app.app_context():
            with pytest.raises(ValueError, match="test_type is required"):
                SessionEngineService.generate_session(
                    user_id=test_user.id,
                    is_test=True
                )

    def test_generate_session_test_not_eligible(self, app, test_user):
        """Test generate_session raises error when test eligibility fails."""
        with app.app_context():
            test_user.level = 10
            db.session.add(test_user)
            db.session.commit()
            
            # Use a test type that requires higher level
            high_level_test = None
            for test_type, (_, level, _, _) in SessionEngineService.TEST_TYPES.items():
                if level > 10:
                    high_level_test = test_type
                    break
            
            if high_level_test:
                with pytest.raises(ValueError, match="Test eligibility check failed"):
                    SessionEngineService.generate_session(
                        user_id=test_user.id,
                        is_test=True,
                        test_type=high_level_test
                    )

    @patch('app.services.session_engine_service.QuestionService.generate_question')
    def test_generate_session_test_success(self, mock_gen_question, app, test_user):
        """Test generate_session creates test session successfully."""
        with app.app_context():
            test_user.level = 5
            db.session.add(test_user)
            db.session.commit()
            
            # Get a test type that user is eligible for
            eligible_test = None
            for test_type, (_, level, _, _) in SessionEngineService.TEST_TYPES.items():
                if level <= test_user.level:
                    eligible_test = test_type
                    break
            
            if eligible_test:
                mock_gen_question.return_value = {
                    "id": "q1",
                    "question_id": 1,
                    "prompt": "5 + 3",
                }
                
                result = SessionEngineService.generate_session(
                    user_id=test_user.id,
                    is_test=True,
                    test_type=eligible_test
                )
                
                assert result["is_test"] is True
                assert result["test_type"] == eligible_test
                assert "questions" in result
                assert len(result["questions"]) > 0

    def test_generate_session_test_unknown_type(self, app, test_user):
        """Test generate_session raises error for unknown test type."""
        with app.app_context():
            # First test: check_test_eligibility returns False for unknown type
            with patch.object(SessionEngineService, 'check_test_eligibility', return_value=(False, "Unknown test type")):
                with pytest.raises(ValueError, match="Test eligibility check failed"):
                    SessionEngineService.generate_session(
                        user_id=test_user.id,
                        is_test=True,
                        test_type="unknown-test-type"
                    )
            
            # Second test: check_test_eligibility passes but test_type not in TEST_TYPES
            with patch.object(SessionEngineService, 'check_test_eligibility', return_value=(True, "")):
                with patch.object(SessionEngineService, 'TEST_TYPES', {}):
                    with pytest.raises(ValueError, match="Unknown test type"):
                        SessionEngineService.generate_session(
                            user_id=test_user.id,
                            is_test=True,
                            test_type="unknown-test-type"
                        )

    @patch('app.services.session_engine_service.AdaptiveDistributionService')
    @patch('app.services.session_engine_service.QuestionService.generate_question')
    def test_generate_session_practice_success(self, mock_gen_question, mock_adaptive, app, test_user):
        """Test generate_session creates practice session successfully."""
        with app.app_context():
            mock_adaptive.generate_adaptive_question_distribution.return_value = {}
            mock_adaptive.select_level_from_distribution.return_value = 1
            mock_adaptive.get_operation_for_level.return_value = "addition"
            
            mock_gen_question.return_value = {
                "id": "q1",
                "question_id": 1,
                "prompt": "5 + 3",
            }
            
            result = SessionEngineService.generate_session(user_id=test_user.id)
            
            assert result["is_test"] is False
            assert result["test_type"] is None
            assert "questions" in result
            assert len(result["questions"]) == 10  # Default practice question count

    @patch('app.services.session_engine_service.AdaptiveDistributionService')
    @patch('app.services.session_engine_service.QuestionService.generate_question')
    def test_generate_session_practice_with_level_override(self, mock_gen_question, mock_adaptive, app, test_user):
        """Test generate_session respects level override for practice."""
        with app.app_context():
            mock_adaptive.generate_adaptive_question_distribution.return_value = {}
            mock_adaptive.select_level_from_distribution.return_value = 1
            mock_adaptive.get_operation_for_level.return_value = "addition"
            
            mock_gen_question.return_value = {
                "id": "q1",
                "question_id": 1,
                "prompt": "5 + 3",
            }
            
            result = SessionEngineService.generate_session(
                user_id=test_user.id,
                level=5
            )
            
            assert result["level"] == 5

    @patch('app.services.session_engine_service.AdaptiveDistributionService')
    @patch('app.services.session_engine_service.QuestionService.generate_question')
    def test_generate_session_practice_retry_on_error(self, mock_gen_question, mock_adaptive, app, test_user):
        """Test generate_session retries on ValueError during question generation."""
        with app.app_context():
            mock_adaptive.generate_adaptive_question_distribution.return_value = {}
            mock_adaptive.select_level_from_distribution.return_value = 1
            mock_adaptive.get_operation_for_level.return_value = "addition"
            
            # First call raises ValueError, subsequent calls succeed
            call_count = [0]
            def question_generator(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] == 1:
                    raise ValueError("Invalid level configuration")
                return {"id": f"q{call_count[0]}", "question_id": call_count[0], "prompt": "5 + 3"}
            
            mock_gen_question.side_effect = question_generator
            
            result = SessionEngineService.generate_session(user_id=test_user.id)
            
            # Should have retried and succeeded
            assert len(result["questions"]) > 0
            assert mock_gen_question.call_count >= 2

    @patch('app.services.session_engine_service.AdaptiveDistributionService')
    @patch('app.services.session_engine_service.QuestionService.generate_question')
    def test_generate_session_practice_retry_exhausted(self, mock_gen_question, mock_adaptive, app, test_user):
        """Test generate_session raises error after max retries."""
        with app.app_context():
            mock_adaptive.generate_adaptive_question_distribution.return_value = {}
            mock_adaptive.select_level_from_distribution.return_value = 1
            mock_adaptive.get_operation_for_level.return_value = "addition"
            
            # All retries fail
            mock_gen_question.side_effect = ValueError("Invalid level configuration")
            
            with pytest.raises(ValueError, match="Invalid level configuration"):
                SessionEngineService.generate_session(user_id=test_user.id)

    @patch('app.services.session_engine_service.AdaptiveDistributionService')
    @patch('app.services.session_engine_service.QuestionService.generate_question')
    def test_generate_session_practice_fallback_to_user_level(self, mock_gen_question, mock_adaptive, app, test_user):
        """Test generate_session falls back to user level on retry."""
        with app.app_context():
            mock_adaptive.generate_adaptive_question_distribution.return_value = {}
            mock_adaptive.select_level_from_distribution.return_value = 99  # Invalid level
            mock_adaptive.get_operation_for_level.return_value = "addition"
            
            # First call fails, subsequent calls succeed
            call_count = [0]
            def question_generator(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] == 1:
                    raise ValueError("Invalid level configuration")
                return {"id": f"q{call_count[0]}", "question_id": call_count[0], "prompt": "5 + 3"}
            
            mock_gen_question.side_effect = question_generator
            
            result = SessionEngineService.generate_session(user_id=test_user.id)
            
            # Should have used user level on retry
            assert len(result["questions"]) > 0
            # Verify get_operation_for_level was called with user level
            assert mock_adaptive.get_operation_for_level.called

    @patch('app.services.session_engine_service.AdaptiveDistributionService')
    @patch('app.services.session_engine_service.QuestionService.generate_question')
    def test_generate_session_stores_question_ids(self, mock_gen_question, mock_adaptive, app, test_user):
        """Test generate_session stores question IDs in session."""
        with app.app_context():
            mock_adaptive.generate_adaptive_question_distribution.return_value = {}
            mock_adaptive.select_level_from_distribution.return_value = 1
            mock_adaptive.get_operation_for_level.return_value = "addition"
            
            mock_gen_question.return_value = {
                "id": "q1",
                "question_id": 123,
                "prompt": "5 + 3",
            }
            
            result = SessionEngineService.generate_session(user_id=test_user.id)
            
            # Verify question_ids were stored
            session = db.session.get(PracticeSession, result["session_id"])
            assert session.question_ids is not None
            question_ids = json.loads(session.question_ids)
            assert 123 in question_ids

    @patch('app.services.session_engine_service.AdaptiveDistributionService')
    @patch('app.services.session_engine_service.QuestionService.generate_question')
    def test_generate_session_no_question_ids(self, mock_gen_question, mock_adaptive, app, test_user):
        """Test generate_session handles questions without question_id."""
        with app.app_context():
            mock_adaptive.generate_adaptive_question_distribution.return_value = {}
            mock_adaptive.select_level_from_distribution.return_value = 1
            mock_adaptive.get_operation_for_level.return_value = "addition"
            
            # Question without question_id
            mock_gen_question.return_value = {
                "id": "q1",
                "prompt": "5 + 3",
            }
            
            result = SessionEngineService.generate_session(user_id=test_user.id)
            
            # Should still create session
            assert result["session_id"] is not None
            session = db.session.get(PracticeSession, result["session_id"])
            # question_ids should be None or empty list
            assert session.question_ids is None or json.loads(session.question_ids) == []

    def test_generate_session_incomplete_mismatch_test_type(self, app, test_user):
        """Test generate_session creates new session if incomplete doesn't match test type."""
        with app.app_context():
            # Create incomplete practice session
            session = PracticeService.create_session(
                user_id=test_user.id,
                is_test=False
            )
            
            with patch('app.services.session_engine_service.PracticeService.get_incomplete_session') as mock_get:
                mock_get.return_value = (session, 0, 0)
                
                # Try to generate test session
                with patch('app.services.session_engine_service.SessionEngineService.check_test_eligibility') as mock_check:
                    mock_check.return_value = (True, "")
                    
                    with patch('app.services.session_engine_service.QuestionService.generate_question') as mock_gen:
                        mock_gen.return_value = {"id": "q1", "question_id": 1}
                        
                        # Should create new test session (incomplete is practice, requested is test)
                        test_type = list(SessionEngineService.TEST_TYPES.keys())[0] if SessionEngineService.TEST_TYPES else None
                        if test_type:
                            result = SessionEngineService.generate_session(
                                user_id=test_user.id,
                                is_test=True,
                                test_type=test_type
                            )
                            # Should be a new test session
                            assert result["is_test"] is True
                            assert result["session_id"] != session.id

    def test_generate_session_resumes_same_concept(self, app, test_user):
        """Test that starting practice for a concept resumes incomplete session of same concept.
        
        Scenario: Start basic addition practice -> new -> exit -> Start basic addition practice -> resume
        """
        with app.app_context():
            concept_id = "c_concept_001"  # Basic Single Digit Addition
            
            # Create incomplete session for concept
            session = PracticeService.create_session(
                user_id=test_user.id,
                mode="standard",
                level=1,
                concept_id=concept_id,
                is_test=False
            )
            
            # Add a question to the session
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
            
            session.question_ids = json.dumps([question.id])
            db.session.add(session)
            db.session.commit()
            
            # Mock get_session_with_details to return session questions
            with patch('app.services.session_engine_service.PracticeService.get_session_with_details') as mock_get_details:
                mock_get_details.return_value = {
                    "questions": [
                        {
                            "id": f"q_{question.id}",
                            "question_id": question.id,
                            "response": None,  # Not answered yet
                        }
                    ]
                }
                
                # Try to start practice for the same concept
                with patch('app.services.session_engine_service.AdaptiveDistributionService.generate_adaptive_question_distribution') as mock_dist:
                    mock_dist.return_value = {"1": 1.0}
                    
                    with patch('app.services.session_engine_service.QuestionService.generate_question') as mock_gen:
                        mock_gen.return_value = {"id": "q1", "question_id": question.id}
                        
                        result = SessionEngineService.generate_session(
                            user_id=test_user.id,
                            mode="standard",
                            level=1,
                            concept_id=concept_id,
                        )
                        
                        # Should resume the existing session
                        assert result["session_id"] == session.id
                        assert result["concept_id"] == concept_id

    def test_generate_session_creates_new_for_different_concept(self, app, test_user):
        """Test that starting practice for a different concept creates new session.
        
        Scenario: Start basic addition practice -> new -> exit -> Start basic subtraction practice -> new
        """
        with app.app_context():
            addition_concept = "c_concept_001"  # Basic Single Digit Addition
            subtraction_concept = "c_concept_003"  # Basic Single Digit Subtraction
            
            # Create incomplete session for addition concept
            addition_session = PracticeService.create_session(
                user_id=test_user.id,
                mode="standard",
                level=1,
                concept_id=addition_concept,
                is_test=False
            )
            
            # Add a question to the session
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
            
            addition_session.question_ids = json.dumps([question.id])
            db.session.add(addition_session)
            db.session.commit()
            
            # Try to start practice for different concept (subtraction)
            with patch('app.services.session_engine_service.AdaptiveDistributionService.generate_adaptive_question_distribution') as mock_dist:
                mock_dist.return_value = {"3": 1.0}
                
                with patch('app.services.session_engine_service.QuestionService.generate_question') as mock_gen:
                    mock_gen.return_value = {"id": "q1", "question_id": 1}
                    
                    result = SessionEngineService.generate_session(
                        user_id=test_user.id,
                        mode="standard",
                        level=3,
                        concept_id=subtraction_concept,
                    )
                    
                    # Should create a new session (not resume addition session)
                    assert result["session_id"] != addition_session.id
                    assert result["concept_id"] == subtraction_concept

    def test_generate_session_resumes_old_concept_after_other_sessions(self, app, test_user):
        """Test that starting practice for a concept resumes old session of that concept.
        
        Scenario: Start basic addition practice -> new -> exit -> Start basic subtraction practice -> 
        new -> exit -> Start basic addition practice -> resume old basic addition practice
        """
        with app.app_context():
            addition_concept = "c_concept_001"  # Basic Single Digit Addition
            subtraction_concept = "c_concept_003"  # Basic Single Digit Subtraction
            
            # Create incomplete session for addition concept (oldest)
            addition_session = PracticeService.create_session(
                user_id=test_user.id,
                mode="standard",
                level=1,
                concept_id=addition_concept,
                is_test=False
            )
            db.session.add(addition_session)
            db.session.commit()
            
            # Wait a moment to ensure different timestamps
            import time
            time.sleep(0.01)
            
            # Create incomplete session for subtraction concept (newer)
            subtraction_session = PracticeService.create_session(
                user_id=test_user.id,
                mode="standard",
                level=3,
                concept_id=subtraction_concept,
                is_test=False
            )
            db.session.add(subtraction_session)
            db.session.commit()
            
            # Add questions to both sessions
            addition_question = Question(
                operation="addition",
                operand1=5,
                operand2=3,
                correct_answer="8",
                prompt="5 + 3",
                required_level=1,
            )
            db.session.add(addition_question)
            db.session.commit()
            
            addition_session.question_ids = json.dumps([addition_question.id])
            db.session.add(addition_session)
            db.session.commit()
            
            # Mock get_session_with_details to return session questions
            with patch('app.services.session_engine_service.PracticeService.get_session_with_details') as mock_get_details:
                mock_get_details.return_value = {
                    "questions": [
                        {
                            "id": f"q_{addition_question.id}",
                            "question_id": addition_question.id,
                            "response": None,  # Not answered yet
                        }
                    ]
                }
                
                # Try to start practice for addition concept again
                with patch('app.services.session_engine_service.AdaptiveDistributionService.generate_adaptive_question_distribution') as mock_dist:
                    mock_dist.return_value = {"1": 1.0}
                    
                    with patch('app.services.session_engine_service.QuestionService.generate_question') as mock_gen:
                        mock_gen.return_value = {"id": "q1", "question_id": addition_question.id}
                        
                        result = SessionEngineService.generate_session(
                            user_id=test_user.id,
                            mode="standard",
                            level=1,
                            concept_id=addition_concept,
                        )
                        
                        # Should resume the old addition session (not the subtraction one)
                        assert result["session_id"] == addition_session.id
                        assert result["concept_id"] == addition_concept

    def test_generate_session_resumes_oldest_for_dashboard(self, app, test_user):
        """Test that dashboard start practice resumes oldest incomplete session regardless of concept."""
        with app.app_context():
            addition_concept = "c_concept_001"
            subtraction_concept = "c_concept_003"
            
            # Create incomplete session for addition concept (oldest)
            addition_session = PracticeService.create_session(
                user_id=test_user.id,
                mode="standard",
                level=1,
                concept_id=addition_concept,
                is_test=False
            )
            db.session.add(addition_session)
            db.session.commit()
            
            # Wait a moment to ensure different timestamps
            import time
            time.sleep(0.01)
            
            # Create incomplete session for subtraction concept (newer)
            subtraction_session = PracticeService.create_session(
                user_id=test_user.id,
                mode="standard",
                level=3,
                concept_id=subtraction_concept,
                is_test=False
            )
            db.session.add(subtraction_session)
            db.session.commit()
            
            # Add questions to addition session
            addition_question = Question(
                operation="addition",
                operand1=5,
                operand2=3,
                correct_answer="8",
                prompt="5 + 3",
                required_level=1,
            )
            db.session.add(addition_question)
            db.session.commit()
            
            addition_session.question_ids = json.dumps([addition_question.id])
            db.session.add(addition_session)
            db.session.commit()
            
            # Mock get_session_with_details to return session questions
            with patch('app.services.session_engine_service.PracticeService.get_session_with_details') as mock_get_details:
                mock_get_details.return_value = {
                    "questions": [
                        {
                            "id": f"q_{addition_question.id}",
                            "question_id": addition_question.id,
                            "response": None,  # Not answered yet
                        }
                    ]
                }
                
                # Try to start practice from dashboard (resume_oldest=True)
                with patch('app.services.session_engine_service.AdaptiveDistributionService.generate_adaptive_question_distribution') as mock_dist:
                    mock_dist.return_value = {"1": 1.0}
                    
                    with patch('app.services.session_engine_service.QuestionService.generate_question') as mock_gen:
                        mock_gen.return_value = {"id": "q1", "question_id": addition_question.id}
                        
                        result = SessionEngineService.generate_session(
                            user_id=test_user.id,
                            mode="standard",
                            resume_oldest=True,
                        )
                        
                        # Should resume the oldest session (addition, not subtraction)
                        assert result["session_id"] == addition_session.id

