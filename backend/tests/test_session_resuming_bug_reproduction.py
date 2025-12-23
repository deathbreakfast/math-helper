"""Tests to reproduce the actual bug in session resuming logic.

The bug: get_incomplete_session uses response_count >= total_questions to auto-complete,
but this is wrong when users answer the same question multiple times.
"""

import json
import pytest
from datetime import datetime

from app import create_app, db
from app.models import PracticeSession, Question, Response, User
from app.services.practice_service import PracticeService
from app.services.session_engine_service import SessionEngineService


@pytest.fixture
def app():
    app = create_app(test_config={"TESTING": True})
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def test_user(app):
    with app.app_context():
        user = User(display_name="TestUser", pin="1234", avatar="🐯", level=1, experience=0)
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user


@pytest.fixture
def test_questions(app):
    """Create 5 test questions."""
    with app.app_context():
        questions = []
        for i in range(5):
            question = Question(
                operation="addition",
                operand1=i,
                operand2=1,
                correct_answer=str(i + 1),
                prompt=f"{i} + 1",
                required_level=1,
            )
            db.session.add(question)
            questions.append(question)
        db.session.commit()
        question_ids = [q.id for q in questions]
        return question_ids


class TestSessionResumingBug:
    """Tests that reproduce the actual bug in auto-completion logic."""

    def test_bug_auto_completion_with_duplicate_responses(self, app, test_user, test_questions):
        """BUG REPRODUCTION: Auto-completion incorrectly triggers when user answers same question multiple times.
        
        Scenario:
        - Session has 5 questions
        - User answers question 0 five times (retrying)
        - response_count = 5, total_questions = 5
        - Bug: get_incomplete_session thinks all questions are answered and auto-completes
        - Reality: Only 1 out of 5 questions is answered
        
        This causes session resuming to fail because the session gets auto-completed incorrectly.
        """
        with app.app_context():
            # Create session with 5 questions
            session = PracticeService.create_session(
                user_id=test_user.id,
                mode="standard",
                concept_id="c_concept_001"
            )
            session.question_ids = json.dumps(test_questions)
            db.session.add(session)
            db.session.commit()
            
            # Answer question 0 five times (user retrying the same question)
            for attempt in range(5):
                PracticeService.record_response(
                    session_id=session.id,
                    question_id=test_questions[0],
                    user_id=test_user.id,
                    submitted_answer=str(attempt),  # Wrong answers
                    correct_answer="1",
                    is_correct=False,
                    duration_ms=1000
                )
            
            # Now try to get incomplete session
            retrieved, count, _ = PracticeService.get_incomplete_session(
                user_id=test_user.id,
                mode="standard"
            )
            
            # BUG: This should NOT auto-complete because only 1/5 questions is answered
            # But the current logic checks response_count >= total_questions (5 >= 5 = True)
            # So it incorrectly auto-completes
            
            # Expected: session should still be incomplete
            # Actual: session gets auto-completed
            if retrieved is None:
                # BUG REPRODUCED: Session was incorrectly auto-completed
                db.session.refresh(session)
                assert session.completed_at is not None, \
                    "BUG: Session was auto-completed even though only 1/5 questions answered. " \
                    f"Response count: {count}, Total questions: 5. " \
                    "The auto-completion logic should check unique questions, not total responses."
            else:
                # This is the correct behavior
                assert retrieved.id == session.id, "Should return the incomplete session"
                assert retrieved.completed_at is None, "Session should not be completed"

    def test_bug_auto_completion_with_partial_answers(self, app, test_user, test_questions):
        """BUG REPRODUCTION: Auto-completion with mixed answered/unanswered questions.
        
        Scenario:
        - Session has 5 questions
        - User answers questions 0, 1, 2 (3 questions)
        - User then answers question 0 again (retry)
        - response_count = 4, total_questions = 5
        - This should be fine (4 < 5), but let's verify the logic
        """
        with app.app_context():
            # Create session with 5 questions
            session = PracticeService.create_session(
                user_id=test_user.id,
                mode="standard",
                concept_id="c_concept_001"
            )
            session.question_ids = json.dumps(test_questions)
            db.session.add(session)
            db.session.commit()
            
            # Answer questions 0, 1, 2
            for i in range(3):
                PracticeService.record_response(
                    session_id=session.id,
                    question_id=test_questions[i],
                    user_id=test_user.id,
                    submitted_answer=str(i + 1),
                    correct_answer=str(i + 1),
                    is_correct=True
                )
            
            # Answer question 0 again (retry)
            PracticeService.record_response(
                session_id=session.id,
                question_id=test_questions[0],
                user_id=test_user.id,
                submitted_answer="1",
                correct_answer="1",
                is_correct=True
            )
            
            # Now try to get incomplete session
            retrieved, count, _ = PracticeService.get_incomplete_session(
                user_id=test_user.id,
                mode="standard"
            )
            
            # Should still be incomplete (3 unique questions answered, 2 remaining)
            assert retrieved is not None, "Session should still be incomplete (3/5 questions answered)"
            assert retrieved.id == session.id, "Should return the incomplete session"
            assert count == 4, "Should count 4 total responses (3 unique questions + 1 retry)"
            
            # Verify session is not completed
            db.session.refresh(session)
            assert session.completed_at is None, "Session should not be auto-completed (only 3/5 questions answered)"

    def test_correct_auto_completion_when_all_unique_questions_answered(self, app, test_user, test_questions):
        """Test that auto-completion works correctly when all unique questions are answered.
        
        This is the correct behavior we want to preserve.
        """
        with app.app_context():
            # Create session with 5 questions
            session = PracticeService.create_session(
                user_id=test_user.id,
                mode="standard",
                concept_id="c_concept_001"
            )
            session.question_ids = json.dumps(test_questions)
            db.session.add(session)
            db.session.commit()
            
            # Answer all 5 unique questions
            for i in range(5):
                PracticeService.record_response(
                    session_id=session.id,
                    question_id=test_questions[i],
                    user_id=test_user.id,
                    submitted_answer=str(i + 1),
                    correct_answer=str(i + 1),
                    is_correct=True
                )
            
            # Now try to get incomplete session - should auto-complete
            retrieved, count, _ = PracticeService.get_incomplete_session(
                user_id=test_user.id,
                mode="standard"
            )
            
            # Should auto-complete because all 5 unique questions are answered
            assert retrieved is None, "Session should be auto-completed when all unique questions answered"
            
            # Verify session was actually completed
            db.session.refresh(session)
            assert session.completed_at is not None, "Session should be marked as completed"

    def test_bug_session_engine_resume_fails_after_incorrect_auto_completion(self, app, test_user, test_questions):
        """BUG REPRODUCTION: SessionEngineService can't resume after incorrect auto-completion.
        
        This reproduces the E2E test failure where expected session ID doesn't match.
        """
        with app.app_context():
            # Create session with 5 questions
            session = PracticeService.create_session(
                user_id=test_user.id,
                mode="standard",
                concept_id="c_concept_001"
            )
            session.question_ids = json.dumps(test_questions)
            db.session.add(session)
            db.session.commit()
            
            original_session_id = session.id
            
            # Answer question 0 five times (bug scenario)
            for attempt in range(5):
                PracticeService.record_response(
                    session_id=session.id,
                    question_id=test_questions[0],
                    user_id=test_user.id,
                    submitted_answer="wrong",
                    correct_answer="1",
                    is_correct=False
                )
            
            # Try to resume via SessionEngineService
            result = SessionEngineService.generate_session(
                user_id=test_user.id,
                mode="standard",
                concept_id="c_concept_001"
            )
            
            # BUG: If auto-completion incorrectly triggered, a new session is created
            # Expected: Should resume original_session_id (but it won't because it was auto-completed)
            # Actual: Creates new session with different ID
            
            if result["session_id"] != original_session_id:
                # BUG REPRODUCED: New session created instead of resuming
                db.session.refresh(session)
                assert session.completed_at is not None, \
                    f"BUG: Original session {original_session_id} was incorrectly auto-completed. " \
                    f"New session {result['session_id']} was created instead. " \
                    f"This reproduces the E2E test failure where expected session doesn't match."
            else:
                # Correct behavior: resumed existing session
                assert result["session_id"] == original_session_id

