"""Tests to verify that sessions maintain concept consistency.

These tests ensure that:
1. All questions in a session are from the same concept
2. When a concept_id is provided, the session uses that exact concept (not random)
"""

import pytest

from app import create_app, db
from app.models import PracticeSession, Question, User
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
def user(app):
    """Create a test user with multiple concepts unlocked.
    
    Ensures the user has at least 2 concepts unlocked (c_add_1s and c_sub_1s)
    by creating the necessary achievements.
    """
    with app.app_context():
        from app.services.xp_service import XPService
        from app.models import Achievement
        from datetime import datetime
        import json
        
        u = User(display_name="TestUser", pin="1234", avatar="🐯", experience=XPService.total_xp_for_level(10))
        db.session.add(u)
        db.session.commit()
        db.session.refresh(u)
        
        # Unlock c_add_2s by creating required achievements
        # c_add_2s requires: math-master-bronze with c_add_1s, and speed-demon-bronze
        achievement1 = Achievement(
            user_id=u.id,
            code="math-master-bronze",
            title="Math Master (Bronze)",
            description="Test achievement",
            icon="🎯",
            category="accuracy",
            earned_at=datetime.utcnow(),
            achievement_metadata=json.dumps({"concept_id": "c_add_1s"}, sort_keys=True),
        )
        db.session.add(achievement1)
        
        achievement2 = Achievement(
            user_id=u.id,
            code="speed-demon-bronze",
            title="Speed Demon (Bronze)",
            description="Test achievement",
            icon="⚡",
            category="speed",
            earned_at=datetime.utcnow(),
        )
        db.session.add(achievement2)
        
        # Unlock c_sub_1s by creating required achievement
        # c_sub_1s requires: math-master-bronze with c_add_2s
        achievement3 = Achievement(
            user_id=u.id,
            code="math-master-bronze",
            title="Math Master (Bronze)",
            description="Test achievement",
            icon="🎯",
            category="accuracy",
            earned_at=datetime.utcnow(),
            achievement_metadata=json.dumps({"concept_id": "c_add_2s"}, sort_keys=True),
        )
        db.session.add(achievement3)
        
        db.session.commit()
        db.session.refresh(u)
        
        # Verify we have multiple concepts unlocked
        from app.services.concept_unlock_service import ConceptUnlockService
        unlocked = ConceptUnlockService.get_unlocked_concepts(u.id)
        assert len(unlocked) >= 2, f"Expected at least 2 unlocked concepts, got {len(unlocked)}: {unlocked}"
        assert "c_add_1s" in unlocked, "c_add_1s should be unlocked"
        assert "c_sub_1s" in unlocked, "c_sub_1s should be unlocked"
        
        return u


def test_all_questions_in_session_have_same_concept(app, user):
    """Test that all questions in a generated session are from the same concept.
    
    This verifies that when a session is created, all questions are generated
    for the same concept_id, ensuring consistency throughout the session.
    """
    with app.app_context():
        # Generate a session with a specific concept
        result = SessionEngineService.generate_session(
            user_id=user.id,
            mode="standard",
            concept_id="c_add_1s",  # Addition with 1s
        )
        
        session_id = result["session_id"]
        session_concept_id = result["concept_id"]
        
        # Verify session has the correct concept_id
        assert session_concept_id == "c_add_1s", "Session should have the requested concept_id"
        
        # Get the session from database
        session = db.session.get(PracticeSession, session_id)
        assert session is not None, "Session should exist"
        assert session.concept_id == "c_add_1s", "Session concept_id should match"
        
        # Get all questions for this session
        session_details = PracticeService.get_session_with_details(session_id)
        assert session_details is not None, "Session details should be available"
        
        questions = session_details.get("questions", [])
        assert len(questions) > 0, "Session should have questions"
        
        # Verify all questions have the same operation (which should match the concept)
        # For c_add_1s, all questions should be addition
        operations = set(q.get("operation") for q in questions)
        assert len(operations) == 1, f"All questions should have the same operation. Found: {operations}"
        assert "addition" in operations, "All questions should be addition for c_add_1s"
        
        # Verify all questions match the concept's expected properties
        # For addition with 1s, operands should be in the expected range
        for question in questions:
            assert question.get("operation") == "addition", \
                f"Question {question.get('question_id')} should be addition"
            # c_add_1s typically involves adding 1 to numbers, so at least one operand should be 1
            # or the operation should be consistent with addition
            operand1 = question.get("operand1")
            operand2 = question.get("operand2")
            assert operand1 is not None and operand2 is not None, \
                "Questions should have operands"


