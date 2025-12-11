"""Backend tests for Accuracy Ace achievements.

Tests verify that Accuracy Ace achievements are correctly awarded based on session accuracy
and minimum question count requirements.
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
        user = User(display_name="TestUser", pin="1234", avatar="🐯", level=1)
        db.session.add(user)
        db.session.commit()
        _ = user.id
        return user


def test_accuracy_ace_bronze_achievement(app, test_user):
    """Test that Accuracy Ace (Bronze) is awarded for 80%+ accuracy with 10+ questions."""
    with app.app_context():
        # Create 10 questions and answer 8 correctly (80% accuracy)
        questions = create_test_questions(10, 1)
        responses_data = []
        for i, q in enumerate(questions):
            responses_data.append({
                'question_id': q.id,
                'answer': q.correct_answer if i < 8 else '999',  # 8 correct, 2 wrong
                'is_correct': i < 8,
                'duration_ms': 3000
            })
        
        session = create_test_session_with_responses(test_user.id, responses_data)
        
        # Check achievements
        accuracy_ace_achievements = AchievementService.check_accuracy_ace_achievements(session)
        
        # Verify achievement was awarded
        achievement = Achievement.query.filter_by(
            user_id=test_user.id,
            code="accuracy-ace-bronze"
        ).first()
        
        assert achievement is not None, "Accuracy Ace (Bronze) should be awarded for 80% accuracy"
        assert achievement.session_id == session.id


def test_accuracy_ace_silver_achievement(app, test_user):
    """Test that Accuracy Ace (Silver) is awarded for 85%+ accuracy with 10+ questions."""
    with app.app_context():
        # Create 10 questions and answer 9 correctly (90% accuracy, qualifies for gold, not silver)
        # For silver, we need 85-89% accuracy. Let's use 87% (8.7 correct, round to 9 correct = 90%)
        # Actually, let's use 10 questions with 9 correct = 90%, which qualifies for gold
        # To test silver specifically, we need 85-89%. Let's use 20 questions with 17 correct = 85%
        questions = create_test_questions(20, 1)
        responses_data = []
        for i, q in enumerate(questions):
            responses_data.append({
                'question_id': q.id,
                'answer': q.correct_answer if i < 17 else '999',  # 17 correct, 3 wrong = 85%
                'is_correct': i < 17,
                'duration_ms': 3000
            })
        
        session = create_test_session_with_responses(test_user.id, responses_data)
        
        # Check achievements
        accuracy_ace_achievements = AchievementService.check_accuracy_ace_achievements(session)
        
        # Verify achievement was awarded (should get silver, not bronze, since 85% >= 85% but < 90%)
        achievement = Achievement.query.filter_by(
            user_id=test_user.id,
            code="accuracy-ace-silver"
        ).first()
        
        assert achievement is not None, "Accuracy Ace (Silver) should be awarded for 85% accuracy"
        assert achievement.session_id == session.id


def test_accuracy_ace_gold_achievement(app, test_user):
    """Test that Accuracy Ace (Gold) is awarded for 90%+ accuracy with 10+ questions."""
    with app.app_context():
        # Create 10 questions and answer 9 correctly (90% accuracy, qualifies for gold)
        questions = create_test_questions(10, 1)
        responses_data = []
        for i, q in enumerate(questions):
            responses_data.append({
                'question_id': q.id,
                'answer': q.correct_answer if i < 9 else '999',  # 9 correct, 1 wrong = 90%
                'is_correct': i < 9,
                'duration_ms': 3000
            })
        
        session = create_test_session_with_responses(test_user.id, responses_data)
        
        # Check achievements
        accuracy_ace_achievements = AchievementService.check_accuracy_ace_achievements(session)
        
        # Verify gold was awarded for 90% accuracy
        achievement = Achievement.query.filter_by(
            user_id=test_user.id,
            code="accuracy-ace-gold"
        ).first()
        
        assert achievement is not None, "Accuracy Ace (Gold) should be awarded for 90% accuracy"
        assert achievement.session_id == session.id


def test_accuracy_ace_minimum_questions_requirement(app, test_user):
    """Test that Accuracy Ace is NOT awarded with less than 10 questions."""
    with app.app_context():
        # Create 9 questions and answer all correctly (100% accuracy but < 10 questions)
        questions = create_test_questions(9, 1)
        responses_data = [{
            'question_id': q.id,
            'answer': q.correct_answer,
            'is_correct': True,
            'duration_ms': 3000
        } for q in questions]
        
        session = create_test_session_with_responses(test_user.id, responses_data)
        
        # Check achievements
        accuracy_ace_achievements = AchievementService.check_accuracy_ace_achievements(session)
        
        # Verify NO achievement was awarded
        achievement = Achievement.query.filter(
            Achievement.user_id == test_user.id,
            Achievement.code.like("accuracy-ace-%")
        ).first()
        
        assert achievement is None, "Accuracy Ace should NOT be awarded with less than 10 questions"


def test_accuracy_ace_not_awarded_for_test_sessions(app, test_user):
    """Test that Accuracy Ace is NOT awarded for test sessions."""
    with app.app_context():
        # Create a test session with 100% accuracy
        questions = create_test_questions(10, 1)
        responses_data = [{
            'question_id': q.id,
            'answer': q.correct_answer,
            'is_correct': True,
            'duration_ms': 3000
        } for q in questions]
        
        session = create_test_session_with_responses(test_user.id, responses_data, is_test=True)
        
        # Check achievements
        accuracy_ace_achievements = AchievementService.check_accuracy_ace_achievements(session)
        
        # Verify NO achievement was awarded
        achievement = Achievement.query.filter(
            Achievement.user_id == test_user.id,
            Achievement.code.like("accuracy-ace-%")
        ).first()
        
        assert achievement is None, "Accuracy Ace should NOT be awarded for test sessions"


def test_accuracy_ace_not_awarded_below_threshold(app, test_user):
    """Test that Accuracy Ace is NOT awarded for accuracy below 80%."""
    with app.app_context():
        # Create 10 questions and answer 7 correctly (70% accuracy, below 80% threshold)
        questions = create_test_questions(10, 1)
        responses_data = []
        for i, q in enumerate(questions):
            responses_data.append({
                'question_id': q.id,
                'answer': q.correct_answer if i < 7 else '999',  # 7 correct, 3 wrong
                'is_correct': i < 7,
                'duration_ms': 3000
            })
        
        session = create_test_session_with_responses(test_user.id, responses_data)
        
        # Check achievements
        accuracy_ace_achievements = AchievementService.check_accuracy_ace_achievements(session)
        
        # Verify NO achievement was awarded
        achievement = Achievement.query.filter(
            Achievement.user_id == test_user.id,
            Achievement.code.like("accuracy-ace-%")
        ).first()
        
        assert achievement is None, "Accuracy Ace should NOT be awarded for accuracy below 80%"


def test_accuracy_ace_all_tiers(app, test_user):
    """Test that all Accuracy Ace tiers can be awarded with appropriate accuracy."""
    with app.app_context():
        # Test bronze with 80% accuracy (10 questions, 8 correct)
        questions1 = create_test_questions(10, 1)
        responses_data1 = []
        for i, q in enumerate(questions1):
            responses_data1.append({
                'question_id': q.id,
                'answer': q.correct_answer if i < 8 else '999',  # 8 correct = 80%
                'is_correct': i < 8,
                'duration_ms': 3000
            })
        session1 = create_test_session_with_responses(test_user.id, responses_data1)
        AchievementService.check_accuracy_ace_achievements(session1)
        bronze = Achievement.query.filter_by(user_id=test_user.id, code="accuracy-ace-bronze").first()
        assert bronze is not None, "Bronze should be awarded for 80% accuracy"
        
        # Clean up
        db.session.delete(session1)
        db.session.delete(bronze)
        db.session.commit()
        
        # Test platinum with 95% accuracy (20 questions, 19 correct)
        questions2 = create_test_questions(20, 1)
        responses_data2 = []
        for i, q in enumerate(questions2):
            responses_data2.append({
                'question_id': q.id,
                'answer': q.correct_answer if i < 19 else '999',  # 19 correct = 95%
                'is_correct': i < 19,
                'duration_ms': 3000
            })
        session2 = create_test_session_with_responses(test_user.id, responses_data2)
        AchievementService.check_accuracy_ace_achievements(session2)
        platinum = Achievement.query.filter_by(user_id=test_user.id, code="accuracy-ace-platinum").first()
        assert platinum is not None, "Platinum should be awarded for 95% accuracy"
        
        # Clean up
        db.session.delete(session2)
        db.session.delete(platinum)
        db.session.commit()
        
        # Test grandmaster with 100% accuracy (10 questions, all correct)
        questions3 = create_test_questions(10, 1)
        responses_data3 = [{
            'question_id': q.id,
            'answer': q.correct_answer,
            'is_correct': True,
            'duration_ms': 3000
        } for q in questions3]
        session3 = create_test_session_with_responses(test_user.id, responses_data3)
        AchievementService.check_accuracy_ace_achievements(session3)
        grandmaster = Achievement.query.filter(
            Achievement.user_id == test_user.id,
            Achievement.code.in_(["accuracy-ace-grandmaster", "accuracy-ace-legendary", "accuracy-ace-mythic", "accuracy-ace-divine", "accuracy-ace-champion"])
        ).first()
        assert grandmaster is not None, "Grandmaster or higher (including champion) should be awarded for 100% accuracy"

