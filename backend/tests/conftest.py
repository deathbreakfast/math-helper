"""Shared pytest fixtures for backend tests.

This module provides common fixtures used across multiple test files.
Individual test files can override these fixtures if needed.
"""

import pytest
from datetime import datetime

from app import create_app, db
from app.models import User, Achievement, PracticeSession, Question, Response


@pytest.fixture
def app():
    """Create test Flask application with database setup."""
    app = create_app(testing=True)
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def test_user(app):
    """Create a basic test user."""
    with app.app_context():
        user = User(display_name="TestUser", pin="1234", avatar="🐯", level=1)
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user


@pytest.fixture
def test_user_with_achievements(app):
    """Create a test user with specified achievements."""
    def _create_user_with_achievements(achievement_codes: list[str] = None, level: int = 1):
        with app.app_context():
            user = User(display_name="TestUser", pin="1234", avatar="🐯", level=level)
            db.session.add(user)
            db.session.flush()
            
            if achievement_codes:
                achievements = []
                for code in achievement_codes:
                    achievement = Achievement(
                        user_id=user.id,
                        code=code,
                        title=f"Achievement {code}",
                        description=f"Test achievement {code}",
                        icon="🏆",
                        category="test",
                        earned_at=datetime.utcnow()
                    )
                    achievements.append(achievement)
                    db.session.add(achievement)
                
                db.session.commit()
                db.session.refresh(user)
                return user, achievements
            
            db.session.commit()
            db.session.refresh(user)
            return user
    
    return _create_user_with_achievements


@pytest.fixture
def test_question(app):
    """Create a basic test question."""
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
        db.session.refresh(question)
        return question


@pytest.fixture
def test_session(app, test_user, test_question):
    """Create a completed practice session with responses.
    
    Returns a practice session with 100 questions, all answered correctly.
    """
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
        db.session.refresh(session)
        return session


@pytest.fixture
def test_test_session(app, test_user, test_question):
    """Create a completed test session with responses."""
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
        db.session.refresh(session)
        return session


@pytest.fixture(autouse=True)
def cleanup_after_test(app):
    """Automatic cleanup fixture that runs after each test.
    
    This fixture ensures database state is clean between tests.
    The app fixture already handles db.drop_all() in its teardown,
    but this provides an additional cleanup point if needed.
    """
    yield
    # Cleanup happens automatically via app fixture's db.drop_all()
    # This fixture can be extended for additional cleanup if needed
    pass

