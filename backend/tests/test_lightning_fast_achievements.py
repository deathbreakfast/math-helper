"""Backend tests for Lightning Fast achievements.

Tests verify that Lightning Fast achievements are correctly awarded based on lifetime
average speed, minimum question requirements per tier, and that incorrect answers
are excluded from the calculation.
"""

import pytest
from datetime import datetime

from app import create_app, db
from app.models import Achievement, PracticeSession, Question, Response, User
from app.services.achievement_service import AchievementService
from tests.helpers.data_helpers import (
    create_test_questions,
    create_test_session_with_responses,
)


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
        user = User(display_name="TestUser", pin="1234", avatar="🐯", experience=0)
        db.session.add(user)
        db.session.commit()
        _ = user.id
        return user


def test_lightning_fast_bronze_minimum_questions(app, test_user):
    """Test that Lightning Fast (Bronze) requires 50 correct questions for a concept."""
    with app.app_context():
        # Create 50 questions with fast correct answers (4s average, qualifies for bronze)
        questions = create_test_questions(50, 1)
        responses_data = [{
            'question_id': q.id,
            'answer': q.correct_answer,
            'is_correct': True,
            'duration_ms': 4000  # 4 seconds per question (qualifies for bronze: <5s)
        } for q in questions]
        
        session = create_test_session_with_responses(test_user.id, responses_data, concept_id="c_add_1s")
        
        # Check achievements
        lightning_fast_achievements = AchievementService.check_lightning_fast_achievements(test_user, session.id)
        
        # Verify achievement was awarded
        achievement = Achievement.query.filter_by(
            user_id=test_user.id,
            code="lightning-fast-bronze"
        ).first()
        
        assert achievement is not None, "Lightning Fast (Bronze) should be awarded with 50+ correct questions at <5s average"
        assert achievement.session_id == session.id


def test_lightning_fast_bronze_not_awarded_below_minimum(app, test_user):
    """Test that Lightning Fast (Bronze) is NOT awarded with less than 50 questions."""
    with app.app_context():
        # Create 49 questions with fast correct answers
        questions = create_test_questions(49, 1)
        responses_data = [{
            'question_id': q.id,
            'answer': q.correct_answer,
            'is_correct': True,
            'duration_ms': 4000  # 4 seconds per question
        } for q in questions]
        
        session = create_test_session_with_responses(test_user.id, responses_data, concept_id="c_add_1s")
        
        # Check achievements
        lightning_fast_achievements = AchievementService.check_lightning_fast_achievements(test_user, session.id)
        
        # Verify NO achievement was awarded
        achievement = Achievement.query.filter(
            Achievement.user_id == test_user.id,
            Achievement.code.like("lightning-fast-%")
        ).first()
        
        assert achievement is None, "Lightning Fast should NOT be awarded with less than 50 questions"


def test_lightning_fast_silver_minimum_questions(app, test_user):
    """Test that Lightning Fast (Silver) requires 100 correct questions for a concept."""
    with app.app_context():
        # Create 100 questions with fast correct answers (3.5s average, qualifies for silver: <4s)
        questions = create_test_questions(100, 1)
        responses_data = [{
            'question_id': q.id,
            'answer': q.correct_answer,
            'is_correct': True,
            'duration_ms': 3500  # 3.5 seconds per question (qualifies for silver: <4s)
        } for q in questions]
        
        session = create_test_session_with_responses(test_user.id, responses_data, concept_id="c_add_1s")
        
        # Check achievements
        lightning_fast_achievements = AchievementService.check_lightning_fast_achievements(test_user, session.id)
        
        # Verify achievement was awarded (should get silver, not bronze)
        achievement = Achievement.query.filter_by(
            user_id=test_user.id,
            code="lightning-fast-silver"
        ).first()
        
        assert achievement is not None, "Lightning Fast (Silver) should be awarded with 100+ correct questions at <4s average"


