"""Backend tests for complete session endpoint XP breakdown.

Tests verify that XP breakdown correct_count matches the session's actual
correct answer count, especially when there are multiple responses per question.
"""

import pytest
from datetime import datetime, timedelta

from app import create_app, db
from app.models import PracticeSession, Question, Response, User
from app.services.concept_xp_service import ConceptXPService
from app.services.practice_service import PracticeService
from tests.helpers.test_data_helpers import create_test_questions, create_test_session_with_responses


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


def test_xp_breakdown_correct_count_matches_session(app, test_user):
    """Test that completing a 10-question session with 10 correct returns xp_breakdown.correct_count == 10."""
    with app.app_context():
        from app.routes.practice import practice_bp
        app.register_blueprint(practice_bp)
        
        # Create 10 questions
        questions = create_test_questions(10, 1, "addition")
        db.session.add_all(questions)
        db.session.commit()
        
        # Create session with 10 correct responses
        responses_data = [
            {'question_id': q.id, 'answer': q.correct_answer, 'is_correct': True, 'duration_ms': 3000}
            for q in questions
        ]
        session = create_test_session_with_responses(
            test_user.id, responses_data, completed_at=None
        )
        
        # Mark session as incomplete initially (will be completed by endpoint) and set concept_id
        session.concept_id = "c_add_1s"
        session.completed_at = None
        db.session.add(session)
        db.session.commit()
        
        # Call complete endpoint
        with app.test_client() as client:
            response = client.post(
                f'/api/practice/sessions/{session.id}/complete',
                json={'total_duration_ms': 30000}
            )
            assert response.status_code == 200
            
            data = response.get_json()
            
            # Verify XP breakdown correct_count matches session
            level_up = data['level_up']
            assert level_up is not None
            xp_breakdown = level_up['xp_breakdown']
            assert xp_breakdown['correct_count'] == 10, f"Expected 10, got {xp_breakdown['correct_count']}"
            
            # Verify session stats
            session_data = data['session']
            assert session_data['total_questions'] == 10
            assert session_data['correct_count'] == 10


def test_xp_breakdown_counts_unique_questions_only(app, test_user):
    """Test that XP breakdown counts unique questions, not all responses.
    
    If a user answers the same question multiple times, we should only count
    it once (using the latest response).
    """
    with app.app_context():
        from app.routes.practice import practice_bp
        app.register_blueprint(practice_bp)
        
        # Create 10 questions
        questions = create_test_questions(10, 1, "addition")
        db.session.add_all(questions)
        db.session.commit()
        
        # Create session
        session = PracticeService.create_session(
            user_id=test_user.id,
            mode="standard",
            level=1,
            concept_id="c_add_1s"
        )
        db.session.commit()
        
        # Add responses: 10 correct answers, but 5 of them are answered twice
        # This creates 15 total responses, but only 10 unique questions
        base_time = datetime.utcnow()
        for i, question in enumerate(questions):
            # First answer (correct)
            response1 = Response(
                session_id=session.id,
                user_id=test_user.id,
                question_id=question.id,
                submitted_answer=question.correct_answer,
                correct_answer=question.correct_answer,
                is_correct=True,
                duration_ms=3000,
                answered_at=base_time + timedelta(seconds=i)
            )
            db.session.add(response1)
            
            # For first 5 questions, add a second response (also correct)
            if i < 5:
                response2 = Response(
                    session_id=session.id,
                    user_id=test_user.id,
                    question_id=question.id,
                    submitted_answer=question.correct_answer,
                    correct_answer=question.correct_answer,
                    is_correct=True,
                    duration_ms=2000,
                    answered_at=base_time + timedelta(seconds=i + 100)  # Later timestamp
                )
                db.session.add(response2)
        
        db.session.commit()
        
        # Verify we have 15 responses total
        all_responses = Response.query.filter_by(session_id=session.id).all()
        assert len(all_responses) == 15, "Should have 15 total responses"
        
        # Call complete endpoint
        with app.test_client() as client:
            response = client.post(
                f'/api/practice/sessions/{session.id}/complete',
                json={'total_duration_ms': 30000}
            )
            assert response.status_code == 200
            
            data = response.get_json()
            
            # Verify XP breakdown correct_count is 10 (unique questions), not 15 (all responses)
            level_up = data['level_up']
            assert level_up is not None
            xp_breakdown = level_up['xp_breakdown']
            assert xp_breakdown['correct_count'] == 10, \
                f"Expected 10 (unique questions), got {xp_breakdown['correct_count']} (should not count duplicate responses)"
            
            # Verify session stats
            session_data = data['session']
            assert session_data['total_questions'] == 10
            assert session_data['correct_count'] == 10