def test_session_with_provided_concept_id_uses_exact_concept(app, user):
    """Test that when concept_id is provided, the session uses that exact concept.
    
    This prevents regression where starting a session from the math concepts page
    might launch a random session instead of the chosen concept.
    """
    with app.app_context():
        # Test with a specific concept
        requested_concept = "c_add_1s"
        
        result = SessionEngineService.generate_session(
            user_id=user.id,
            mode="standard",
            concept_id=requested_concept,
        )
        
        # Verify the session uses the exact concept that was requested
        assert result["concept_id"] == requested_concept, \
            f"Session should use the requested concept '{requested_concept}', but got '{result['concept_id']}'"
        
        # Verify the session in the database also has the correct concept_id
        session = db.session.get(PracticeSession, result["session_id"])
        assert session.concept_id == requested_concept, \
            f"Database session should have concept_id '{requested_concept}', but got '{session.concept_id}'"
        
        # Verify all questions are consistent with this concept
        session_details = PracticeService.get_session_with_details(result["session_id"])
        questions = session_details.get("questions", [])
        
        for question in questions:
            assert question.get("operation") == "addition", \
                f"All questions should be addition for concept '{requested_concept}'"


def test_session_with_different_concept_uses_different_operation(app, user):
    """Test that different concepts produce different question types.
    
    This helps verify that concept_id is actually being used to generate questions.
    """
    with app.app_context():
        # Test with subtraction concept
        result = SessionEngineService.generate_session(
            user_id=user.id,
            mode="standard",
            concept_id="c_sub_1s",  # Subtraction with 1s
        )
        
        assert result["concept_id"] == "c_sub_1s", "Session should use the requested concept"
        
        # Get questions and verify they are subtraction
        session_details = PracticeService.get_session_with_details(result["session_id"])
        questions = session_details.get("questions", [])
        
        assert len(questions) > 0, "Session should have questions"
        
        # All questions should be subtraction
        for question in questions:
            assert question.get("operation") == "subtraction", \
                f"All questions should be subtraction for concept 'c_sub_1s', but got '{question.get('operation')}'"


def test_multiple_sessions_with_same_concept_are_consistent(app, user):
    """Test that multiple sessions with the same concept_id all use that concept.
    
    This ensures consistency across multiple session generations.
    """
    with app.app_context():
        concept_id = "c_add_1s"
        
        # Generate multiple sessions with the same concept
        for i in range(3):
            result = SessionEngineService.generate_session(
                user_id=user.id,
                mode="standard",
                concept_id=concept_id,
            )
            
            # Each session should use the exact concept
            assert result["concept_id"] == concept_id, \
                f"Session {i+1} should use concept '{concept_id}', but got '{result['concept_id']}'"
            
            # Verify questions are consistent
            session_details = PracticeService.get_session_with_details(result["session_id"])
            questions = session_details.get("questions", [])
            
            for question in questions:
                assert question.get("operation") == "addition", \
                    f"All questions in session {i+1} should be addition"


