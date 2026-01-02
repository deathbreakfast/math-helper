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
        user = User(display_name="TestUser", pin="1234", avatar="🐯", experience=0)
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
    """Test that Accuracy Ace (Silver) is awarded for 90%+ accuracy with 10+ questions."""
    with app.app_context():
        # Silver now requires 90% accuracy (updated requirement)
        # Create 10 questions and answer 9 correctly (90% accuracy, qualifies for silver)
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
        
        # Verify achievement was awarded (should get silver for 90% accuracy)
        achievement = Achievement.query.filter_by(
            user_id=test_user.id,
            code="accuracy-ace-silver"
        ).first()
        
        assert achievement is not None, "Accuracy Ace (Silver) should be awarded for 90% accuracy"
        assert achievement.session_id == session.id


def test_accuracy_ace_gold_achievement(app, test_user):
    """Test that Accuracy Ace (Gold) is awarded for 100% accuracy with 10+ questions."""
    with app.app_context():
        # Gold now requires 100% accuracy
        # Create 10 questions and answer all correctly (100% accuracy)
        questions = create_test_questions(10, 1)
        responses_data = [{
            'question_id': q.id,
            'answer': q.correct_answer,
            'is_correct': True,
            'duration_ms': 3000
        } for q in questions]
        
        session = create_test_session_with_responses(test_user.id, responses_data)
        
        # Check achievements
        accuracy_ace_achievements = AchievementService.check_accuracy_ace_achievements(session)
        
        # Verify gold was awarded for 100% accuracy
        achievement = Achievement.query.filter_by(
            user_id=test_user.id,
            code="accuracy-ace-gold"
        ).first()
        
        assert achievement is not None, "Accuracy Ace (Gold) should be awarded for 100% accuracy"
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


def test_accuracy_ace_highest_tier_only(app, test_user):
    """Test that only the highest qualifying tier is awarded."""
    with app.app_context():
        # Test 100% accuracy should award gold (highest), not silver or bronze
        questions = create_test_questions(10, 1)
        responses_data = [{
            'question_id': q.id,
            'answer': q.correct_answer,
            'is_correct': True,
            'duration_ms': 3000
        } for q in questions]
        session = create_test_session_with_responses(test_user.id, responses_data)
        AchievementService.check_accuracy_ace_achievements(session)
        
        # Should only have gold, not bronze or silver
        gold = Achievement.query.filter_by(user_id=test_user.id, code="accuracy-ace-gold").first()
        bronze = Achievement.query.filter_by(user_id=test_user.id, code="accuracy-ace-bronze").first()
        silver = Achievement.query.filter_by(user_id=test_user.id, code="accuracy-ace-silver").first()
        
        assert gold is not None, "Gold should be awarded for 100% accuracy"
        assert bronze is None, "Bronze should NOT be awarded when gold qualifies"
        assert silver is None, "Silver should NOT be awarded when gold qualifies"


def test_accuracy_ace_multiple_instances_across_sessions(app, test_user):
    """Test that multiple instances of same tier can be earned across sessions."""
    with app.app_context():
        # Session 1: 80% accuracy = bronze
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
        bronze1 = Achievement.query.filter_by(
            user_id=test_user.id, 
            code="accuracy-ace-bronze",
            session_id=session1.id
        ).first()
        assert bronze1 is not None, "Bronze should be awarded in session 1"
        
        # Session 2: 80% accuracy again = another bronze
        questions2 = create_test_questions(10, 1)
        responses_data2 = []
        for i, q in enumerate(questions2):
            responses_data2.append({
                'question_id': q.id,
                'answer': q.correct_answer if i < 8 else '999',  # 8 correct = 80%
                'is_correct': i < 8,
                'duration_ms': 3000
            })
        session2 = create_test_session_with_responses(test_user.id, responses_data2)
        AchievementService.check_accuracy_ace_achievements(session2)
        bronze2 = Achievement.query.filter_by(
            user_id=test_user.id, 
            code="accuracy-ace-bronze",
            session_id=session2.id
        ).first()
        assert bronze2 is not None, "Bronze should be awarded in session 2"
        assert bronze1.id != bronze2.id, "Should be two different bronze achievements"


def test_accuracy_ace_only_one_per_session(app, test_user):
    """Test that only one Accuracy Ace can be awarded per session."""
    with app.app_context():
        # 100% accuracy qualifies for all tiers, but should only award gold
        questions = create_test_questions(10, 1)
        responses_data = [{
            'question_id': q.id,
            'answer': q.correct_answer,
            'is_correct': True,
            'duration_ms': 3000
        } for q in questions]
        session = create_test_session_with_responses(test_user.id, responses_data)
        AchievementService.check_accuracy_ace_achievements(session)
        
        # Count achievements for this session
        achievements = Achievement.query.filter(
            Achievement.user_id == test_user.id,
            Achievement.code.like("accuracy-ace-%"),
            Achievement.session_id == session.id
        ).all()
        
        assert len(achievements) == 1, "Should only award one Accuracy Ace per session"
        assert achievements[0].code == "accuracy-ace-gold", "Should award highest tier (gold)"

