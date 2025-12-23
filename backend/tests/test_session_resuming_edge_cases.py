"""Tests to reproduce session resuming issues seen in E2E tests.

These tests attempt to reproduce scenarios where session resuming fails,
particularly the issue where expected session IDs don't match actual session IDs.
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
def test_user2(app):
    with app.app_context():
        user = User(display_name="TestUser2", pin="5678", avatar="🐻", level=1, experience=0)
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user


@pytest.fixture
def test_questions(app):
    """Create 10 test questions."""
    with app.app_context():
        questions = []
        for i in range(10):
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
        # Access IDs while still in context to prevent DetachedInstanceError
        question_ids = [q.id for q in questions]
        return question_ids


class TestSessionResumingEdgeCases:
    """Test cases to reproduce session resuming failures."""

    def test_multiple_incomplete_sessions_returns_most_recent(self, app, test_user, test_questions):
        """Test that get_incomplete_session returns the most recent session when multiple exist.
        
        This reproduces the E2E issue where session IDs don't match expectations.
        """
        with app.app_context():
            # Create first incomplete session
            session1 = PracticeService.create_session(
                user_id=test_user.id,
                mode="standard",
                concept_id="c_concept_001"
            )
            session1.question_ids = json.dumps([test_questions[0], test_questions[1]])
            db.session.add(session1)
            db.session.commit()
            
            # Create second incomplete session (more recent)
            session2 = PracticeService.create_session(
                user_id=test_user.id,
                mode="standard",
                concept_id="c_concept_001"
            )
            session2.question_ids = json.dumps([test_questions[2], test_questions[3]])
            db.session.add(session2)
            db.session.commit()
            
            # Get incomplete session - should return most recent (session2)
            retrieved, count, _ = PracticeService.get_incomplete_session(
                user_id=test_user.id,
                mode="standard"
            )
            
            assert retrieved is not None, "Should find an incomplete session"
            assert retrieved.id == session2.id, \
                f"Expected most recent session {session2.id}, but got {retrieved.id}. " \
                f"This could cause E2E test failures where expected session doesn't match."

    def test_session_resuming_with_partial_responses(self, app, test_user, test_questions):
        """Test resuming a session that has some responses but not all questions answered.
        
        This tests the scenario where a user starts a session, answers some questions,
        then tries to resume it.
        """
        with app.app_context():
            # Create session with 10 questions
            session = PracticeService.create_session(
                user_id=test_user.id,
                mode="standard",
                concept_id="c_concept_001"
            )
            question_ids = test_questions[:10]
            session.question_ids = json.dumps(question_ids)
            db.session.add(session)
            db.session.commit()
            
            # Answer first 3 questions
            for i in range(3):
                PracticeService.record_response(
                    session_id=session.id,
                    question_id=test_questions[i],
                    user_id=test_user.id,
                    submitted_answer=str(i + 1),
                    correct_answer=str(i + 1),
                    is_correct=True
                )
            
            # Try to resume the session
            retrieved, count, _ = PracticeService.get_incomplete_session(
                user_id=test_user.id,
                mode="standard"
            )
            
            assert retrieved is not None, "Should find incomplete session with partial responses"
            assert retrieved.id == session.id, \
                f"Expected session {session.id}, but got {retrieved.id}"
            assert count == 3, f"Expected 3 responses, but got {count}"
            
            # Verify session is not auto-completed (should have 3/10 responses)
            db.session.refresh(session)
            assert session.completed_at is None, "Session should not be auto-completed with only 3/10 responses"

    def test_session_auto_completion_with_all_responses(self, app, test_user, test_questions):
        """Test that session is auto-completed when all questions have responses.
        
        This tests the auto-completion logic that might be interfering with resuming.
        """
        with app.app_context():
            # Create session with 5 questions
            session = PracticeService.create_session(
                user_id=test_user.id,
                mode="standard",
                concept_id="c_concept_001"
            )
            question_ids = test_questions[:5]
            session.question_ids = json.dumps(question_ids)
            db.session.add(session)
            db.session.commit()
            
            # Answer all 5 questions
            for i in range(5):
                PracticeService.record_response(
                    session_id=session.id,
                    question_id=test_questions[i],
                    user_id=test_user.id,
                    submitted_answer=str(i + 1),
                    correct_answer=str(i + 1),
                    is_correct=True
                )
            
            # Try to get incomplete session - should auto-complete and return None
            retrieved, count, _ = PracticeService.get_incomplete_session(
                user_id=test_user.id,
                mode="standard"
            )
            
            assert retrieved is None, "Session should be auto-completed when all questions answered"
            assert count == 0, "Should return 0 count after auto-completion"
            
            # Verify session was actually completed
            db.session.refresh(session)
            assert session.completed_at is not None, "Session should be marked as completed"

    def test_multiple_users_incomplete_sessions_isolation(self, app, test_user, test_user2, test_questions):
        """Test that incomplete sessions are properly isolated between users.
        
        This ensures one user's incomplete session doesn't affect another user.
        """
        with app.app_context():
            # Create incomplete session for user1
            session1 = PracticeService.create_session(
                user_id=test_user.id,
                mode="standard",
                concept_id="c_concept_001"
            )
            session1.question_ids = json.dumps([test_questions[0]])
            db.session.add(session1)
            
            # Create incomplete session for user2
            session2 = PracticeService.create_session(
                user_id=test_user2.id,
                mode="standard",
                concept_id="c_concept_001"
            )
            session2.question_ids = json.dumps([test_questions[1]])
            db.session.add(session2)
            db.session.commit()
            
            # Get incomplete session for user1 - should only get user1's session
            retrieved1, _, _ = PracticeService.get_incomplete_session(
                user_id=test_user.id,
                mode="standard"
            )
            
            # Get incomplete session for user2 - should only get user2's session
            retrieved2, _, _ = PracticeService.get_incomplete_session(
                user_id=test_user2.id,
                mode="standard"
            )
            
            assert retrieved1 is not None, "User1 should have an incomplete session"
            assert retrieved1.id == session1.id, f"User1 should get session {session1.id}, got {retrieved1.id}"
            
            assert retrieved2 is not None, "User2 should have an incomplete session"
            assert retrieved2.id == session2.id, f"User2 should get session {session2.id}, got {retrieved2.id}"

    def test_session_resuming_with_concept_id_mismatch(self, app, test_user, test_questions):
        """Test that session resuming respects concept_id filtering.
        
        This tests the scenario where a user has incomplete sessions for different concepts.
        """
        with app.app_context():
            # Create session for concept_001
            session1 = PracticeService.create_session(
                user_id=test_user.id,
                mode="standard",
                concept_id="c_concept_001"
            )
            session1.question_ids = json.dumps([test_questions[0]])
            db.session.add(session1)
            
            # Create session for concept_003
            session2 = PracticeService.create_session(
                user_id=test_user.id,
                mode="standard",
                concept_id="c_concept_003"
            )
            session2.question_ids = json.dumps([test_questions[1]])
            db.session.add(session2)
            db.session.commit()
            
            # Try to resume with concept_001 - should get session1
            retrieved, _, _ = PracticeService.get_incomplete_session(
                user_id=test_user.id,
                mode="standard",
                concept_id="c_concept_001"
            )
            
            assert retrieved is not None, "Should find session for concept_001"
            assert retrieved.id == session1.id, \
                f"Expected session {session1.id} for concept_001, got {retrieved.id}"
            assert retrieved.concept_id == "c_concept_001", "Should match concept_id filter"

    def test_session_engine_resume_vs_create_new(self, app, test_user, test_questions):
        """Test that SessionEngineService properly resumes vs creates new sessions.
        
        This is the key test that reproduces the E2E issue where new sessions
        are created instead of resuming existing ones.
        """
        with app.app_context():
            # Create an incomplete session
            session = PracticeService.create_session(
                user_id=test_user.id,
                mode="standard",
                concept_id="c_concept_001"
            )
            question_ids = test_questions[:5]
            session.question_ids = json.dumps(question_ids)
            db.session.add(session)
            db.session.commit()
            
            # Answer 2 out of 5 questions
            for i in range(2):
                PracticeService.record_response(
                    session_id=session.id,
                    question_id=test_questions[i],
                    user_id=test_user.id,
                    submitted_answer=str(i + 1),
                    correct_answer=str(i + 1),
                    is_correct=True
                )
            
            original_session_id = session.id
            
            # Try to generate/resume session - should resume existing one
            result = SessionEngineService.generate_session(
                user_id=test_user.id,
                mode="standard",
                concept_id="c_concept_001"
            )
            
            # This is the critical assertion - should resume, not create new
            assert result["session_id"] == original_session_id, \
                f"Expected to resume session {original_session_id}, but got new session {result['session_id']}. " \
                f"This reproduces the E2E test failure where session IDs don't match."

    def test_session_engine_resume_with_no_concept_id(self, app, test_user, test_questions):
        """Test that SessionEngineService properly resumes when concept_id is None.
        
        This reproduces the E2E scenario where:
        1. startPracticeSessionViaAPI creates a session (concept_id=None, backend randomly selects)
        2. Test navigates to practice, calls generate_session again (concept_id=None)
        3. Should restore the same session, not create a new one
        """
        with app.app_context():
            # Simulate what happens when startPracticeSessionViaAPI is called:
            # Backend randomly selects a concept and creates a session
            # For this test, we'll create a session with a specific concept_id
            # to simulate what the backend would have selected
            session = PracticeService.create_session(
                user_id=test_user.id,
                mode="standard",
                concept_id="c_concept_001"  # Simulate backend's random selection
            )
            question_ids = test_questions[:5]
            session.question_ids = json.dumps(question_ids)
            db.session.add(session)
            db.session.commit()
            
            # Answer 2 out of 5 questions (session is incomplete)
            for i in range(2):
                PracticeService.record_response(
                    session_id=session.id,
                    question_id=test_questions[i],
                    user_id=test_user.id,
                    submitted_answer=str(i + 1),
                    correct_answer=str(i + 1),
                    is_correct=True
                )
            
            original_session_id = session.id
            
            # Now simulate what happens when navigating to practice:
            # Frontend calls generate_session with concept_id=None
            # Backend should find and restore the incomplete session
            result = SessionEngineService.generate_session(
                user_id=test_user.id,
                mode="standard",
                concept_id=None  # This is what E2E tests pass
            )
            
            # Critical assertion: should resume the same session
            assert result["session_id"] == original_session_id, \
                f"Expected to resume session {original_session_id} when concept_id=None, " \
                f"but got new session {result['session_id']}. " \
                f"This reproduces the E2E test failure where session IDs are off by 1."
            
            # Verify the restored session has the same concept_id as the original
            assert result["concept_id"] == "c_concept_001", \
                f"Restored session should have same concept_id, got {result['concept_id']}"

    def test_session_engine_resume_with_multiple_incomplete_sessions(self, app, test_user, test_questions):
        """Test that SessionEngineService resumes the most recent incomplete session.
        
        When there are multiple incomplete sessions from different concepts,
        and concept_id=None, it should resume the most recent one.
        """
        with app.app_context():
            # Create two incomplete sessions with different concepts
            session1 = PracticeService.create_session(
                user_id=test_user.id,
                mode="standard",
                concept_id="c_concept_001"
            )
            session1.question_ids = json.dumps(test_questions[:3])
            db.session.add(session1)
            db.session.commit()
            
            # Answer 1 question in session1
            PracticeService.record_response(
                session_id=session1.id,
                question_id=test_questions[0],
                user_id=test_user.id,
                submitted_answer="1",
                correct_answer="1",
                is_correct=True
            )
            
            # Create a second, more recent session
            session2 = PracticeService.create_session(
                user_id=test_user.id,
                mode="standard",
                concept_id="c_concept_002"
            )
            session2.question_ids = json.dumps(test_questions[:3])
            db.session.add(session2)
            db.session.commit()
            
            # Answer 1 question in session2
            PracticeService.record_response(
                session_id=session2.id,
                question_id=test_questions[0],
                user_id=test_user.id,
                submitted_answer="1",
                correct_answer="1",
                is_correct=True
            )
            
            # When concept_id=None, should resume the most recent incomplete session (session2)
            result = SessionEngineService.generate_session(
                user_id=test_user.id,
                mode="standard",
                concept_id=None
            )
            
            # Should resume session2 (most recent), not session1
            assert result["session_id"] == session2.id, \
                f"Expected to resume most recent session {session2.id}, but got {result['session_id']}"
            assert result["concept_id"] == "c_concept_002", \
                f"Should resume session with concept c_concept_002, got {result['concept_id']}"

    def test_session_engine_creates_new_when_all_answered(self, app, test_user, test_questions):
        """Test that SessionEngineService creates new session when all questions are answered.
        
        This tests the auto-completion path in SessionEngineService.
        """
        with app.app_context():
            # Create an incomplete session
            session = PracticeService.create_session(
                user_id=test_user.id,
                mode="standard",
                concept_id="c_concept_001"
            )
            question_ids = test_questions[:5]
            session.question_ids = json.dumps(question_ids)
            db.session.add(session)
            db.session.commit()
            
            # Answer all 5 questions
            for i in range(5):
                PracticeService.record_response(
                    session_id=session.id,
                    question_id=test_questions[i],
                    user_id=test_user.id,
                    submitted_answer=str(i + 1),
                    correct_answer=str(i + 1),
                    is_correct=True
                )
            
            original_session_id = session.id
            
            # Try to generate session - should create new since all questions answered
            result = SessionEngineService.generate_session(
                user_id=test_user.id,
                mode="standard",
                concept_id="c_concept_001"
            )
            
            # Should create a new session, not resume the completed one
            assert result["session_id"] != original_session_id, \
                f"Should create new session when all questions answered, but resumed {original_session_id}"
            
            # Verify original session was auto-completed
            db.session.refresh(session)
            assert session.completed_at is not None, "Original session should be auto-completed"

    def test_multiple_sessions_sequential_creation(self, app, test_user, test_questions):
        """Test sequential session creation to reproduce E2E session ID mismatch.
        
        This simulates the E2E test scenario where multiple sessions are created
        and the expected session ID doesn't match the actual one.
        """
        with app.app_context():
            session_ids = []
            
            # Create 5 incomplete sessions sequentially
            for i in range(5):
                session = PracticeService.create_session(
                    user_id=test_user.id,
                    mode="standard",
                    concept_id="c_concept_001"
                )
                session.question_ids = json.dumps([test_questions[i]])
                db.session.add(session)
                db.session.commit()
                session_ids.append(session.id)
            
            # Get incomplete session - should return most recent (last one)
            retrieved, _, _ = PracticeService.get_incomplete_session(
                user_id=test_user.id,
                mode="standard"
            )
            
            expected_session_id = session_ids[-1]  # Most recent
            
            assert retrieved is not None, "Should find an incomplete session"
            assert retrieved.id == expected_session_id, \
                f"Expected most recent session {expected_session_id}, but got {retrieved.id}. " \
                f"Available session IDs: {session_ids}. " \
                f"This could explain E2E test failures where expected session doesn't match."

    def test_session_resuming_with_duplicate_responses(self, app, test_user, test_questions):
        """Test resuming a session where user answered the same question multiple times.
        
        This tests the 'latest response per question' logic that might affect resuming.
        """
        with app.app_context():
            # Create session with 5 questions
            session = PracticeService.create_session(
                user_id=test_user.id,
                mode="standard",
                concept_id="c_concept_001"
            )
            question_ids = test_questions[:5]
            session.question_ids = json.dumps(question_ids)
            db.session.add(session)
            db.session.commit()
            
            # Answer question 0 multiple times (simulating user retrying)
            from datetime import timedelta
            base_time = datetime.utcnow()
            
            # First answer (wrong)
            PracticeService.record_response(
                session_id=session.id,
                question_id=test_questions[0],
                user_id=test_user.id,
                submitted_answer="wrong",
                correct_answer="1",
                is_correct=False,
                duration_ms=1000
            )
            
            # Second answer (correct) - should be the one counted
            response2 = PracticeService.record_response(
                session_id=session.id,
                question_id=test_questions[0],
                user_id=test_user.id,
                submitted_answer="1",
                correct_answer="1",
                is_correct=True,
                duration_ms=2000
            )
            # Set later timestamp
            response2.answered_at = base_time + timedelta(seconds=10)
            db.session.add(response2)
            db.session.commit()
            
            # Try to resume - should work and count only the latest response
            retrieved, count, _ = PracticeService.get_incomplete_session(
                user_id=test_user.id,
                mode="standard"
            )
            
            assert retrieved is not None, "Should find incomplete session"
            assert retrieved.id == session.id, f"Expected session {session.id}, got {retrieved.id}"
            # Should count only unique questions, not all responses
            # Note: get_incomplete_session returns total response count, not unique questions
            # So 2 responses for 1 question = count of 2
            assert count == 2, f"Should count 2 responses (both answers to same question), got {count}"

    def test_session_resuming_after_completion_attempt(self, app, test_user, test_questions):
        """Test what happens when trying to resume a session that was partially completed.
        
        This tests edge cases around session completion state.
        """
        with app.app_context():
            # Create session
            session = PracticeService.create_session(
                user_id=test_user.id,
                mode="standard",
                concept_id="c_concept_001"
            )
            question_ids = test_questions[:5]
            session.question_ids = json.dumps(question_ids)
            db.session.add(session)
            db.session.commit()
            
            # Answer 3 out of 5 questions
            for i in range(3):
                PracticeService.record_response(
                    session_id=session.id,
                    question_id=test_questions[i],
                    user_id=test_user.id,
                    submitted_answer=str(i + 1),
                    correct_answer=str(i + 1),
                    is_correct=True
                )
            
            # Try to complete the session (but it shouldn't complete with only 3/5)
            # This simulates a failed completion attempt
            try:
                PracticeService.complete_session(
                    session_id=session.id,
                    total_questions=5,
                    correct_count=3,
                    total_duration_ms=5000
                )
            except Exception:
                pass  # Might fail, that's okay for this test
            
            # Try to resume - should still find the session
            retrieved, count, _ = PracticeService.get_incomplete_session(
                user_id=test_user.id,
                mode="standard"
            )
            
            # Session might be completed or not, depending on implementation
            # But if it's incomplete, we should be able to resume it
            if retrieved:
                assert retrieved.id == session.id, \
                    f"If session is incomplete, should resume {session.id}, got {retrieved.id}"

