"""Comprehensive tests for PracticeService.

Tests cover all methods in PracticeService to achieve >80% coverage.
"""

import json
import pytest
from datetime import datetime

from app import create_app, db
from app.models import FlaggedQuestion, LevelProblemConfig, PracticeSession, Question, Response, User
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
        _ = user.id
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


class TestPracticeService:
    """Test suite for PracticeService static methods."""

    def test_create_session_basic(self, app, test_user):
        """Test create_session creates a basic session."""
        with app.app_context():
            session = PracticeService.create_session(
                user_id=test_user.id,
                mode="standard",
                level=1
            )
            
            assert session.id is not None
            assert session.user_id == test_user.id
            assert session.mode == "standard"
            assert session.level == 1
            assert session.is_test is False
            assert session.test_type is None
            assert session.started_at is not None
            assert session.completed_at is None

    def test_create_session_test_mode(self, app, test_user):
        """Test create_session creates a test session."""
        with app.app_context():
            session = PracticeService.create_session(
                user_id=test_user.id,
                mode="standard",
                level=1,
                is_test=True,
                test_type="addition-1digit"
            )
            
            assert session.is_test is True
            assert session.test_type == "addition-1digit"

    def test_complete_session(self, app, test_user):
        """Test complete_session marks session as completed with statistics."""
        with app.app_context():
            session = PracticeService.create_session(
                user_id=test_user.id,
                mode="standard",
                level=1
            )
            session_id = session.id
            
            completed = PracticeService.complete_session(
                session_id=session_id,
                total_questions=10,
                correct_count=8,
                total_duration_ms=50000
            )
            
            assert completed.completed_at is not None
            assert completed.total_questions == 10
            assert completed.correct_count == 8
            assert completed.accuracy == 80.0
            assert completed.total_duration_ms == 50000

    def test_complete_session_zero_questions(self, app, test_user):
        """Test complete_session handles zero questions."""
        with app.app_context():
            session = PracticeService.create_session(
                user_id=test_user.id,
                mode="standard",
                level=1
            )
            
            completed = PracticeService.complete_session(
                session_id=session.id,
                total_questions=0,
                correct_count=0,
                total_duration_ms=0
            )
            
            assert completed.accuracy == 0.0

    def test_complete_session_not_found(self, app):
        """Test complete_session raises error for non-existent session."""
        with app.app_context():
            with pytest.raises(ValueError, match="Session 99999 not found"):
                PracticeService.complete_session(
                    session_id=99999,
                    total_questions=10,
                    correct_count=8
                )

    def test_create_question_basic(self, app):
        """Test create_question creates a basic question."""
        with app.app_context():
            question = PracticeService.create_question(
                operation="addition",
                operand1=5,
                operand2=3,
                correct_answer="8",
                prompt="5 + 3",
                required_level=1
            )
            
            assert question.id is not None
            assert question.operation == "addition"
            assert question.operand1 == 5
            assert question.operand2 == 3
            assert question.correct_answer == "8"
            assert question.prompt == "5 + 3"
            assert question.required_level == 1

    def test_create_question_with_all_fields(self, app):
        """Test create_question with all optional fields."""
        with app.app_context():
            layout_config = {"type": "vertical"}
            accepted_answers = ["8", "eight"]
            
            question = PracticeService.create_question(
                operation="addition",
                operand1=5,
                operand2=3,
                correct_answer="8",
                prompt="5 + 3",
                required_level=1,
                difficulty="Level 1",
                level_tag="1",
                target_ms=4000,
                hint="Add the numbers",
                answer_format="integer",
                accepted_answers=accepted_answers,
                layout_type="vertical",
                layout_config=layout_config,
                math_type_label="Addition (Standard)"
            )
            
            assert question.difficulty == "Level 1"
            assert question.level_tag == "1"
            assert question.target_ms == 4000
            assert question.hint == "Add the numbers"
            assert question.answer_format == "integer"
            assert json.loads(question.accepted_answers) == accepted_answers
            assert question.layout_type == "vertical"
            assert json.loads(question.layout_config) == layout_config
            assert question.math_type_label == "Addition (Standard)"

    def test_get_question(self, app, test_question):
        """Test get_question retrieves a question by ID."""
        with app.app_context():
            retrieved = PracticeService.get_question(test_question.id)
            
            assert retrieved is not None
            assert retrieved.id == test_question.id
            assert retrieved.operation == "addition"

    def test_get_question_not_found(self, app):
        """Test get_question returns None for non-existent question."""
        with app.app_context():
            result = PracticeService.get_question(99999)
            assert result is None

    def test_get_questions_for_level(self, app):
        """Test get_questions_for_level retrieves questions for a level."""
        with app.app_context():
            # Create questions at different levels
            q1 = PracticeService.create_question(
                operation="addition",
                operand1=1,
                operand2=1,
                correct_answer="2",
                prompt="1 + 1",
                required_level=1
            )
            q2 = PracticeService.create_question(
                operation="addition",
                operand1=2,
                operand2=2,
                correct_answer="4",
                prompt="2 + 2",
                required_level=2
            )
            q3 = PracticeService.create_question(
                operation="addition",
                operand1=3,
                operand2=3,
                correct_answer="6",
                prompt="3 + 3",
                required_level=3
            )
            
            # Get questions for level 2 (should include level 1 and 2)
            questions = PracticeService.get_questions_for_level(level=2)
            question_ids = [q.id for q in questions]
            
            assert q1.id in question_ids
            assert q2.id in question_ids
            assert q3.id not in question_ids  # Level 3 > 2

    def test_get_questions_for_level_with_operation(self, app):
        """Test get_questions_for_level filters by operation."""
        with app.app_context():
            q1 = PracticeService.create_question(
                operation="addition",
                operand1=1,
                operand2=1,
                correct_answer="2",
                prompt="1 + 1",
                required_level=1
            )
            q2 = PracticeService.create_question(
                operation="subtraction",
                operand1=5,
                operand2=3,
                correct_answer="2",
                prompt="5 - 3",
                required_level=1
            )
            
            questions = PracticeService.get_questions_for_level(level=1, operation="addition")
            question_ids = [q.id for q in questions]
            
            assert q1.id in question_ids
            assert q2.id not in question_ids

    def test_get_questions_for_level_with_limit(self, app):
        """Test get_questions_for_level respects limit."""
        with app.app_context():
            # Create multiple questions
            for i in range(5):
                PracticeService.create_question(
                    operation="addition",
                    operand1=i,
                    operand2=i,
                    correct_answer=str(i + i),
                    prompt=f"{i} + {i}",
                    required_level=1
                )
            
            questions = PracticeService.get_questions_for_level(level=1, limit=3)
            assert len(questions) == 3

    def test_record_response(self, app, test_user, test_question):
        """Test record_response creates a response."""
        with app.app_context():
            session = PracticeService.create_session(user_id=test_user.id)
            
            response = PracticeService.record_response(
                session_id=session.id,
                question_id=test_question.id,
                user_id=test_user.id,
                submitted_answer="8",
                correct_answer="8",
                is_correct=True,
                duration_ms=2000
            )
            
            assert response.id is not None
            assert response.session_id == session.id
            assert response.question_id == test_question.id
            assert response.user_id == test_user.id
            assert response.submitted_answer == "8"
            assert response.correct_answer == "8"
            assert response.is_correct is True
            assert response.duration_ms == 2000
            assert response.is_flagged is False
            assert response.answered_at is not None

    def test_record_response_without_session(self, app, test_user, test_question):
        """Test record_response without session_id."""
        with app.app_context():
            response = PracticeService.record_response(
                session_id=None,
                question_id=test_question.id,
                user_id=test_user.id,
                submitted_answer="8",
                correct_answer="8",
                is_correct=True
            )
            
            assert response.session_id is None

    def test_record_response_flagged(self, app, test_user, test_question):
        """Test record_response with is_flagged=True."""
        with app.app_context():
            session = PracticeService.create_session(user_id=test_user.id)
            
            response = PracticeService.record_response(
                session_id=session.id,
                question_id=test_question.id,
                user_id=test_user.id,
                submitted_answer="8",
                correct_answer="8",
                is_correct=True,
                is_flagged=True
            )
            
            assert response.is_flagged is True

    def test_flag_question(self, app, test_user, test_question):
        """Test flag_question creates a flag."""
        with app.app_context():
            session = PracticeService.create_session(user_id=test_user.id)
            
            flagged = PracticeService.flag_question(
                user_id=test_user.id,
                question_id=test_question.id,
                session_id=session.id,
                notes="Need to review"
            )
            
            assert flagged.id is not None
            assert flagged.user_id == test_user.id
            assert flagged.question_id == test_question.id
            assert flagged.session_id == session.id
            assert flagged.notes == "Need to review"
            assert flagged.flagged_at is not None

    def test_flag_question_already_flagged(self, app, test_user, test_question):
        """Test flag_question returns existing flag if already flagged."""
        with app.app_context():
            session = PracticeService.create_session(user_id=test_user.id)
            
            flagged1 = PracticeService.flag_question(
                user_id=test_user.id,
                question_id=test_question.id,
                session_id=session.id
            )
            
            flagged2 = PracticeService.flag_question(
                user_id=test_user.id,
                question_id=test_question.id,
                session_id=session.id
            )
            
            assert flagged1.id == flagged2.id  # Same flag returned

    def test_unflag_question(self, app, test_user, test_question):
        """Test unflag_question removes a flag."""
        with app.app_context():
            session = PracticeService.create_session(user_id=test_user.id)
            
            PracticeService.flag_question(
                user_id=test_user.id,
                question_id=test_question.id,
                session_id=session.id
            )
            
            result = PracticeService.unflag_question(
                user_id=test_user.id,
                question_id=test_question.id,
                session_id=session.id
            )
            
            assert result is True
            
            # Verify flag is removed
            flagged = FlaggedQuestion.query.filter_by(
                user_id=test_user.id,
                question_id=test_question.id,
                session_id=session.id
            ).first()
            assert flagged is None

    def test_unflag_question_not_flagged(self, app, test_user, test_question):
        """Test unflag_question returns False if question not flagged."""
        with app.app_context():
            result = PracticeService.unflag_question(
                user_id=test_user.id,
                question_id=test_question.id
            )
            
            assert result is False

    def test_get_flagged_questions(self, app, test_user):
        """Test get_flagged_questions retrieves all flagged questions."""
        with app.app_context():
            session = PracticeService.create_session(user_id=test_user.id)
            
            # Create multiple questions
            q1 = PracticeService.create_question(
                operation="addition",
                operand1=1,
                operand2=1,
                correct_answer="2",
                prompt="1 + 1",
                required_level=1
            )
            q2 = PracticeService.create_question(
                operation="addition",
                operand1=2,
                operand2=2,
                correct_answer="4",
                prompt="2 + 2",
                required_level=1
            )
            
            # Flag both questions
            PracticeService.flag_question(
                user_id=test_user.id,
                question_id=q1.id,
                session_id=session.id
            )
            PracticeService.flag_question(
                user_id=test_user.id,
                question_id=q2.id,
                session_id=session.id
            )
            
            flagged = PracticeService.get_flagged_questions(user_id=test_user.id)
            
            assert len(flagged) == 2
            question_ids = [f.question_id for f in flagged]
            assert q1.id in question_ids
            assert q2.id in question_ids

    def test_get_flagged_questions_with_session(self, app, test_user):
        """Test get_flagged_questions filters by session_id."""
        with app.app_context():
            session1 = PracticeService.create_session(user_id=test_user.id)
            session2 = PracticeService.create_session(user_id=test_user.id)
            
            q1 = PracticeService.create_question(
                operation="addition",
                operand1=1,
                operand2=1,
                correct_answer="2",
                prompt="1 + 1",
                required_level=1
            )
            
            # Flag in session1
            PracticeService.flag_question(
                user_id=test_user.id,
                question_id=q1.id,
                session_id=session1.id
            )
            
            # Get flags for session1 only
            flagged = PracticeService.get_flagged_questions(
                user_id=test_user.id,
                session_id=session1.id
            )
            
            assert len(flagged) == 1
            assert flagged[0].session_id == session1.id

    def test_get_level_problem_config(self, app):
        """Test get_level_problem_config retrieves config for a level."""
        with app.app_context():
            config = PracticeService.create_level_problem_config(
                level=1,
                operation="addition",
                min_operand1=1,
                max_operand1=10,
                min_operand2=1,
                max_operand2=10
            )
            
            configs = PracticeService.get_level_problem_config(level=1)
            
            assert len(configs) == 1
            assert configs[0].id == config.id

    def test_get_level_problem_config_with_operation(self, app):
        """Test get_level_problem_config filters by operation."""
        with app.app_context():
            PracticeService.create_level_problem_config(
                level=1,
                operation="addition"
            )
            PracticeService.create_level_problem_config(
                level=1,
                operation="subtraction"
            )
            
            configs = PracticeService.get_level_problem_config(level=1, operation="addition")
            
            assert len(configs) == 1
            assert configs[0].operation == "addition"

    def test_get_level_problem_config_only_available(self, app):
        """Test get_level_problem_config only returns available configs."""
        with app.app_context():
            PracticeService.create_level_problem_config(
                level=1,
                operation="addition",
                is_available=True
            )
            PracticeService.create_level_problem_config(
                level=1,
                operation="subtraction",
                is_available=False
            )
            
            configs = PracticeService.get_level_problem_config(level=1)
            
            assert len(configs) == 1
            assert configs[0].operation == "addition"

    def test_create_level_problem_config_new(self, app):
        """Test create_level_problem_config creates a new config."""
        with app.app_context():
            config = PracticeService.create_level_problem_config(
                level=1,
                operation="addition",
                min_operand1=1,
                max_operand1=10,
                min_operand2=1,
                max_operand2=10,
                layout_types=["vertical", "horizontal"],
                answer_formats=["integer", "remainder"]
            )
            
            assert config.id is not None
            assert config.level == 1
            assert config.operation == "addition"
            assert config.min_operand1 == 1
            assert config.max_operand1 == 10
            assert json.loads(config.layout_types) == ["vertical", "horizontal"]
            assert json.loads(config.answer_formats) == ["integer", "remainder"]

    def test_create_level_problem_config_update_existing(self, app):
        """Test create_level_problem_config updates existing config."""
        with app.app_context():
            # Create initial config
            config1 = PracticeService.create_level_problem_config(
                level=1,
                operation="addition",
                min_operand1=1,
                max_operand1=5
            )
            
            # Update it
            config2 = PracticeService.create_level_problem_config(
                level=1,
                operation="addition",
                min_operand1=1,
                max_operand1=10
            )
            
            assert config1.id == config2.id  # Same config
            assert config2.max_operand1 == 10  # Updated value

    def test_get_incomplete_session_no_session(self, app, test_user):
        """Test get_incomplete_session returns None when no incomplete session exists."""
        with app.app_context():
            session, response_count, _ = PracticeService.get_incomplete_session(
                user_id=test_user.id
            )
            
            assert session is None
            assert response_count == 0

    def test_get_incomplete_session_with_incomplete(self, app, test_user):
        """Test get_incomplete_session returns incomplete session."""
        with app.app_context():
            session = PracticeService.create_session(user_id=test_user.id)
            
            retrieved, response_count, _ = PracticeService.get_incomplete_session(
                user_id=test_user.id
            )
            
            assert retrieved is not None
            assert retrieved.id == session.id
            assert response_count == 0

    def test_get_incomplete_session_with_responses(self, app, test_user, test_question):
        """Test get_incomplete_session counts responses."""
        with app.app_context():
            session = PracticeService.create_session(user_id=test_user.id)
            
            # Add a response
            PracticeService.record_response(
                session_id=session.id,
                question_id=test_question.id,
                user_id=test_user.id,
                submitted_answer="8",
                correct_answer="8",
                is_correct=True
            )
            
            retrieved, response_count, _ = PracticeService.get_incomplete_session(
                user_id=test_user.id
            )
            
            assert retrieved is not None
            assert response_count == 1

    def test_get_incomplete_session_with_mode_filter(self, app, test_user):
        """Test get_incomplete_session filters by mode."""
        with app.app_context():
            session1 = PracticeService.create_session(
                user_id=test_user.id,
                mode="standard"
            )
            session2 = PracticeService.create_session(
                user_id=test_user.id,
                mode="multiplication"
            )
            
            retrieved, _, _ = PracticeService.get_incomplete_session(
                user_id=test_user.id,
                mode="multiplication"
            )
            
            assert retrieved is not None
            assert retrieved.id == session2.id
            assert retrieved.mode == "multiplication"

    def test_get_incomplete_session_auto_completes_all_answered(self, app, test_user):
        """Test get_incomplete_session auto-completes session when all questions answered."""
        with app.app_context():
            session = PracticeService.create_session(user_id=test_user.id)
            question = PracticeService.create_question(
                operation="addition",
                operand1=1,
                operand2=1,
                correct_answer="2",
                prompt="1 + 1",
                required_level=1
            )
            
            # Set question_ids on session
            session.question_ids = json.dumps([question.id])
            db.session.add(session)
            db.session.commit()
            
            # Add response for the question
            PracticeService.record_response(
                session_id=session.id,
                question_id=question.id,
                user_id=test_user.id,
                submitted_answer="2",
                correct_answer="2",
                is_correct=True
            )
            
            # Should auto-complete and return None
            retrieved, response_count, _ = PracticeService.get_incomplete_session(
                user_id=test_user.id
            )
            
            assert retrieved is None
            assert response_count == 0
            
            # Verify session was completed
            db.session.refresh(session)
            assert session.completed_at is not None

    def test_get_incomplete_session_invalid_question_ids_json(self, app, test_user):
        """Test get_incomplete_session handles invalid question_ids JSON."""
        with app.app_context():
            session = PracticeService.create_session(user_id=test_user.id)
            session.question_ids = "invalid json"
            db.session.add(session)
            db.session.commit()
            
            # Should still return session (fallback behavior)
            retrieved, response_count, _ = PracticeService.get_incomplete_session(
                user_id=test_user.id
            )
            
            assert retrieved is not None
            assert retrieved.id == session.id

    def test_get_session_with_details_not_found(self, app):
        """Test get_session_with_details returns None for non-existent session."""
        with app.app_context():
            result = PracticeService.get_session_with_details(99999)
            assert result is None

    def test_get_session_with_details_basic(self, app, test_user, test_question):
        """Test get_session_with_details returns session with questions."""
        with app.app_context():
            session = PracticeService.create_session(user_id=test_user.id)
            session.question_ids = json.dumps([test_question.id])
            db.session.add(session)
            db.session.commit()
            
            result = PracticeService.get_session_with_details(session.id)
            
            assert result is not None
            assert result["session"]["id"] == session.id
            assert len(result["questions"]) == 1
            assert result["questions"][0]["question_id"] == test_question.id

    def test_get_session_with_details_with_responses(self, app, test_user, test_question):
        """Test get_session_with_details includes responses."""
        with app.app_context():
            session = PracticeService.create_session(user_id=test_user.id)
            session.question_ids = json.dumps([test_question.id])
            db.session.add(session)
            db.session.commit()
            
            # Add response
            PracticeService.record_response(
                session_id=session.id,
                question_id=test_question.id,
                user_id=test_user.id,
                submitted_answer="8",
                correct_answer="8",
                is_correct=True,
                duration_ms=2000
            )
            
            result = PracticeService.get_session_with_details(session.id)
            
            assert result["questions"][0]["response"] is not None
            assert result["questions"][0]["response"]["submitted_answer"] == "8"
            assert result["questions"][0]["response"]["is_correct"] is True

    def test_get_session_with_details_orders_answered_first(self, app, test_user):
        """Test get_session_with_details orders answered questions first."""
        with app.app_context():
            session = PracticeService.create_session(user_id=test_user.id)
            
            # Create two questions
            q1 = PracticeService.create_question(
                operation="addition",
                operand1=1,
                operand2=1,
                correct_answer="2",
                prompt="1 + 1",
                required_level=1
            )
            q2 = PracticeService.create_question(
                operation="addition",
                operand1=2,
                operand2=2,
                correct_answer="4",
                prompt="2 + 2",
                required_level=1
            )
            
            session.question_ids = json.dumps([q1.id, q2.id])
            db.session.add(session)
            db.session.commit()
            
            # Answer q2 first, then q1
            from datetime import datetime, timedelta
            response2 = PracticeService.record_response(
                session_id=session.id,
                question_id=q2.id,
                user_id=test_user.id,
                submitted_answer="4",
                correct_answer="4",
                is_correct=True
            )
            # Set answered_at to be earlier
            response2.answered_at = datetime.utcnow() - timedelta(minutes=1)
            db.session.add(response2)
            db.session.commit()
            
            response1 = PracticeService.record_response(
                session_id=session.id,
                question_id=q1.id,
                user_id=test_user.id,
                submitted_answer="2",
                correct_answer="2",
                is_correct=True
            )
            
            result = PracticeService.get_session_with_details(session.id)
            
            # Answered questions should come first, ordered by answered_at (most recent first)
            # So q1 (answered later) should come before q2 (answered earlier)
            assert result["questions"][0]["question_id"] == q1.id
            assert result["questions"][1]["question_id"] == q2.id

    def test_get_session_with_details_backward_compatibility(self, app, test_user, test_question):
        """Test get_session_with_details works without question_ids (backward compatibility)."""
        with app.app_context():
            session = PracticeService.create_session(user_id=test_user.id)
            # Don't set question_ids
            
            # Add response (this creates the question reference)
            PracticeService.record_response(
                session_id=session.id,
                question_id=test_question.id,
                user_id=test_user.id,
                submitted_answer="8",
                correct_answer="8",
                is_correct=True
            )
            
            result = PracticeService.get_session_with_details(session.id)
            
            # Should infer questions from responses
            assert len(result["questions"]) == 1
            assert result["questions"][0]["question_id"] == test_question.id

    def test_get_session_with_details_invalid_json_fallback(self, app, test_user, test_question):
        """Test get_session_with_details handles invalid question_ids JSON."""
        with app.app_context():
            session = PracticeService.create_session(user_id=test_user.id)
            session.question_ids = "invalid json {"
            db.session.add(session)
            db.session.commit()
            
            # Add response so we can infer from responses
            PracticeService.record_response(
                session_id=session.id,
                question_id=test_question.id,
                user_id=test_user.id,
                submitted_answer="8",
                correct_answer="8",
                is_correct=True
            )
            
            result = PracticeService.get_session_with_details(session.id)
            
            # Should fall back to inferring from responses
            assert len(result["questions"]) == 1
            assert result["questions"][0]["question_id"] == test_question.id

    def test_validate_answer_direct_match(self, app, test_question):
        """Test validate_answer with direct match."""
        with app.app_context():
            result = PracticeService.validate_answer(test_question, "8")
            assert result is True

    def test_validate_answer_remainder_format(self, app):
        """Test validate_answer with remainder format."""
        with app.app_context():
            question = PracticeService.create_question(
                operation="division",
                operand1=10,
                operand2=3,
                correct_answer="3 R 1",
                prompt="10 ÷ 3",
                required_level=1,
                answer_format="remainder"
            )
            
            # Test various formats
            assert PracticeService.validate_answer(question, "3 R 1") is True
            assert PracticeService.validate_answer(question, "3r1") is True
            assert PracticeService.validate_answer(question, "3 R1") is True
            assert PracticeService.validate_answer(question, "3r 1") is True
            assert PracticeService.validate_answer(question, "4") is False

    def test_validate_answer_fraction_format(self, app):
        """Test validate_answer with fraction format."""
        with app.app_context():
            question = PracticeService.create_question(
                operation="division",
                operand1=1,
                operand2=2,
                correct_answer="1/2",
                prompt="1 ÷ 2",
                required_level=1,
                answer_format="fraction"
            )
            
            assert PracticeService.validate_answer(question, "1/2") is True
            assert PracticeService.validate_answer(question, "2/4") is True  # Equivalent fraction
            # Note: "0.5" might match as decimal before fraction check, so test with non-decimal
            assert PracticeService.validate_answer(question, "invalid") is False

    def test_validate_answer_decimal_format(self, app):
        """Test validate_answer with decimal format."""
        with app.app_context():
            question = PracticeService.create_question(
                operation="division",
                operand1=1,
                operand2=2,
                correct_answer="0.5",
                prompt="1 ÷ 2",
                required_level=1,
                answer_format="decimal"
            )
            
            assert PracticeService.validate_answer(question, "0.5") is True
            assert PracticeService.validate_answer(question, "0.50") is True  # Within tolerance
            # Tolerance check: abs(submitted - correct) < 0.01
            # 0.5 - 0.51 = -0.01, abs(-0.01) = 0.01, and 0.01 < 0.01 is False
            # So 0.51 is outside tolerance (boundary is exclusive)
            assert PracticeService.validate_answer(question, "0.509") is True  # Within tolerance (0.009 < 0.01)
            assert PracticeService.validate_answer(question, "0.51") is False  # At boundary (0.01 is NOT < 0.01)
            assert PracticeService.validate_answer(question, "0.52") is False  # Outside tolerance
            assert PracticeService.validate_answer(question, "invalid") is False

    def test_validate_answer_with_accepted_answers(self, app):
        """Test validate_answer checks accepted_answers."""
        with app.app_context():
            question = PracticeService.create_question(
                operation="addition",
                operand1=5,
                operand2=3,
                correct_answer="8",
                prompt="5 + 3",
                required_level=1,
                accepted_answers=["8", "eight", "VIII"]
            )
            
            assert PracticeService.validate_answer(question, "8") is True
            assert PracticeService.validate_answer(question, "eight") is True
            assert PracticeService.validate_answer(question, "VIII") is True
            assert PracticeService.validate_answer(question, "9") is False

    def test_validate_answer_invalid_accepted_answers_json(self, app):
        """Test validate_answer handles invalid accepted_answers JSON."""
        with app.app_context():
            question = PracticeService.create_question(
                operation="addition",
                operand1=5,
                operand2=3,
                correct_answer="8",
                prompt="5 + 3",
                required_level=1
            )
            question.accepted_answers = "invalid json"
            db.session.add(question)
            db.session.commit()
            
            # Should still work with direct match
            assert PracticeService.validate_answer(question, "8") is True
            assert PracticeService.validate_answer(question, "9") is False

    def test_validate_answer_strips_whitespace(self, app, test_question):
        """Test validate_answer strips whitespace from answers."""
        with app.app_context():
            assert PracticeService.validate_answer(test_question, " 8 ") is True
            assert PracticeService.validate_answer(test_question, "8\n") is True

    def test_get_incomplete_session_with_concept_id_filter(self, app, test_user):
        """Test get_incomplete_session filters by concept_id."""
        with app.app_context():
            # Create sessions with different concept_ids
            session1 = PracticeService.create_session(
                user_id=test_user.id,
                mode="standard",
                concept_id="c_level_1"
            )
            session2 = PracticeService.create_session(
                user_id=test_user.id,
                mode="standard",
                concept_id="c_level_3"
            )
            
            # Get incomplete session with concept_id filter
            result, count, _ = PracticeService.get_incomplete_session(
                test_user.id, 
                mode="standard",
                concept_id="c_level_1"
            )
            
            # Should return the session with matching concept_id
            assert result is not None
            assert result.id == session1.id
            assert result.concept_id == "c_level_1"

    def test_get_oldest_incomplete_session(self, app, test_user):
        """Test get_oldest_incomplete_session returns oldest session."""
        with app.app_context():
            import time
            
            # Create first session (oldest)
            session1 = PracticeService.create_session(
                user_id=test_user.id,
                mode="standard",
                concept_id="c_level_1"
            )
            db.session.add(session1)
            db.session.commit()
            
            # Wait a moment to ensure different timestamps
            time.sleep(0.01)
            
            # Create second session (newer)
            session2 = PracticeService.create_session(
                user_id=test_user.id,
                mode="standard",
                concept_id="c_level_3"
            )
            db.session.add(session2)
            db.session.commit()
            
            # Get oldest incomplete session
            result, count, _ = PracticeService.get_oldest_incomplete_session(test_user.id, mode="standard")
            
            # Should return the oldest session (session1)
            assert result is not None
            assert result.id == session1.id