def test_xp_breakdown_cross_session_isolation(app, test_user):
    """Test that XP breakdown is isolated to the session being completed.
    
    Create Session A with some questions (do not complete).
    Create Session B with 10 questions, complete with exactly 10/10 correct.
    Assert Session B returns xp_breakdown.correct_count == 10 (not inflated by Session A).
    """
    with app.app_context():
        from app.routes.practice import practice_bp
        app.register_blueprint(practice_bp)
        
        # Create questions for Session A
        questions_a = create_test_questions(5, 1, "addition")
        db.session.add_all(questions_a)
        
        # Create questions for Session B
        questions_b = create_test_questions(10, 1, "addition")
        db.session.add_all(questions_b)
        
        db.session.commit()
        
        # Create Session A with 5 questions (don't complete)
        responses_data_a = [
            {'question_id': q.id, 'answer': q.correct_answer, 'is_correct': True, 'duration_ms': 3000}
            for q in questions_a
        ]
        session_a = create_test_session_with_responses(
            test_user.id, responses_data_a, completed_at=None
        )
        session_a.concept_id = "c_add_1s"
        session_a.completed_at = None  # Keep it incomplete
        db.session.add(session_a)
        db.session.commit()
        
        # Create Session B with 10 questions (will complete)
        responses_data_b = [
            {'question_id': q.id, 'answer': q.correct_answer, 'is_correct': True, 'duration_ms': 3000}
            for q in questions_b
        ]
        session_b = create_test_session_with_responses(
            test_user.id, responses_data_b, completed_at=None
        )
        session_b.concept_id = "c_add_1s"
        session_b.completed_at = None  # Will be completed by endpoint
        db.session.add(session_b)
        db.session.commit()
        
        # Verify Session A is incomplete
        assert session_a.completed_at is None
        
        # Call complete endpoint for Session B
        with app.test_client() as client:
            response = client.post(
                f'/api/practice/sessions/{session_b.id}/complete',
                json={'total_duration_ms': 30000}
            )
            assert response.status_code == 200
            
            data = response.get_json()
            
            # Verify XP breakdown correct_count is exactly 10 (Session B only), not 15
            level_up = data['level_up']
            assert level_up is not None
            xp_breakdown = level_up['xp_breakdown']
            assert xp_breakdown['correct_count'] == 10, \
                f"Expected 10 (Session B only), got {xp_breakdown['correct_count']} (should not include Session A)"
            
            # Verify session stats
            session_data = data['session']
            assert session_data['total_questions'] == 10
            assert session_data['correct_count'] == 10


