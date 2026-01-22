"""Tests for SessionEngineService (concept-based practice)."""

import pytest

from app import create_app, db
from app.models import User
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
    with app.app_context():
        from app.services.xp_service import XPService
        u = User(display_name="SessionUser", pin="1234", avatar="🐯", experience=XPService.total_xp_for_level(10))
        db.session.add(u)
        db.session.commit()
        db.session.refresh(u)
        return u


def test_generate_session_with_concept_id_returns_concept_id_and_questions(app, user):
    with app.app_context():
        result = SessionEngineService.generate_session(
            user_id=user.id,
            mode="standard",
            concept_id="c_concept_001",
        )

        assert result["session_id"] is not None
        assert result["concept_id"] == "c_concept_001"
        assert result["level"] is not None
        assert isinstance(result["questions"], list)
        assert len(result["questions"]) > 0


def test_generate_session_default_selects_concept(app, user):
    with app.app_context():
        result = SessionEngineService.generate_session(
            user_id=user.id,
            mode="standard",
        )

        assert result["concept_id"] is not None
        assert isinstance(result["concept_id"], str)
        # Concept ID can be either c_concept_### or descriptive (c_add_1s, etc.)
        assert result["concept_id"].startswith("c_")
        assert isinstance(result["questions"], list)
        assert len(result["questions"]) > 0


def test_generate_session_selects_only_unlocked_concepts(app, user):
    """Test that when no concept_id is provided, only unlocked concepts are selected."""
    with app.app_context():
        from app.services.concept_unlock_service import ConceptUnlockService
        
        # Get all unlocked concepts for this user
        unlocked_concepts = ConceptUnlockService.get_unlocked_concepts(user.id)
        
        # Generate multiple sessions and verify they all use unlocked concepts
        selected_concepts = set()
        for _ in range(10):  # Generate 10 sessions to increase chance of variety
            result = SessionEngineService.generate_session(
                user_id=user.id,
                mode="standard",
            )
            selected_concept = result["concept_id"]
            selected_concepts.add(selected_concept)
            
            # Verify the selected concept is in the unlocked list
            assert selected_concept in unlocked_concepts, \
                f"Selected concept {selected_concept} is not unlocked. Unlocked: {unlocked_concepts}"
        
        # Verify we're actually selecting from unlocked concepts
        assert len(selected_concepts) > 0, "Should have selected at least one concept"


def test_generate_session_uses_dynamic_question_count_with_no_history(app, user):
    """Test that session generation uses default question count (10) when no perfect sessions exist."""
    with app.app_context():
        result = SessionEngineService.generate_session(
            user_id=user.id,
            mode="standard",
            concept_id="c_concept_001",
        )
        
        assert result["session_id"] is not None
        assert isinstance(result["questions"], list)
        assert len(result["questions"]) == 10, "Should default to 10 questions with no perfect sessions"


def test_generate_session_uses_dynamic_question_count_with_perfect_sessions(app, user):
    """Test that session generation uses dynamic question count based on perfect session history."""
    with app.app_context():
        from datetime import datetime
        from app.models import PracticeSession
        
        # Create 5 perfect sessions for the concept
        for i in range(5):
            session = PracticeSession(
                user_id=user.id,
                mode="standard",
                concept_id="c_concept_001",
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                total_questions=10,
                correct_count=10,
                accuracy=100.0,
            )
            db.session.add(session)
        
        db.session.commit()
        
        # Generate a new session for the same concept
        result = SessionEngineService.generate_session(
            user_id=user.id,
            mode="standard",
            concept_id="c_concept_001",
        )
        
        assert result["session_id"] is not None
        assert isinstance(result["questions"], list)
        # With 5 perfect sessions, should have more than 10 questions (around 20 based on sigmoid)
        assert len(result["questions"]) > 10, f"Expected more than 10 questions, got {len(result['questions'])}"
        assert len(result["questions"]) <= 50, f"Should not exceed 50 questions, got {len(result['questions'])}"


def test_generate_session_uses_capped_question_count(app, user):
    """Test that session generation caps question count at 50 even with many perfect sessions."""
    with app.app_context():
        from datetime import datetime
        from app.models import PracticeSession
        
        # Create 15 perfect sessions (more than needed to reach cap)
        for i in range(15):
            session = PracticeSession(
                user_id=user.id,
                mode="standard",
                concept_id="c_concept_001",
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                total_questions=10,
                correct_count=10,
                accuracy=100.0,
            )
            db.session.add(session)
        
        db.session.commit()
        
        # Generate a new session for the same concept
        result = SessionEngineService.generate_session(
            user_id=user.id,
            mode="standard",
            concept_id="c_concept_001",
        )
        
        assert result["session_id"] is not None
        assert isinstance(result["questions"], list)
        # Should be capped at 50
        assert len(result["questions"]) == 50, f"Expected 50 questions at cap, got {len(result['questions'])}"


def test_generate_session_question_count_per_concept(app, user):
    """Test that question count is calculated per concept independently."""
    with app.app_context():
        from datetime import datetime
        from app.models import PracticeSession
        
        # Create 5 perfect sessions for concept_001
        for i in range(5):
            session = PracticeSession(
                user_id=user.id,
                mode="standard",
                concept_id="c_concept_001",
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                total_questions=10,
                correct_count=10,
                accuracy=100.0,
            )
            db.session.add(session)
        
        # Create 0 perfect sessions for concept_003
        # (no sessions created)
        
        db.session.commit()
        
        # Generate session for concept_001 (should have more questions)
        result1 = SessionEngineService.generate_session(
            user_id=user.id,
            mode="standard",
            concept_id="c_concept_001",
        )
        
        # Generate session for concept_003 (should have default 10 questions)
        result2 = SessionEngineService.generate_session(
            user_id=user.id,
            mode="standard",
            concept_id="c_concept_003",
        )
        
        assert len(result1["questions"]) > 10, "concept_001 should have more than 10 questions"
        assert len(result2["questions"]) == 10, "concept_003 should have default 10 questions"

