"""Backend tests for Perfect Streak achievements.

Tests verify that Perfect Streak achievements are correctly awarded for
consecutive perfect sessions.
"""

import pytest
from datetime import datetime

from app import create_app, db
from app.models import Achievement, PracticeSession, Question, Response, User
from app.services.achievement_service import AchievementService
from app.services.analytics_service import AnalyticsService
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


def test_perfect_streak_bronze_3_sessions(app, test_user):
    """Test that Perfect Streak (Bronze) is awarded for 3 consecutive perfect sessions."""
    with app.app_context():
        # Create 3 consecutive perfect sessions (100% accuracy)
        for session_num in range(3):
            questions = create_test_questions(10)
            responses_data = [{
                'question_id': q.id,
                'answer': q.correct_answer,
                'is_correct': True,
                'duration_ms': 3000
            } for q in questions]
            
            session = create_test_session_with_responses(test_user.id, responses_data)
            user = db.session.get(User, test_user.id)
            metrics = AnalyticsService.compute_user_metrics(user.id)
            AchievementService.ensure_achievements(user, metrics, session_id=session.id)
        
        # Verify achievement was awarded
        achievement = Achievement.query.filter_by(
            user_id=test_user.id,
            code="perfect-streak-bronze"
        ).first()
        
        assert achievement is not None, "Perfect Streak (Bronze) should be awarded for 3 consecutive perfect sessions"


def test_perfect_streak_silver_5_sessions(app, test_user):
    """Test that Perfect Streak (Silver) is awarded for 5 consecutive perfect sessions."""
    with app.app_context():
        # Create 5 consecutive perfect sessions (100% accuracy)
        for session_num in range(5):
            questions = create_test_questions(10)
            responses_data = [{
                'question_id': q.id,
                'answer': q.correct_answer,
                'is_correct': True,
                'duration_ms': 3000
            } for q in questions]
            
            session = create_test_session_with_responses(test_user.id, responses_data)
            user = db.session.get(User, test_user.id)
            metrics = AnalyticsService.compute_user_metrics(user.id)
            AchievementService.ensure_achievements(user, metrics, session_id=session.id)
        
        # Verify achievement was awarded
        achievement = Achievement.query.filter_by(
            user_id=test_user.id,
            code="perfect-streak-silver"
        ).first()
        
        assert achievement is not None, "Perfect Streak (Silver) should be awarded for 5 consecutive perfect sessions"


def test_perfect_streak_broken_by_imperfect_session(app, test_user):
    """Test that one imperfect session breaks the perfect streak."""
    with app.app_context():
        # Create 2 perfect sessions
        for session_num in range(2):
            questions = create_test_questions(10)
            responses_data = [{
                'question_id': q.id,
                'answer': q.correct_answer,
                'is_correct': True,
                'duration_ms': 3000
            } for q in questions]
            
            session = create_test_session_with_responses(test_user.id, responses_data)
            user = db.session.get(User, test_user.id)
            metrics = AnalyticsService.compute_user_metrics(user.id)
            AchievementService.ensure_achievements(user, metrics, session_id=session.id)
        
        # Create one imperfect session (not 100% accuracy)
        questions = create_test_questions(10)
        responses_data = []
        for i, q in enumerate(questions):
            responses_data.append({
                'question_id': q.id,
                'answer': q.correct_answer if i < 9 else '999',  # 9 correct, 1 wrong
                'is_correct': i < 9,
                'duration_ms': 3000
            })
        
        session = create_test_session_with_responses(test_user.id, responses_data)
        user = db.session.get(User, test_user.id)
        metrics = AnalyticsService.compute_user_metrics(user.id)
        AchievementService.ensure_achievements(user, metrics, session_id=session.id)
        
        # Verify NO achievement was awarded (streak broken)
        achievement = Achievement.query.filter(
            Achievement.user_id == test_user.id,
            Achievement.code.like("perfect-streak-%")
        ).first()
        
        assert achievement is None, "Perfect Streak should NOT be awarded when streak is broken"