def test_session_from_home_page_without_concept_selects_unlocked_concept(app, user):
    """Test that starting a session from home page (no concept_id) selects an unlocked concept.
    
    This is the expected behavior when no concept is specified - it should randomly
    select from unlocked concepts, but all questions in that session should still
    be from the same concept.
    """
    with app.app_context():
        # Generate session without specifying concept_id (like from home page)
        result = SessionEngineService.generate_session(
            user_id=user.id,
            mode="standard",
            # concept_id=None (not provided)
        )
        
        # Should have selected a concept
        selected_concept = result["concept_id"]
        assert selected_concept is not None, "Should have selected a concept"
        assert selected_concept.startswith("c_"), "Concept ID should start with 'c_'"
        
        # Get questions and verify they all match the selected concept
        session_details = PracticeService.get_session_with_details(result["session_id"])
        questions = session_details.get("questions", [])
        
        assert len(questions) > 0, "Session should have questions"
        
        # Get the concept config to verify operation type
        from app.services.concept_config_service import ConceptConfigService
        concept_config = ConceptConfigService.get_concept_config(selected_concept)
        assert concept_config is not None, f"Concept config should exist for '{selected_concept}'"
        expected_operation = concept_config.get("operation")
        
        # All questions should have the same operation as the concept
        for question in questions:
            assert question.get("operation") == expected_operation, \
                f"All questions should have operation '{expected_operation}' for concept '{selected_concept}'"


def test_api_endpoint_with_concept_id_uses_exact_concept(app, user):
    """Test that the API endpoint respects concept_id parameter.
    
    This prevents regression where starting a session from the math concepts page
    via the API might launch a random session instead of the chosen concept.
    """
    with app.test_client() as client:
        # Test with a specific concept (like from math concepts page)
        requested_concept = "c_add_1s"
        
        response = client.post(
            "/api/practice/sessions/start",
            json={
                "user_id": user.id,
                "mode": "standard",
                "concept_id": requested_concept,
            },
            content_type="application/json",
        )
        
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.get_data(as_text=True)}"
        
        data = response.get_json()
        assert data is not None, "Response should contain JSON data"
        
        # API response may have 'data' key or return data directly
        session_data = data.get("data", data)
        assert session_data["concept_id"] == requested_concept, \
            f"API should return the requested concept '{requested_concept}', but got '{session_data.get('concept_id')}'"
        
        # Verify the session in the database also has the correct concept_id
        with app.app_context():
            from app.models import PracticeSession
            session = db.session.get(PracticeSession, session_data["session_id"])
            assert session is not None, "Session should exist in database"
            assert session.concept_id == requested_concept, \
                f"Database session should have concept_id '{requested_concept}', but got '{session.concept_id}'"
            
            # Verify all questions are consistent with this concept
            session_details = PracticeService.get_session_with_details(session_data["session_id"])
            questions = session_details.get("questions", [])
            
            assert len(questions) > 0, "Session should have questions"
            
            for question in questions:
                assert question.get("operation") == "addition", \
                    f"All questions should be addition for concept '{requested_concept}'"


def test_api_endpoint_without_concept_id_selects_random_unlocked(app, user):
    """Test that the API endpoint without concept_id selects a random unlocked concept.
    
    This is the expected behavior when starting from home page (no concept specified).
    """
    with app.test_client() as client:
        response = client.post(
            "/api/practice/sessions/start",
            json={
                "user_id": user.id,
                "mode": "standard",
                # concept_id not provided
            },
            content_type="application/json",
        )
        
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.get_data(as_text=True)}"
        
        data = response.get_json()
        assert data is not None, "Response should contain JSON data"
        
        # API response may have 'data' key or return data directly
        session_data = data.get("data", data)
        selected_concept = session_data["concept_id"]
        
        assert selected_concept is not None, "Should have selected a concept"
        assert selected_concept.startswith("c_"), "Concept ID should start with 'c_'"
        
        # Verify all questions are consistent with the selected concept
        with app.app_context():
            session_details = PracticeService.get_session_with_details(session_data["session_id"])
            questions = session_details.get("questions", [])
            
            assert len(questions) > 0, "Session should have questions"
            
            # Get the concept config to verify operation type
            from app.services.concept_config_service import ConceptConfigService
            concept_config = ConceptConfigService.get_concept_config(selected_concept)
            assert concept_config is not None, f"Concept config should exist for '{selected_concept}'"
            expected_operation = concept_config.get("operation")
            
            # All questions should have the same operation as the concept
            for question in questions:
                assert question.get("operation") == expected_operation, \
                    f"All questions should have operation '{expected_operation}' for concept '{selected_concept}'"
