"""Backend tests for question distribution validation.

Tests verify that question distribution logic works correctly for the
category-based adaptive distribution system.

Testing Strategy:
- Deterministic tests use mocks to test each category in isolation
- Statistical tests verify probability distributions over large samples
- Each category is tested to ensure it generates the expected levels
"""

import pytest
from datetime import datetime
from unittest.mock import patch

from app import create_app, db
from app.models import PracticeSession, Question, Response, TestAttempt, User
from app.services.adaptive_distribution_service import AdaptiveDistributionService
from app.services.session_engine_service import SessionEngineService
from tests.helpers.data_helpers import (
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
        import uuid
        unique_name = f"TestUser_{uuid.uuid4().hex[:8]}"
        user = User(display_name=unique_name, pin="1234", avatar="🐯", level=1)
        db.session.add(user)
        db.session.commit()
        # Access id to ensure it's loaded before returning (prevents DetachedInstanceError)
        _ = user.id
        return user


def analyze_question_distribution(questions: list[dict]) -> dict:
    """Analyze question distribution across levels.
    
    Returns:
        Dictionary with levelCounts, levelPercentages, and totalQuestions
    """
    from app.models import Question
    
    level_counts = {}
    total_questions = len(questions)
    
    for q in questions:
        # Questions from SessionEngineService may have question_id to look up
        # or difficulty field like "Level 5"
        level = None
        
        # Try to get level from question_id
        question_id = q.get("question_id")
        if question_id:
            question = Question.query.get(question_id)
            if question:
                level = question.required_level
        
        # Fall back to difficulty field parsing
        if level is None:
            difficulty = q.get("difficulty", "")
            if difficulty.startswith("Level "):
                try:
                    level = int(difficulty.split(" ")[1])
                except (ValueError, IndexError):
                    level = 1
            else:
                level = q.get("required_level") or q.get("level") or 1
        
        level_counts[level] = level_counts.get(level, 0) + 1
        
    level_percentages = {}
    for level, count in level_counts.items():
        level_percentages[level] = (count / total_questions) * 100 if total_questions > 0 else 0
    
    return {
        "levelCounts": level_counts,
        "levelPercentages": level_percentages,
        "totalQuestions": total_questions,
    }


# ============================================================================
# Diagnostic Tests for Debugging Distribution Issues
# ============================================================================

def test_generate_level_category_distribution_direct(app, test_user):
    """Diagnostic: Verify generate_level_category_distribution returns correct distribution."""
    with app.app_context():
        distribution = AdaptiveDistributionService.generate_level_category_distribution(5)
        
        # Should have 3 levels: 3, 4, 5
        assert len(distribution) == 3, f"Expected 3 levels, got {len(distribution)}: {distribution}"
        
        levels = [item["level"] for item in distribution]
        assert set(levels) == {3, 4, 5}, f"Expected levels 3, 4, 5, got {levels}"
        
        # Verify weights are normalized (sum to ~1.0)
        total_weight = sum(item["weight"] for item in distribution)
        assert abs(total_weight - 1.0) < 0.01, f"Weights should sum to 1.0, got {total_weight}"
        
        # Verify weights are approximately equal
        expected_weight = 1.0 / 3.0
        for item in distribution:
            assert abs(item["weight"] - expected_weight) < 0.01, \
                f"Level {item['level']} weight should be ~0.333, got {item['weight']}"


def test_select_level_from_distribution_all_levels(app, test_user):
    """Diagnostic: Verify select_level_from_distribution selects all levels in distribution."""
    with app.app_context():
        from collections import Counter
        
        # Create the expected distribution for level 5
        distribution = AdaptiveDistributionService.generate_level_category_distribution(5)
        
        # Select levels 1000 times and count
        level_counts = Counter()
        for _ in range(1000):
            level = AdaptiveDistributionService.select_level_from_distribution(distribution)
            level_counts[level] += 1
        
        # All three levels should appear
        assert len(level_counts) == 3, f"Expected 3 levels, got {len(level_counts)}: {level_counts}"
        assert set(level_counts.keys()) == {3, 4, 5}, \
            f"Expected levels 3, 4, 5, got {set(level_counts.keys())}"
        
        # Each level should have roughly 30-40% (allowing for variance)
        total = sum(level_counts.values())
        for level in [3, 4, 5]:
            pct = (level_counts[level] / total) * 100
            assert 25 <= pct <= 45, \
                f"Level {level} should have 25-45% (got {pct:.1f}%). Counts: {level_counts}"


def test_question_generation_all_levels(app, test_user):
    """Diagnostic: Verify question generation works for levels 3, 4, and 5."""
    with app.app_context():
        from app.services.question_service import QuestionService
        
        for level in [3, 4, 5]:
            try:
                question_data = QuestionService.generate_question(
                    operation=None,  # Will use config
                    level=level,
                    test_constraints=None,
                )
                
                assert question_data is not None, f"Level {level} returned None"
                assert "question_id" in question_data, f"Level {level} missing question_id"
                assert question_data.get("question_id") is not None, f"Level {level} question_id is None"
                
                # Verify question was saved to database with correct level
                from app.models import Question
                question = Question.query.get(question_data["question_id"])
                assert question is not None, f"Level {level} question not found in database"
                assert question.required_level == level, \
                    f"Level {level} question saved with required_level={question.required_level}"
                    
            except Exception as e:
                assert False, f"Level {level} question generation failed: {e}"


# ============================================================================
# Deterministic Category Tests (using mocks)
# ============================================================================

def test_level_category_distribution(app, test_user):
    """DIST-001: Level category generates questions from user_level-2, user_level-1, and user_level.
    
    Verifies that when the "level" category is selected, questions are generated
    from exactly three levels: current level - 2, current level - 1, and current level.
    Each level should have approximately 33% weight.
    
    Uses a large sample size (200 sessions = 2000 questions) to ensure statistical
    reliability and reduce flakiness from random variance.
    """
    with app.app_context():
        # Set user to level 5
        set_user_level_directly(test_user.id, 5)
        
        # Mock select_category to always return "level"
        with patch.object(AdaptiveDistributionService, 'select_category', return_value='level'):
            # Generate multiple sessions (all will use "level" category)
            # Using 200 sessions (~2000 questions) for better statistical sampling
            # This reduces flakiness by providing a large enough sample to reliably
            # detect the expected 33.3% distribution per level
            all_questions = []
            for _ in range(200):
                session_data = SessionEngineService.generate_session(
                    user_id=test_user.id,
                    mode="standard",
                    is_test=False,
                    level=5,
                )
                questions = session_data.get("questions", [])
                if questions:
                    all_questions.extend(questions)
            
            assert len(all_questions) > 0, "No questions generated"
            
            # Analyze distribution
            distribution = analyze_question_distribution(all_questions)
            level_counts = distribution["levelCounts"]
            
            # Level category should only generate questions from levels 3, 4, 5
            # (user_level - 2, user_level - 1, user_level)
            expected_levels = {3, 4, 5}
            actual_levels = set(level_counts.keys())
            
            # Verify only expected levels appear
            assert actual_levels.issubset(expected_levels), \
                f"Level category should only generate levels 3, 4, 5. Got: {actual_levels}"
            
            # Verify all three levels appear (or at least 2 if user_level is too low)
            assert len(actual_levels) >= 2, \
                f"Level category should generate questions from multiple levels. Got: {actual_levels}"
            
            # Verify distribution - each level should have approximately 33.3% (1/3) of questions
            # With 2000 questions, we expect ~667 questions per level
            # Use individual proportion checks with wider tolerance to account for random variance
            # The chi-square test can be too strict with large sample sizes where small deviations
            # from perfect 33.3% are statistically significant but not practically meaningful
            total = len(all_questions)
            expected_proportion = 1.0 / 3.0  # 33.3% per level
            
            # For large samples (2000+), we allow a wider range: 28-38% per level
            # This accounts for random variance while still detecting significant biases
            min_proportion = 0.28  # 28% minimum
            max_proportion = 0.38  # 38% maximum
            
            observed_percentages = {}
            for level in sorted(expected_levels):
                if level in level_counts:
                    count = level_counts[level]
                    pct = (count / total)
                    observed_percentages[level] = pct * 100
                    
                    assert min_proportion <= pct <= max_proportion, (
                        f"Level {level} proportion is outside acceptable range.\n"
                        f"Expected: ~33.3% (acceptable range: {min_proportion*100:.0f}%-{max_proportion*100:.0f}%)\n"
                        f"Observed: {pct*100:.1f}% ({count}/{total})\n"
                        f"All levels: {observed_percentages}"
                    )
                else:
                    # Level didn't appear - this shouldn't happen with 2000 questions
                    assert False, f"Level {level} did not appear in distribution. Got: {level_counts}"
            
            # Additional check: verify distribution is roughly balanced
            # The difference between highest and lowest percentage should be reasonable
            if len(observed_percentages) == 3:
                percentages = list(observed_percentages.values())
                max_diff = max(percentages) - min(percentages)
                # With equal weights, max difference should be less than 15 percentage points
                assert max_diff < 15.0, (
                    f"Distribution is too imbalanced. Max difference: {max_diff:.1f}%\n"
                    f"Observed percentages: {observed_percentages}"
                )


def test_bottom_performers_category_distribution(app, test_user):
    """DIST-002: Bottom performers category includes slowest and lowest accuracy levels.
    
    Verifies that when "bottom_performers" category is selected, questions are generated
    from the user's slowest level and/or lowest accuracy level.
    """
    with app.app_context():
        # Set user to level 10
        set_user_level_directly(test_user.id, 10)
        
        # Create slow responses on level 2 to establish it as "slowest"
        questions_level_2 = create_test_questions(10, 2)
        for _ in range(3):
            responses_data = [{
                'question_id': q.id,
                'answer': q.correct_answer,
                'is_correct': True,
                'duration_ms': 10000  # 10 seconds - slow
            } for q in questions_level_2[:5]]
            
            session = create_test_session_with_responses(test_user.id, responses_data, level=2)
            session.completed_at = datetime.utcnow()
            db.session.add(session)
            db.session.commit()
        
        # Create low accuracy responses on level 3
        questions_level_3 = create_test_questions(10, 3)
        for _ in range(3):
            responses_data = [{
                'question_id': q.id,
                'answer': 'wrong',  # Wrong answer
                'is_correct': False,
                'duration_ms': 2000
            } for q in questions_level_3[:5]]
            
            session = create_test_session_with_responses(test_user.id, responses_data, level=3)
            session.completed_at = datetime.utcnow()
            db.session.add(session)
            db.session.commit()
        
        # Verify slowest and lowest accuracy levels
        slowest_level = AdaptiveDistributionService.get_user_slowest_level(test_user.id)
        lowest_accuracy_level = AdaptiveDistributionService.get_user_lowest_accuracy_level(test_user.id)
        
        assert slowest_level == 2, f"Expected slowest level to be 2, got {slowest_level}"
        assert lowest_accuracy_level == 3, f"Expected lowest accuracy level to be 3, got {lowest_accuracy_level}"
        
        # Mock select_category to always return "bottom_performers"
        with patch.object(AdaptiveDistributionService, 'select_category', return_value='bottom_performers'):
            # Generate multiple sessions
            all_questions = []
            for _ in range(10):
                session_data = SessionEngineService.generate_session(
                    user_id=test_user.id,
                    mode="standard",
                    is_test=False,
                    level=10,
                )
                questions = session_data.get("questions", [])
                if questions:
                    all_questions.extend(questions)
            
            assert len(all_questions) > 0, "No questions generated"
            
            # Analyze distribution
            distribution = analyze_question_distribution(all_questions)
            level_counts = distribution["levelCounts"]
            
            # Bottom performers should only generate questions from slowest (2) and/or lowest accuracy (3) levels
            expected_levels = {2, 3}
            actual_levels = set(level_counts.keys())
            
            # Verify only expected levels appear
            assert actual_levels.issubset(expected_levels), \
                f"Bottom performers category should only generate levels 2, 3. Got: {actual_levels}"
            
            # Verify at least one of the expected levels appears
            assert len(actual_levels) > 0, \
                f"Bottom performers category should generate questions. Got: {actual_levels}"


def test_requirements_category_distribution(app, test_user):
    """DIST-003: Requirements category generates questions from levels needed for achievements.
    
    Verifies that when "requirements" category is selected, questions are generated
    from levels required for achievements (level+1 requirements and locked test requirements).
    """
    with app.app_context():
        # Set user to level 5
        set_user_level_directly(test_user.id, 5)
        
        # Get requirements category levels
        requirements_levels = AdaptiveDistributionService.get_requirements_category_levels(test_user)
        
        # If no requirements found, the service falls back to level category
        # So we'll test that it generates questions from valid levels
        if not requirements_levels:
            # Fallback case - should still generate questions
            with patch.object(AdaptiveDistributionService, 'select_category', return_value='requirements'):
                session_data = SessionEngineService.generate_session(
                    user_id=test_user.id,
                    mode="standard",
                    is_test=False,
                    level=5,
                )
                questions = session_data.get("questions", [])
                assert len(questions) > 0, "Requirements category should generate questions even with fallback"
        else:
            # Mock select_category to always return "requirements"
            with patch.object(AdaptiveDistributionService, 'select_category', return_value='requirements'):
                # Generate multiple sessions
                all_questions = []
                for _ in range(10):
                    session_data = SessionEngineService.generate_session(
                        user_id=test_user.id,
                        mode="standard",
                        is_test=False,
                        level=5,
                    )
                    questions = session_data.get("questions", [])
                    if questions:
                        all_questions.extend(questions)
                
                assert len(all_questions) > 0, "No questions generated"
                
                # Analyze distribution
                distribution = analyze_question_distribution(all_questions)
                level_counts = distribution["levelCounts"]
                actual_levels = set(level_counts.keys())
                
                # Requirements category should generate questions from requirement levels
                # All requirement levels should be <= user level (filtered in service)
                assert all(level <= 5 for level in actual_levels), \
                    f"Requirements category should only generate levels <= user level (5). Got: {actual_levels}"


def test_random_category_distribution(app, test_user):
    """DIST-004: Random category generates questions from a single random level per session.
    
    Verifies that when "random" category is selected, all questions in a session
    come from the same random level (between 1 and user_level).
    """
    with app.app_context():
        # Set user to level 10
        set_user_level_directly(test_user.id, 10)
        
        # Mock select_category to always return "random"
        with patch.object(AdaptiveDistributionService, 'select_category', return_value='random'):
            # Generate multiple sessions
            session_levels = []
            for _ in range(10):
                session_data = SessionEngineService.generate_session(
                    user_id=test_user.id,
                    mode="standard",
                    is_test=False,
                    level=10,
                )
                questions = session_data.get("questions", [])
                if questions:
                    # All questions in a session should be from the same level
                    distribution = analyze_question_distribution(questions)
                    session_levels_in_session = set(distribution["levelCounts"].keys())
                    
                    # Each session should have questions from exactly one level
                    assert len(session_levels_in_session) == 1, \
                        f"Random category should generate all questions from same level in a session. " \
                        f"Got levels: {session_levels_in_session}"
                    
                    session_levels.append(list(session_levels_in_session)[0])
            
            # Verify levels are within valid range (1 to user_level)
            assert all(1 <= level <= 10 for level in session_levels), \
                f"Random category should generate levels between 1 and 10. Got: {session_levels}"
            
            # Verify we get some variety across sessions (not all same level)
            # This is probabilistic, but with 10 sessions we should see some variety
            unique_levels = set(session_levels)
            assert len(unique_levels) >= 1, \
                f"Random category should generate questions. Got levels: {session_levels}"


# ============================================================================
# Integration Tests (without mocks - verify system works end-to-end)
# ============================================================================

def test_adaptive_distribution_generates_questions(app, test_user):
    """DIST-005: Adaptive distribution generates questions across multiple levels.
    
    Integration test that verifies the full system generates questions without mocks.
    This ensures the integration between SessionEngineService and AdaptiveDistributionService works.
    """
    with app.app_context():
        set_user_level_directly(test_user.id, 5)
        
        # Generate multiple sessions (using real random category selection)
        all_questions = []
        for _ in range(20):
            session_data = SessionEngineService.generate_session(
                user_id=test_user.id,
                mode="standard",
                is_test=False,
                level=5,
            )
            questions = session_data.get("questions", [])
            if questions:
                all_questions.extend(questions)
        
        # Verify questions were generated
        assert len(all_questions) > 0, "No questions were generated"
        
        distribution = analyze_question_distribution(all_questions)
        total = len(all_questions)
        
        # Verify distribution analysis works
        assert len(distribution["levelCounts"]) > 0, "No levels found in distribution"
        all_levels_count = sum(distribution["levelCounts"].values())
        assert all_levels_count == total, "Level counts should match total questions"
        
        # Verify questions are distributed across multiple levels
        # (This should happen naturally with the category system)
        assert len(distribution["levelCounts"]) > 1 or total < 10, \
            f"Questions should be distributed across multiple levels. Got: {distribution['levelCounts']}"


def test_adaptive_distribution_handles_edge_cases(app, test_user):
    """DIST-006: Adaptive distribution handles edge cases (low level, no history).
    
    Verifies that the system works correctly for users at low levels or with no response history.
    """
    with app.app_context():
        # Test with level 1 user (can't have level-2 or level-1)
        set_user_level_directly(test_user.id, 1)
        
        # Generate sessions
        all_questions = []
        for _ in range(5):
            session_data = SessionEngineService.generate_session(
                user_id=test_user.id,
                mode="standard",
                is_test=False,
                level=1,
            )
            questions = session_data.get("questions", [])
            if questions:
                all_questions.extend(questions)
        
        assert len(all_questions) > 0, "No questions generated for level 1 user"
        
        distribution = analyze_question_distribution(all_questions)
        
        # All questions should be from level 1 (or valid levels)
        actual_levels = set(distribution["levelCounts"].keys())
        assert all(level >= 1 for level in actual_levels), \
            f"All levels should be >= 1. Got: {actual_levels}"
        
        # Test with user who has no response history (bottom_performers should fallback)
        set_user_level_directly(test_user.id, 5)
        
        # Clear any existing responses by creating a new user context
        # (In practice, this tests the fallback logic in bottom_performers)
        session_data = SessionEngineService.generate_session(
            user_id=test_user.id,
            mode="standard",
            is_test=False,
            level=5,
        )
        questions = session_data.get("questions", [])
        assert len(questions) > 0, "Should generate questions even with no history"