def test_lightning_fast_excludes_incorrect_answers(app, test_user):
    """Test that incorrect answers are excluded from Lightning Fast speed calculation."""
    with app.app_context():
        # Create 75 questions - answer 50 correctly very fast (1s), 25 incorrectly very fast (1s)
        # Average of correct answers: 1s (very fast, qualifies for gold: <3s)
        # Need 50 correct answers for bronze minimum
        # But if we included incorrect, average would still be 1s, but we want to verify only correct are counted
        questions = create_test_questions(75, 1)
        responses_data = []
        for i, q in enumerate(questions):
            responses_data.append({
                'question_id': q.id,
                'answer': q.correct_answer if i < 50 else '999',  # First 50 correct, rest wrong
                'is_correct': i < 50,
                'duration_ms': 1000  # All answered in 1 second
            })
        
        session = create_test_session_with_responses(test_user.id, responses_data, concept_id="c_add_1s")
        
        # Check achievements
        lightning_fast_achievements = AchievementService.check_lightning_fast_achievements(test_user, session.id)
        
        # Verify achievement was awarded (only correct answers counted, so 1s average qualifies for bronze: <5s with 50+ correct)
        achievement = Achievement.query.filter_by(
            user_id=test_user.id,
            code="lightning-fast-bronze"
        ).first()
        
        assert achievement is not None, "Lightning Fast (Bronze) should be awarded based on correct answers only (1s average with 50+ correct qualifies for bronze)"


def test_lightning_fast_negative_quick_incorrect_answers(app, test_user):
    """Test that answering questions quickly but incorrectly does NOT award Lightning Fast."""
    with app.app_context():
        # Create 50 questions - answer all incorrectly but very quickly
        questions = create_test_questions(50, 1)
        responses_data = [{
            'question_id': q.id,
            'answer': '999',  # All wrong
            'is_correct': False,
            'duration_ms': 500  # Very fast but incorrect
        } for q in questions]
        
        session = create_test_session_with_responses(test_user.id, responses_data, concept_id="c_add_1s")
        
        # Check achievements
        lightning_fast_achievements = AchievementService.check_lightning_fast_achievements(test_user, session.id)
        
        # Verify NO achievement was awarded (no correct answers to calculate speed from)
        achievement = Achievement.query.filter(
            Achievement.user_id == test_user.id,
            Achievement.code.like("lightning-fast-%")
        ).first()
        
        assert achievement is None, "Lightning Fast should NOT be awarded when all answers are incorrect"


def test_lightning_fast_lifetime_average(app, test_user):
    """Test that Lightning Fast uses lifetime average, not just session average."""
    with app.app_context():
        # First session: 30 questions at 6s average (too slow, doesn't qualify)
        questions1 = create_test_questions(30, 1)
        session1 = create_test_session_with_responses(test_user.id, [{
            'question_id': q.id,
            'answer': q.correct_answer,
            'is_correct': True,
            'duration_ms': 6000
        } for q in questions1], concept_id="c_add_1s")
        
        # Second session: 20 questions at 2s average (fast, but total is 50 at ~4.4s average)
        questions2 = create_test_questions(20, 1)
        session2 = create_test_session_with_responses(test_user.id, [{
            'question_id': q.id,
            'answer': q.correct_answer,
            'is_correct': True,
            'duration_ms': 2000
        } for q in questions2], concept_id="c_add_1s")
        
        # Check achievements after second session
        lightning_fast_achievements = AchievementService.check_lightning_fast_achievements(test_user, session2.id)
        
        # Lifetime average: (30*6 + 20*2) / 50 = (180 + 40) / 50 = 220/50 = 4.4s
        # This qualifies for bronze (<5s) with 50+ questions
        achievement = Achievement.query.filter_by(
            user_id=test_user.id,
            code="lightning-fast-bronze"
        ).first()
        
        assert achievement is not None, "Lightning Fast should use lifetime average across all sessions"


def test_lightning_fast_multiple_tiers_progression(app, test_user):
    """Test that multiple Lightning Fast tiers can be awarded as user progresses."""
    with app.app_context():
        # First: 50 questions at 4.5s average -> Bronze
        questions1 = create_test_questions(50, 1)
        session1 = create_test_session_with_responses(test_user.id, [{
            'question_id': q.id,
            'answer': q.correct_answer,
            'is_correct': True,
            'duration_ms': 4500
        } for q in questions1], concept_id="c_add_1s")
        
        AchievementService.check_lightning_fast_achievements(test_user, session1.id)
        
        bronze = Achievement.query.filter_by(user_id=test_user.id, code="lightning-fast-bronze").first()
        assert bronze is not None, "Bronze should be awarded"
        
        # Second: Add 50 more questions at 3.5s average -> Total 100 at ~4s average -> Silver
        questions2 = create_test_questions(50, 1)
        session2 = create_test_session_with_responses(test_user.id, [{
            'question_id': q.id,
            'answer': q.correct_answer,
            'is_correct': True,
            'duration_ms': 3500
        } for q in questions2], concept_id="c_add_1s")
        
        AchievementService.check_lightning_fast_achievements(test_user, session2.id)
        
        silver = Achievement.query.filter_by(user_id=test_user.id, code="lightning-fast-silver").first()
        assert silver is not None, "Silver should be awarded with 100+ questions at <4s average"