def test_perfect_streak_silver_with_bronze_exists_once(app, test_user):
    """Test that perfect-streak-silver is awarded after 5 consecutive perfect sessions.
    
    Verifies:
    - silver is awarded
    - exactly one bronze exists
    - bronze was NOT awarded/linked in the silver-award session
    """
    with app.app_context():
        sessions = []
        # Create 5 consecutive perfect sessions
        for session_num in range(5):
            questions = create_test_questions(10)
            responses_data = [{
                'question_id': q.id,
                'answer': q.correct_answer,
                'is_correct': True,
                'duration_ms': 3000
            } for q in questions]
            
            session = create_test_session_with_responses(test_user.id, responses_data)
            sessions.append(session)
            user = db.session.get(User, test_user.id)
            metrics = AnalyticsService.compute_user_metrics(user.id)
            AchievementService.ensure_achievements(user, metrics, session_id=session.id)
            
            # After session 4, verify bronze count is still 1 (not awarded again)
            if session_num == 3:  # session_num is 0-indexed, so 3 is the 4th session
                bronze_count_after_4 = Achievement.query.filter(
                    Achievement.user_id == test_user.id,
                    Achievement.code == "perfect-streak-bronze"
                ).count()
                assert bronze_count_after_4 == 1, "Bronze should NOT be awarded at session 4 (already awarded at session 3)"
                
                # Verify bronze is NOT linked to session 4
                bronze_in_session_4 = Achievement.query.filter(
                    Achievement.user_id == test_user.id,
                    Achievement.code == "perfect-streak-bronze",
                    Achievement.session_id == sessions[3].id
                ).first()
                assert bronze_in_session_4 is None, "Bronze should NOT be linked to session 4"
        
        # Verify silver was awarded
        silver_achievement = Achievement.query.filter_by(
            user_id=test_user.id,
            code="perfect-streak-silver"
        ).first()
        
        assert silver_achievement is not None, "Perfect Streak (Silver) should be awarded for 5 consecutive perfect sessions"
        
        # Verify exactly one bronze exists
        bronze_count = Achievement.query.filter(
            Achievement.user_id == test_user.id,
            Achievement.code == "perfect-streak-bronze"
        ).count()
        assert bronze_count == 1, "Should have exactly one perfect-streak-bronze achievement"
        
        # Verify bronze was NOT awarded/linked in the silver-award session (session 5)
        silver_session_id = sessions[4].id
        bronze_in_silver_session = Achievement.query.filter(
            Achievement.user_id == test_user.id,
            Achievement.code == "perfect-streak-bronze",
            Achievement.session_id == silver_session_id
        ).first()
        
        assert bronze_in_silver_session is None, "Bronze should NOT be awarded/linked in the silver-award session"


def test_perfect_streak_broken_then_re_earned_bronze(app, test_user):
    """Test that perfect streak can be re-earned after being broken.
    
    Verifies:
    - 3 perfect sessions awards bronze
    - 1 imperfect session breaks streak
    - 2 perfect sessions does NOT award silver (need 5 total)
    - 1 more perfect session awards bronze again (3 in new run)
    - Total bronze count becomes 2 (one per uninterrupted run)
    """
    with app.app_context():
        # Create 3 perfect sessions
        for session_num in range(3):
            questions = create_test_questions(10)
            responses_data = [{
                'question_id': q.id,
                'answer': q.correct_answer,
                'is_correct': True,
                'duration_ms': 3000
            } for q in questions]
            
            session = create_test_session_with_responses(test_user.id, responses_data)
            user = db.session.get(User, test_user.id)
            metrics = AnalyticsService.compute_user_metrics(user.id)
            AchievementService.ensure_achievements(user, metrics, session_id=session.id)
        
        # Verify bronze exists
        bronze1 = Achievement.query.filter_by(
            user_id=test_user.id,
            code="perfect-streak-bronze"
        ).first()
        assert bronze1 is not None, "Perfect Streak (Bronze) should be awarded for 3 consecutive perfect sessions"
        
        # Create 1 imperfect session (breaks streak)
        questions = create_test_questions(10)
        responses_data = []
        for i, q in enumerate(questions):
            responses_data.append({
                'question_id': q.id,
                'answer': q.correct_answer if i < 9 else '999',  # 9 correct, 1 wrong
                'is_correct': i < 9,
                'duration_ms': 3000
            })
        
        imperfect_session = create_test_session_with_responses(test_user.id, responses_data)
        user = db.session.get(User, test_user.id)
        metrics = AnalyticsService.compute_user_metrics(user.id)
        AchievementService.ensure_achievements(user, metrics, session_id=imperfect_session.id)
        
        # Create 2 perfect sessions (total would be 5, but streak was broken)
        for session_num in range(2):
            questions = create_test_questions(10)
            responses_data = [{
                'question_id': q.id,
                'answer': q.correct_answer,
                'is_correct': True,
                'duration_ms': 3000
            } for q in questions]
            
            session = create_test_session_with_responses(test_user.id, responses_data)
            user = db.session.get(User, test_user.id)
            metrics = AnalyticsService.compute_user_metrics(user.id)
            AchievementService.ensure_achievements(user, metrics, session_id=session.id)
        
        # Verify silver does NOT exist (streak was broken, only 2 perfect in new run)
        silver = Achievement.query.filter_by(
            user_id=test_user.id,
            code="perfect-streak-silver"
        ).first()
        assert silver is None, "Silver should NOT be awarded (streak was broken, only 2 perfect in new run)"
        
        # Create 1 more perfect session (now 3 in new run, should award bronze again)
        questions = create_test_questions(10)
        responses_data = [{
            'question_id': q.id,
            'answer': q.correct_answer,
            'is_correct': True,
            'duration_ms': 3000
        } for q in questions]
        
        session = create_test_session_with_responses(test_user.id, responses_data)
        user = db.session.get(User, test_user.id)
        metrics = AnalyticsService.compute_user_metrics(user.id)
        new_achievements = AchievementService.ensure_achievements(user, metrics, session_id=session.id)
        
        # Verify bronze was returned for this session
        bronze_codes = [a.code for a in new_achievements if a.code == "perfect-streak-bronze"]
        assert len(bronze_codes) > 0, "Bronze should be returned for the 3rd perfect session in new run"
        
        # Verify total bronze count is now 2 (one per uninterrupted run)
        bronze_count = Achievement.query.filter(
            Achievement.user_id == test_user.id,
            Achievement.code == "perfect-streak-bronze"
        ).count()
        assert bronze_count == 2, f"Should have exactly 2 bronze achievements (one per run), got {bronze_count}"