def test_xp_breakdown_uses_latest_response_per_question(app, test_user):
    """Test that when a question is answered multiple times, we use the latest response.
    
    Create a session where:
    - Question 1: answered incorrectly first, then correctly
    - Question 2: answered correctly first, then incorrectly
    - Other questions: answered correctly once
    
    XP breakdown should count Question 1 as correct (latest) and Question 2 as incorrect (latest).
    """
    with app.app_context():
        from app.routes.practice import practice_bp
        app.register_blueprint(practice_bp)
        
        # Create 10 questions
        questions = create_test_questions(10, 1, "addition")
        db.session.add_all(questions)
        db.session.commit()
        
        # Create session
        session = PracticeService.create_session(
            user_id=test_user.id,
            mode="standard",
            level=1,
            concept_id="c_add_1s"
        )
        db.session.commit()
        
        base_time = datetime.utcnow()
        
        # Add responses
        for i, question in enumerate(questions):
            if i == 0:
                # Question 1: wrong first, then correct (should count as correct)
                wrong_response = Response(
                    session_id=session.id,
                    user_id=test_user.id,
                    question_id=question.id,
                    submitted_answer="999",  # Wrong answer
                    correct_answer=question.correct_answer,
                    is_correct=False,
                    duration_ms=2000,
                    answered_at=base_time + timedelta(seconds=i)
                )
                db.session.add(wrong_response)
                
                correct_response = Response(
                    session_id=session.id,
                    user_id=test_user.id,
                    question_id=question.id,
                    submitted_answer=question.correct_answer,
                    correct_answer=question.correct_answer,
                    is_correct=True,
                    duration_ms=3000,
                    answered_at=base_time + timedelta(seconds=i + 100)  # Later
                )
                db.session.add(correct_response)
            elif i == 1:
                # Question 2: correct first, then wrong (should count as wrong)
                correct_response = Response(
                    session_id=session.id,
                    user_id=test_user.id,
                    question_id=question.id,
                    submitted_answer=question.correct_answer,
                    correct_answer=question.correct_answer,
                    is_correct=True,
                    duration_ms=2000,
                    answered_at=base_time + timedelta(seconds=i)
                )
                db.session.add(correct_response)
                
                wrong_response = Response(
                    session_id=session.id,
                    user_id=test_user.id,
                    question_id=question.id,
                    submitted_answer="999",  # Wrong answer
                    correct_answer=question.correct_answer,
                    is_correct=False,
                    duration_ms=3000,
                    answered_at=base_time + timedelta(seconds=i + 100)  # Later
                )
                db.session.add(wrong_response)
            else:
                # Other questions: answered correctly once
                response = Response(
                    session_id=session.id,
                    user_id=test_user.id,
                    question_id=question.id,
                    submitted_answer=question.correct_answer,
                    correct_answer=question.correct_answer,
                    is_correct=True,
                    duration_ms=3000,
                    answered_at=base_time + timedelta(seconds=i)
                )
                db.session.add(response)
        
        db.session.commit()
        
        # Call complete endpoint
        with app.test_client() as client:
            response = client.post(
                f'/api/practice/sessions/{session.id}/complete',
                json={'total_duration_ms': 30000}
            )
            assert response.status_code == 200
            
            data = response.get_json()
            
            # Verify XP breakdown correct_count is 9 (10 questions - 1 wrong = 9 correct)
            # Question 1: latest response is correct ✓
            # Question 2: latest response is wrong ✗
            # Questions 3-10: all correct ✓✓✓✓✓✓✓✓
            level_up = data['level_up']
            assert level_up is not None
            xp_breakdown = level_up['xp_breakdown']
            assert xp_breakdown['correct_count'] == 9, \
                f"Expected 9 (Q1 correct, Q2 wrong, Q3-10 correct), got {xp_breakdown['correct_count']}"
            
            # Verify session stats
            session_data = data['session']
            assert session_data['total_questions'] == 10
            assert session_data['correct_count'] == 9