def test_lightning_fast_concept_specific(app, test_user):
    """Test that Lightning Fast achievements are concept-specific."""
    with app.app_context():
        # Create 50 questions with fast answers
        questions1 = create_test_questions(50, 1)
        session1 = create_test_session_with_responses(test_user.id, [{
            'question_id': q.id,
            'answer': q.correct_answer,
            'is_correct': True,
            'duration_ms': 4000
        } for q in questions1], concept_id="c_add_1s")
        
        AchievementService.check_lightning_fast_achievements(test_user, session1.id)
        
        achievement = Achievement.query.filter_by(
            user_id=test_user.id,
            code="lightning-fast-bronze"
        ).first()
        
        assert achievement is not None, "Achievement should be awarded for c_add_1s"
        
        # Check metadata
        import json
        if achievement.achievement_metadata:
            metadata = json.loads(achievement.achievement_metadata)
            assert metadata.get("concept_id") == "c_add_1s", "Achievement should have concept_id c_add_1s in metadata"
            assert "level" not in metadata, "Achievement should not have level in metadata (legacy removed)"


def test_lightning_fast_with_descriptive_concept_id(app, test_user):
    """Test that Lightning Fast works with descriptive concept IDs (e.g., c_add_1s).
    
    Bug reproduction: User completed "Single Digit Addition (1s)" 6 times with avg time 1.3s.
    This should qualify for bronze (1.3s < 5.0s) with 50+ questions, but currently fails
    because:
    1. The checker requires session.level to be set (line 54), but descriptive concepts may have level=None
    2. The checker filters by Question.required_level instead of session.concept_id
    
    This test reproduces the bug by creating sessions with concept_id but level=None.
    """
    with app.app_context():
        # Create 6 sessions with c_add_1s concept, each with ~10 questions
        # Total: 60 questions at 1.3s average (should qualify for bronze: <5s with 50+ questions)
        questions_per_session = 10
        total_sessions = 6
        avg_duration_ms = 1300  # 1.3 seconds per question
        
        all_questions = create_test_questions(questions_per_session * total_sessions, experience=0)
        question_idx = 0
        
        sessions = []
        for session_num in range(total_sessions):
            session_questions = all_questions[question_idx:question_idx + questions_per_session]
            question_idx += questions_per_session
            
            responses_data = [{
                'question_id': q.id,
                'answer': q.correct_answer,
                'is_correct': True,
                'duration_ms': avg_duration_ms  # 1.3 seconds per question
            } for q in session_questions]
            
            # Create session with descriptive concept_id c_add_1s and level=None
            # This matches the real scenario where descriptive concepts don't have a legacy level
            session = create_test_session_with_responses(
                test_user.id,
                responses_data,
                level=None,  # No level set for descriptive concepts
                concept_id="c_add_1s"
            )
            sessions.append(session)
        
        # Check achievements after the last session
        # Total: 60 correct questions at 1.3s average should qualify for bronze
        lightning_fast_achievements = AchievementService.check_lightning_fast_achievements(
            test_user, 
            sessions[-1].id
        )
        
        # Verify achievement was awarded (this test will fail until we fix the bug)
        achievement = Achievement.query.filter_by(
            user_id=test_user.id,
            code="lightning-fast-bronze"
        ).first()
        
        assert achievement is not None, (
            "Lightning Fast (Bronze) should be awarded for c_add_1s with 60+ correct questions "
            "at 1.3s average (1.3s < 5.0s qualifies for bronze). "
            "Currently fails because checker requires session.level and filters by level instead of concept_id."
        )
        
        # Verify metadata includes concept_id
        import json
        if achievement.achievement_metadata:
            metadata = json.loads(achievement.achievement_metadata)
            assert metadata.get("concept_id") == "c_add_1s", (
                "Achievement should have concept_id c_add_1s in metadata"
            )

