"""Backend tests for achievement awarding validation.

Tests verify that achievements are correctly awarded based on user performance
across different categories: milestone, accuracy, speed, consistency, and progression.
"""

import pytest
from datetime import datetime, timedelta

from app import create_app, db
from app.models import Achievement, PracticeSession, Question, Response, User
from app.services.achievement_service import AchievementService
from app.services.analytics_service import AnalyticsService
from tests.helpers.data_helpers import (
    award_achievement_directly,
    create_test_questions,
    create_test_session_with_responses,
    set_user_level_directly,
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
        user = User(display_name="TestUser", pin="1234", avatar="🐯", level=1)
        db.session.add(user)
        db.session.commit()
        # Access id to ensure it's loaded before returning (prevents DetachedInstanceError)
        _ = user.id
        return user


# ============================================================================
# Milestone Achievement Tests
# ============================================================================

def test_first_victory_achievement(app, test_user):
    """ACH-AWARD-001: first-victory achievement awarded after answering 1 question."""
    with app.app_context():
        # Create a question and answer it
        questions = create_test_questions(1, 1)
        responses_data = [{
            'question_id': questions[0].id,
            'answer': questions[0].correct_answer,
            'is_correct': True,
            'duration_ms': 3000
        }]
        
        session = create_test_session_with_responses(test_user.id, responses_data)
        
        # Get user and compute metrics, then check and award achievements
        user = db.session.get(User, test_user.id)
        metrics = AnalyticsService.compute_user_metrics(user.id)
        AchievementService.ensure_achievements(user, metrics, session_id=session.id)
        
        # Verify achievement was awarded
        achievement = Achievement.query.filter_by(
            user_id=test_user.id,
            code="first-victory"
        ).first()
        
        assert achievement is not None
        assert achievement.session_id == session.id


def test_first_steps_achievement(app, test_user):
    """ACH-AWARD-002: first-steps achievement awarded after 10 addition problems at level 1."""
    with app.app_context():
        # Create 10 addition questions at level 1
        questions = create_test_questions(10, 1, operation="addition")
        responses_data = [{
            'question_id': q.id,
            'answer': q.correct_answer,
            'is_correct': True,
            'duration_ms': 3000
        } for q in questions]
        
        session = create_test_session_with_responses(test_user.id, responses_data, level=1)
        
        # Get user and compute metrics, then check and award achievements
        user = db.session.get(User, test_user.id)
        metrics = AnalyticsService.compute_user_metrics(user.id)
        AchievementService.ensure_achievements(user, metrics, session_id=session.id)
        
        # Verify achievement was awarded
        achievement = Achievement.query.filter_by(
            user_id=test_user.id,
            code="first-steps"
        ).first()
        
        assert achievement is not None


def test_question_master_bronze_achievement(app, test_user):
    """ACH-AWARD-003: question-master-bronze achievement awarded after 100+ questions total."""
    with app.app_context():
        # Create multiple sessions totaling 100+ responses
        questions = create_test_questions(110, 1)
        
        # Split into multiple sessions
        for i in range(0, 110, 20):
            session_questions = questions[i:i+20]
            responses_data = [{
                'question_id': q.id,
                'answer': q.correct_answer,
                'is_correct': True,
                'duration_ms': 3000
            } for q in session_questions]
            
            session = create_test_session_with_responses(test_user.id, responses_data)
            # Get user and compute metrics, then check and award achievements
            user = db.session.get(User, test_user.id)
            metrics = AnalyticsService.compute_user_metrics(user.id)
            AchievementService.ensure_achievements(user, metrics, session_id=session.id)
        
        # Verify achievement was awarded
        achievement = Achievement.query.filter_by(
            user_id=test_user.id,
            code="question-master-bronze"
        ).first()
        
        assert achievement is not None


# ============================================================================
# Accuracy Achievement Tests
# ============================================================================

def test_first_steps_achievement(app, test_user):
    """ACH-AWARD-004: first-steps achievement awarded after answering first question."""
    with app.app_context():
        # Create 1 question and answer it
        questions = create_test_questions(1, 1, operation="addition")
        responses_data = [{
            'question_id': questions[0].id,
            'answer': questions[0].correct_answer,
            'is_correct': True,
            'duration_ms': 3000
        }]
        
        session = create_test_session_with_responses(test_user.id, responses_data, level=1)
        
        # Get user and compute metrics, then check and award achievements
        user = db.session.get(User, test_user.id)
        metrics = AnalyticsService.compute_user_metrics(user.id)
        AchievementService.ensure_achievements(user, metrics, session_id=session.id)
        
        # Verify achievement was awarded
        achievement = Achievement.query.filter_by(
            user_id=test_user.id,
            code="first-steps"
        ).first()
        
        assert achievement is not None


def test_speed_demon_bronze_achievement(app, test_user):
    """ACH-AWARD-005: speed-demon-bronze awarded for avg < 5.0s with 10+ questions."""
    with app.app_context():
        # Create 10 questions with average time < 5.0s (use 4.5s)
        questions = create_test_questions(10, 1)
        responses_data = [{
            'question_id': q.id,
            'answer': q.correct_answer,
            'is_correct': True,
            'duration_ms': 4500  # 4.5 seconds per question
        } for q in questions]
        
        session = create_test_session_with_responses(test_user.id, responses_data)
        
        # Get user and compute metrics, then check and award achievements
        user = db.session.get(User, test_user.id)
        metrics = AnalyticsService.compute_user_metrics(user.id)
        AchievementService.ensure_achievements(user, metrics, session_id=session.id)
        
        # Verify achievement was awarded
        achievement = Achievement.query.filter_by(
            user_id=test_user.id,
            code="speed-demon-bronze"
        ).first()
        
        assert achievement is not None


def test_speed_demon_with_multiplier(app, test_user):
    """Test speed-demon achievement with concept speed multiplier (2.0x).
    
    Uses concept c_concept_037 which has speed_multiplier 2.0.
    With 9.0s average, should qualify for bronze (9.0s < 5.0s * 2.0 = 10.0s).
    Without multiplier, 9.0s would NOT qualify (9.0s > 5.0s).
    """
    with app.app_context():
        # Create 10 questions with average time 9.0s (would NOT qualify without multiplier)
        questions = create_test_questions(10, 1)
        responses_data = [{
            'question_id': q.id,
            'answer': q.correct_answer,
            'is_correct': True,
            'duration_ms': 9000  # 9.0 seconds per question
        } for q in questions]
        
        # Use concept_id with 2.0 multiplier (c_concept_037)
        session = create_test_session_with_responses(
            test_user.id, 
            responses_data, 
            concept_id="c_concept_037"
        )
        
        # Get user and compute metrics, then check and award achievements
        user = db.session.get(User, test_user.id)
        metrics = AnalyticsService.compute_user_metrics(user.id)
        AchievementService.ensure_achievements(user, metrics, session_id=session.id)
        
        # Verify achievement was awarded (multiplier should make 9.0s qualify for bronze)
        achievement = Achievement.query.filter_by(
            user_id=test_user.id,
            code="speed-demon-bronze"
        ).first()
        
        assert achievement is not None, "Speed demon bronze should be awarded with 2.0x multiplier (9.0s < 10.0s)"


# ============================================================================
# Speed Achievement Tests
# ============================================================================

def test_speed_demon_gold_achievement(app, test_user):
    """ACH-AWARD-006: speed-demon-gold awarded for avg < 3.0s with 10+ questions."""
    with app.app_context():
        # Create 10 questions with average time < 3.0s but > 2.5s (use 2.8s to get gold, not platinum)
        questions = create_test_questions(10, 1)
        responses_data = [{
            'question_id': q.id,
            'answer': q.correct_answer,
            'is_correct': True,
            'duration_ms': 2800  # 2.8 seconds per question (qualifies for gold, not platinum)
        } for q in questions]
        
        session = create_test_session_with_responses(test_user.id, responses_data)
        
        # Get user and compute metrics, then check and award achievements
        user = db.session.get(User, test_user.id)
        metrics = AnalyticsService.compute_user_metrics(user.id)
        AchievementService.ensure_achievements(user, metrics, session_id=session.id)
        
        # Verify achievement was awarded (check for gold or higher tier)
        achievement = Achievement.query.filter(
            Achievement.user_id == test_user.id,
            Achievement.code.in_(["speed-demon-gold", "speed-demon-platinum", "speed-demon-diamond"])
        ).first()
        
        assert achievement is not None, "Speed demon achievement (gold or higher) should be awarded"


def test_lightning_fast_with_multiplier(app, test_user):
    """Test lightning-fast achievement with concept speed multiplier (2.0x).
    
    Uses concept c_concept_037 which has speed_multiplier 2.0.
    With 9.0s average at level 37, should qualify for bronze (9.0s < 5.0s * 2.0 = 10.0s).
    Without multiplier, 9.0s would NOT qualify (9.0s > 5.0s).
    """
    with app.app_context():
        # Set user level to 37 to match the concept
        set_user_level_directly(test_user.id, 37)
        
        # Create 50 questions at level 37 (minimum for bronze) with average time 9.0s
        questions = create_test_questions(50, 37)
        responses_data = [{
            'question_id': q.id,
            'answer': q.correct_answer,
            'is_correct': True,
            'duration_ms': 9000  # 9.0 seconds per question
        } for q in questions]
        
        # Use concept_id with 2.0 multiplier (c_concept_037) and level 37
        session = create_test_session_with_responses(
            test_user.id, 
            responses_data, 
            level=37,
            concept_id="c_concept_037"
        )
        
        # Get user and compute metrics, then check and award achievements
        user = db.session.get(User, test_user.id)
        metrics = AnalyticsService.compute_user_metrics(user.id)
        
        # Lightning-fast achievements are checked separately via check_lightning_fast_achievements
        lightning_fast_achievements = AchievementService.check_lightning_fast_achievements(user, session.id)
        
        # Verify achievement was awarded (multiplier should make 9.0s qualify for bronze)
        achievement = Achievement.query.filter_by(
            user_id=test_user.id,
            code="lightning-fast-bronze"
        ).first()
        
        assert achievement is not None, "Lightning fast bronze should be awarded with 2.0x multiplier (9.0s < 10.0s)"


# ============================================================================
# Consistency Achievement Tests
# ============================================================================

def test_perfect_streak_bronze_achievement(app, test_user):
    """ACH-AWARD-007: perfect-streak-bronze awarded for 3 consecutive perfect sessions."""
    with app.app_context():
        # Create 3 consecutive perfect sessions (100% accuracy) - bronze requires 3
        for session_num in range(3):
            questions = create_test_questions(10, 1)
            responses_data = [{
                'question_id': q.id,
                'answer': q.correct_answer,
                'is_correct': True,
                'duration_ms': 3000
            } for q in questions]
            
            session = create_test_session_with_responses(test_user.id, responses_data)
            # Get user and compute metrics, then check and award achievements
            user = db.session.get(User, test_user.id)
            metrics = AnalyticsService.compute_user_metrics(user.id)
            AchievementService.ensure_achievements(user, metrics, session_id=session.id)
        
        # Verify achievement was awarded
        achievement = Achievement.query.filter_by(
            user_id=test_user.id,
            code="perfect-streak-bronze"
        ).first()
        
        assert achievement is not None


def test_week_warrior_bronze_achievement(app, test_user):
    """ACH-AWARD-008: week-warrior-bronze awarded for 7 consecutive days with practice."""
    with app.app_context():
        from app.models import Response
        from app.services.analytics_service import AnalyticsService
        
        # Create responses on 7 consecutive days (bronze requires 7 days)
        # Streak is calculated from Response.answered_at dates, not session dates
        base_date = datetime.utcnow()
        questions = create_test_questions(5, 1)
        
        for day_offset in range(7):
            response_date = base_date - timedelta(days=6-day_offset)
            # Create a response for each day
            response = Response(
                session_id=None,  # Can be None for streak calculation
                user_id=test_user.id,
                question_id=questions[0].id,
                submitted_answer=questions[0].correct_answer,
                correct_answer=questions[0].correct_answer,
                is_correct=True,
                duration_ms=3000,
                answered_at=response_date
            )
            db.session.add(response)
        
        db.session.commit()
        
        # Aggregate daily stats to ensure streak calculation works
        from app.services.analytics_service import AnalyticsService
        for day_offset in range(7):
            stat_date = (base_date - timedelta(days=6-day_offset)).date()
            AnalyticsService.aggregate_daily_stats(test_user.id, stat_date)
        
        # Get user and compute metrics, then check and award achievements
        user = db.session.get(User, test_user.id)
        metrics = AnalyticsService.compute_user_metrics(test_user.id)
        AchievementService.ensure_achievements(user, metrics, session_id=None)
        
        # Verify achievement was awarded
        achievement = Achievement.query.filter_by(
            user_id=test_user.id,
            code="week-warrior-bronze"
        ).first()
        
        assert achievement is not None


# ============================================================================
# Progression Achievement Tests
# ============================================================================

def test_first_victory_achievement_verification(app, test_user):
    """ACH-AWARD-009: Verify first-victory is awarded (already tested in test_first_victory_achievement)."""
    # This test is covered by test_first_victory_achievement
    # Keeping as placeholder to maintain test numbering
    pass


def test_first_steps_only_awarded_once(app, test_user):
    """Test that first-steps achievement is only awarded once."""
    with app.app_context():
        # First session - should award first-steps
        questions1 = create_test_questions(1, 1, operation="addition")
        responses_data1 = [{
            'question_id': questions1[0].id,
            'answer': questions1[0].correct_answer,
            'is_correct': True,
            'duration_ms': 3000
        }]
        
        session1 = create_test_session_with_responses(test_user.id, responses_data1, level=1)
        user = db.session.get(User, test_user.id)
        metrics = AnalyticsService.compute_user_metrics(user.id)
        AchievementService.ensure_achievements(user, metrics, session_id=session1.id)
        
        # Verify first achievement was awarded
        achievement1 = Achievement.query.filter_by(
            user_id=test_user.id,
            code="first-steps"
        ).first()
        assert achievement1 is not None, "First Steps should be awarded on first question"
        
        # Second session - should NOT award first-steps again
        questions2 = create_test_questions(1, 1, operation="addition")
        responses_data2 = [{
            'question_id': questions2[0].id,
            'answer': questions2[0].correct_answer,
            'is_correct': True,
            'duration_ms': 3000
        }]
        
        session2 = create_test_session_with_responses(test_user.id, responses_data2, level=1)
        user = db.session.get(User, test_user.id)
        metrics = AnalyticsService.compute_user_metrics(user.id)
        AchievementService.ensure_achievements(user, metrics, session_id=session2.id)
        
        # Verify only one first-steps achievement exists
        achievement_count = Achievement.query.filter_by(
            user_id=test_user.id,
            code="first-steps"
        ).count()
        
        assert achievement_count == 1, "First Steps should only be awarded once"


def test_first_victory_only_awarded_once(app, test_user):
    """Test that first-victory achievement is only awarded once."""
    with app.app_context():
        # First session - should award first-victory
        questions1 = create_test_questions(1, 1)
        responses_data1 = [{
            'question_id': questions1[0].id,
            'answer': questions1[0].correct_answer,
            'is_correct': True,
            'duration_ms': 3000
        }]
        
        session1 = create_test_session_with_responses(test_user.id, responses_data1)
        user = db.session.get(User, test_user.id)
        metrics = AnalyticsService.compute_user_metrics(user.id)
        AchievementService.ensure_achievements(user, metrics, session_id=session1.id)
        
        # Verify first achievement was awarded
        achievement1 = Achievement.query.filter_by(
            user_id=test_user.id,
            code="first-victory"
        ).first()
        assert achievement1 is not None, "First Victory should be awarded on first session"
        
        # Second session - should NOT award first-victory again
        questions2 = create_test_questions(1, 1)
        responses_data2 = [{
            'question_id': questions2[0].id,
            'answer': questions2[0].correct_answer,
            'is_correct': True,
            'duration_ms': 3000
        }]
        
        session2 = create_test_session_with_responses(test_user.id, responses_data2)
        user = db.session.get(User, test_user.id)
        metrics = AnalyticsService.compute_user_metrics(user.id)
        AchievementService.ensure_achievements(user, metrics, session_id=session2.id)
        
        # Verify only one first-victory achievement exists
        achievement_count = Achievement.query.filter_by(
            user_id=test_user.id,
            code="first-victory"
        ).count()
        
        assert achievement_count == 1, "First Victory should only be awarded once"


def test_first_victory_not_awarded_on_incomplete_session(app, test_user):
    """Test that first-victory achievement is NOT awarded when session is not completed."""
    with app.app_context():
        # Create a session with responses but NOT completed
        questions = create_test_questions(1, 1)
        responses_data = [{
            'question_id': questions[0].id,
            'answer': questions[0].correct_answer,
            'is_correct': True,
            'duration_ms': 3000
        }]
        
        # Create session but don't mark it as completed (completed_at = None)
        from app.models import PracticeSession, Response, Question
        session = PracticeSession(
            user_id=test_user.id,
            mode="standard",
            level=1,
            started_at=datetime.utcnow(),
            completed_at=None  # Session is NOT completed
        )
        db.session.add(session)
        db.session.flush()
        
        # Add response
        for resp_data in responses_data:
            question = db.session.get(Question, resp_data['question_id'])
            response = Response(
                session_id=session.id,
                user_id=test_user.id,
                question_id=question.id,
                submitted_answer=resp_data['answer'],
                correct_answer=question.correct_answer,
                is_correct=resp_data['is_correct'],
                duration_ms=resp_data['duration_ms'],
                answered_at=datetime.utcnow()
            )
            db.session.add(response)
        
        db.session.commit()
        
        # Now check achievements - should NOT award first-victory
        user = db.session.get(User, test_user.id)
        metrics = AnalyticsService.compute_user_metrics(user.id)
        AchievementService.ensure_achievements(user, metrics, session_id=session.id)
        
        # Verify first-victory was NOT awarded
        achievement = Achievement.query.filter_by(
            user_id=test_user.id,
            code="first-victory"
        ).first()
        
        assert achievement is None, "First Victory should NOT be awarded when session is not completed"


def test_first_victory_awarded_only_on_completed_session(app, test_user):
    """Test that first-victory achievement IS awarded when session IS completed."""
    with app.app_context():
        # Create a completed session
        questions = create_test_questions(1, 1)
        responses_data = [{
            'question_id': questions[0].id,
            'answer': questions[0].correct_answer,
            'is_correct': True,
            'duration_ms': 3000
        }]
        
        # Create test session with responses (this helper creates completed sessions)
        session = create_test_session_with_responses(test_user.id, responses_data)
        
        # Verify session is completed
        assert session.completed_at is not None, "Test session should be completed"
        
        # Now check achievements - should award first-victory
        user = db.session.get(User, test_user.id)
        metrics = AnalyticsService.compute_user_metrics(user.id)
        AchievementService.ensure_achievements(user, metrics, session_id=session.id)
        
        # Verify first-victory WAS awarded
        achievement = Achievement.query.filter_by(
            user_id=test_user.id,
            code="first-victory"
        ).first()
        
        assert achievement is not None, "First Victory should be awarded when session is completed"
        assert achievement.session_id == session.id, "Achievement should be linked to the completed session"