def test_xp_breakdown_multiplier_delta_calculation(app, test_user):
    """Test that multipliers are calculated as deltas (0.03 + 0.32 = 0.35, total = 1.35).
    
    Verify that multipliers are treated as bonus deltas over 1.0:
    - Individual multipliers stored as factors (1.03, 1.32) but returned as deltas (0.03, 0.32)
    - Total multiplier = 1.0 + sum(deltas) = 1.0 + 0.03 + 0.32 = 1.35
    - Not sum(factors) = 1.03 + 1.32 = 2.35
    """
    with app.app_context():
        from app.routes.practice import practice_bp
        app.register_blueprint(practice_bp)
        
        # Create questions
        questions = create_test_questions(10, 1, "addition")
        db.session.add_all(questions)
        db.session.commit()
        
        # Create session with 10 correct responses
        responses_data = [
            {'question_id': q.id, 'answer': q.correct_answer, 'is_correct': True, 'duration_ms': 1500}
            for q in questions
        ]
        session = create_test_session_with_responses(
            test_user.id, responses_data, completed_at=None
        )
        session.concept_id = "c_add_1s"
        session.completed_at = None
        db.session.add(session)
        db.session.commit()
        
        # Award achievements that have multipliers
        # Using first-steps (1.01 factor -> 0.01 delta) and accuracy-ace-gold (1.03 factor -> 0.03 delta)
        # These are small multipliers that are easy to verify
        from app.models import Achievement
        from app.services.achievement_service import AchievementService
        
        # Create first-steps achievement (multiplier factor 1.01 -> delta 0.01)
        from tests.helpers.data_helpers import award_achievement_directly
        award_achievement_directly(test_user.id, "first-steps", session_id=session.id)
        
        # For accuracy-ace-gold, we need a session with 100% accuracy and 10+ questions
        # Since we have 10 correct out of 10, this should qualify
        from app.services.achievement_service import AchievementService
        from app.services.analytics_service import AnalyticsService
        
        # Check for accuracy-ace achievements
        user = db.session.get(User, test_user.id)
        metrics = AnalyticsService.compute_user_metrics(user.id)
        AchievementService.ensure_achievements(user, metrics, session_id=session.id)
        
        # Manually award accuracy-ace-gold if not already awarded (for test simplicity)
        existing_ace = Achievement.query.filter_by(
            user_id=test_user.id, code="accuracy-ace-gold", session_id=session.id
        ).first()
        if not existing_ace:
            award_achievement_directly(test_user.id, "accuracy-ace-gold", session_id=session.id)
        
        db.session.commit()
        
        # Call complete endpoint
        with app.test_client() as client:
            response = client.post(
                f'/api/practice/sessions/{session.id}/complete',
                json={'total_duration_ms': 15000}
            )
            assert response.status_code == 200
            
            data = response.get_json()
            
            level_up = data['level_up']
            assert level_up is not None
            xp_breakdown = level_up['xp_breakdown']
            
            # Verify multipliers are returned as deltas (not factors)
            multipliers = xp_breakdown.get('multipliers', [])
            assert len(multipliers) >= 1, "Should have at least one multiplier"
            
            # Check that multipliers are deltas (should be < 1.0 for typical multipliers)
            # first-steps: 1.01 factor -> 0.01 delta
            # accuracy-ace-gold: 1.03 factor -> 0.03 delta
            for mult in multipliers:
                assert mult['multiplier'] < 1.0, f"Multiplier should be delta (< 1.0), got {mult['multiplier']}"
            
            # Verify total_multiplier calculation
            # Should be 1.0 + sum(deltas), not sum(factors)
            total_multiplier = xp_breakdown.get('total_multiplier', 1.0)
            
            # Calculate expected: sum of deltas
            expected_deltas_sum = sum(m['multiplier'] for m in multipliers)
            expected_total = 1.0 + expected_deltas_sum
            
            # Total should be close to expected (allowing for floating point precision)
            assert abs(total_multiplier - expected_total) < 0.001, \
                f"Total multiplier should be 1.0 + sum(deltas) = {expected_total}, got {total_multiplier}"
            
            # Verify it's NOT the sum of factors (which would be much larger)
            # If we had factors 1.01 and 1.03, sum would be 2.04, but we expect 1.04
            assert total_multiplier < 2.0, \
                f"Total multiplier should be < 2.0 (sum of factors would be >= 2.0), got {total_multiplier}"

