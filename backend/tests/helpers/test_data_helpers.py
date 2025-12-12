"""Helper functions for creating test data in backend tests.

These helpers allow tests to quickly set up users, achievements, sessions,
and questions without going through the full service layer validation.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import select

from app.config.achievements import ACHIEVEMENTS_CONFIG
from app.models import Achievement, PracticeSession, Question, Response, User, db


def award_achievement_directly(
    user_id: int, 
    achievement_code: str, 
    earned_at: Optional[datetime] = None,
    session_id: Optional[int] = None
) -> Achievement:
    """Award achievement directly without checking requirements (for testing).
    
    Args:
        user_id: The user ID to award the achievement to
        achievement_code: The achievement code (e.g., 'first-victory')
        earned_at: Optional datetime for when achievement was earned
        session_id: Optional session ID to link the achievement to
        
    Returns:
        The created or existing Achievement object
        
    Raises:
        ValueError: If achievement_code is not found in ACHIEVEMENTS_CONFIG
    """
    # Get achievement config to extract metadata
    config = ACHIEVEMENTS_CONFIG.get(achievement_code)
    if not config:
        raise ValueError(f"Achievement code '{achievement_code}' not found in ACHIEVEMENTS_CONFIG")
    
    existing = db.session.scalar(
        select(Achievement).where(
            Achievement.user_id == user_id,
            Achievement.code == achievement_code
        )
    )
    
    if existing:
        # Update session_id if provided and different
        if session_id and existing.session_id != session_id:
            existing.session_id = session_id
            db.session.add(existing)
            db.session.commit()
        return existing
    
    achievement = Achievement(
        user_id=user_id,
        code=achievement_code,
        title=config.get("title", achievement_code),
        description=config.get("description", ""),
        icon=config.get("icon", "🏆"),
        category=config.get("category", "test"),
        earned_at=earned_at or datetime.utcnow(),
        session_id=session_id
    )
    db.session.add(achievement)
    db.session.commit()
    return achievement


def set_user_level_directly(user_id: int, level: int) -> Optional[User]:
    """Set user level directly without checking requirements (for testing).
    
    Args:
        user_id: The user ID to update
        level: The level to set
        
    Returns:
        The updated User object, or None if user not found
    """
    user = db.session.get(User, user_id)
    if user:
        user.level = level
        user.updated_at = datetime.utcnow()
        db.session.commit()
        return user
    return None


def create_test_session_with_responses(
    user_id: int,
    responses_data: list[dict],
    mode: str = "standard",
    level: int = 1,
    is_test: bool = False,
    test_type: Optional[str] = None,
    completed_at: Optional[datetime] = None
) -> PracticeSession:
    """Create a practice session with responses for testing.
    
    Args:
        user_id: The user ID for the session
        responses_data: List of response dicts with keys:
            - question_id: int (required)
            - answer: str (optional, defaults to '')
            - is_correct: bool (optional, defaults to False)
            - duration_ms: int (optional, defaults to 3000)
            - answered_at: datetime (optional, defaults to now)
        mode: Session mode (default: "standard")
        level: Session level (default: 1)
        is_test: Whether this is a test session (default: False)
        test_type: Test type if is_test is True (optional)
        completed_at: When session was completed (optional, defaults to now)
        
    Returns:
        The created PracticeSession object
    """
    session = PracticeSession(
        user_id=user_id,
        mode=mode,
        level=level,
        is_test=is_test,
        test_type=test_type,
        started_at=datetime.utcnow()
    )
    db.session.add(session)
    db.session.flush()
    
    correct_count = 0
    total_duration_ms = 0
    
    for resp_data in responses_data:
        question = db.session.get(Question, resp_data['question_id'])
        if not question:
            continue
        
        is_correct = resp_data.get('is_correct', False)
        duration_ms = resp_data.get('duration_ms', 3000)
        answer = resp_data.get('answer', '')
        
        # If answer not provided but is_correct is True, use correct_answer
        if not answer and is_correct:
            answer = question.correct_answer
        
        response = Response(
            session_id=session.id,
            user_id=user_id,
            question_id=question.id,
            submitted_answer=answer,
            correct_answer=question.correct_answer,
            is_correct=is_correct,
            duration_ms=duration_ms,
            answered_at=resp_data.get('answered_at', datetime.utcnow())
        )
        db.session.add(response)
        
        if is_correct:
            correct_count += 1
        total_duration_ms += duration_ms
    
    # Calculate session stats
    total_questions = len([r for r in responses_data if db.session.get(Question, r['question_id'])])
    accuracy = (correct_count / total_questions * 100) if total_questions > 0 else 0.0
    
    session.completed_at = completed_at or datetime.utcnow()
    session.total_questions = total_questions
    session.correct_count = correct_count
    session.accuracy = accuracy
    session.total_duration_ms = total_duration_ms
    
    db.session.commit()
    return session


def create_test_questions(
    count: int,
    level: int,
    operation: str = "addition"
) -> list[Question]:
    """Create test questions for achievement testing.
    
    Args:
        count: Number of questions to create
        level: Required level for the questions
        operation: Operation type (default: "addition")
        
    Returns:
        List of created Question objects
    """
    questions = []
    for i in range(count):
        operand1 = 1 + i
        operand2 = 1
        
        # Calculate correct answer based on operation
        if operation == "addition":
            correct_answer = str(operand1 + operand2)
            prompt = f"{operand1} + {operand2}"
        elif operation == "subtraction":
            correct_answer = str(operand1 + operand2 - operand2)  # Keep it simple
            prompt = f"{operand1 + operand2} - {operand2}"
        elif operation == "multiplication":
            correct_answer = str(operand1 * operand2)
            prompt = f"{operand1} × {operand2}"
        elif operation == "division":
            correct_answer = str(operand1)
            prompt = f"{operand1 * operand2} ÷ {operand2}"
        else:
            correct_answer = str(operand1 + operand2)
            prompt = f"{operand1} + {operand2}"
        
        question = Question(
            operation=operation,
            operand1=operand1,
            operand2=operand2,
            correct_answer=correct_answer,
            prompt=prompt,
            required_level=level,
            level_tag=f"Level {level}"
        )
        db.session.add(question)
        questions.append(question)
    
    db.session.commit()
    return questions

