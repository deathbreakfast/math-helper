"""Statistical verification tests for question distribution.

These tests verify that the probability distributions work correctly over
large sample sizes. They test the randomness and probability weights of
the category-based adaptive distribution system.

Statistical Validation Strategy:
- Large sample sizes (1000+ iterations) for reliable statistical inference
- Confidence intervals calculated using Wilson score method
- Chi-square goodness of fit tests for multinomial distributions
"""

import pytest
from collections import Counter
from unittest.mock import patch

from app import create_app, db
from app.models import User
from app.services.adaptive_distribution_service import AdaptiveDistributionService
from tests.helpers.data_helpers import set_user_level_directly
from tests.helpers.statistics_helpers import (
    check_distribution_proportion,
    check_distribution_multinomial,
    get_acceptable_range,
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
        user = User(display_name=unique_name, pin="1234", avatar="🐯", level=5)
        db.session.add(user)
        db.session.commit()
        _ = user.id  # Ensure id is loaded
        return user


def test_category_selection_probability(app, test_user):
    """STAT-001: Category selection follows expected probability distribution.
    
    Verifies that over 1000 iterations, the category selection matches:
    - Level: 35%
    - Requirements: 35%
    - Bottom Performers: 20%
    - Random: 10%
    
    Uses Chi-square goodness of fit test to verify the distribution.
    """
    with app.app_context():
        # Run 1000 iterations
        num_iterations = 1000
        category_counts = Counter()
        
        for _ in range(num_iterations):
            category = AdaptiveDistributionService.select_category()
            category_counts[category] += 1
        
        # Expected probabilities
        expected_proportions = {
            "level": 0.35,
            "requirements": 0.35,
            "bottom_performers": 0.20,
            "random": 0.10,
        }
        
        # Convert to lists for chi-square test
        categories = ["level", "requirements", "bottom_performers", "random"]
        observed_counts = [category_counts[cat] for cat in categories]
        expected_props = [expected_proportions[cat] for cat in categories]
        
        # Perform chi-square goodness of fit test
        is_valid, chi_square, p_value = check_distribution_multinomial(
            observed_counts, expected_props, confidence=0.95
        )
        
        # Calculate observed percentages for reporting
        total = sum(observed_counts)
        observed_percentages = {cat: (category_counts[cat] / total * 100) for cat in categories}
        expected_percentages = {cat: (expected_proportions[cat] * 100) for cat in categories}
        
        # Assert that distribution is valid
        assert is_valid, (
            f"Category distribution does not match expected probabilities.\n"
            f"Expected: {expected_percentages}\n"
            f"Observed: {observed_percentages}\n"
            f"Chi-square: {chi_square:.2f}"
        )
        
        # Also verify each category individually with confidence intervals
        for category in categories:
            observed_count = category_counts[category]
            expected_prop = expected_proportions[category]
            is_valid_prop, z_score, (lower_ci, upper_ci) = check_distribution_proportion(
                observed_count, total, expected_prop, confidence=0.95
            )
            
            assert is_valid_prop, (
                f"Category '{category}' proportion is outside confidence interval.\n"
                f"Expected: {expected_prop * 100:.1f}%\n"
                f"Observed: {observed_count / total * 100:.1f}%\n"
                f"95% CI: [{lower_ci:.1f}%, {upper_ci:.1f}%]\n"
                f"Z-score: {z_score:.2f}"
            )


def test_level_category_distribution_weights(app, test_user):
    """STAT-002: Level category distribution weights are correct.
    
    Verifies that within the "level" category, questions are distributed
    with equal weight (33.33%) across user_level-2, user_level-1, and user_level.
    """
    with app.app_context():
        set_user_level_directly(test_user.id, 10)
        
        # Get level category distribution (Type B mode for 3-level distribution)
        distribution = AdaptiveDistributionService.generate_level_category_distribution(10, mode='type_b')
        
        # Should have 3 levels: 8, 9, 10
        assert len(distribution) == 3, f"Expected 3 levels, got {len(distribution)}"
        
        # Verify levels
        levels = [item["level"] for item in distribution]
        assert set(levels) == {8, 9, 10}, f"Expected levels 8, 9, 10, got {levels}"
        
        # Verify weights are approximately equal (should be 1/3 each after normalization)
        weights = [item["weight"] for item in distribution]
        expected_weight = 1.0 / 3.0
        
        for weight in weights:
            assert abs(weight - expected_weight) < 0.01, \
                f"Weights should be approximately 0.333. Got: {weights}"
        
        # Test with lower level (level 2 - can't have level-2)
        distribution_low = AdaptiveDistributionService.generate_level_category_distribution(2, mode='type_b')
        levels_low = [item["level"] for item in distribution_low]
        
        # Should only have levels 1 and 2 (can't have level-2)
        assert set(levels_low) == {1, 2}, f"Expected levels 1, 2, got {levels_low}"
        
        # Weights should be normalized to sum to 1.0
        total_weight = sum(item["weight"] for item in distribution_low)
        assert abs(total_weight - 1.0) < 0.001, \
            f"Weights should sum to 1.0. Got: {total_weight}"


def test_level_selection_from_distribution(app, test_user):
    """STAT-003: Level selection from distribution follows weights.
    
    Verifies that when selecting levels from a distribution, the frequency
    of each level matches the weight over many iterations.
    """
    with app.app_context():
        # Create a test distribution with known weights
        test_distribution = [
            {"level": 5, "weight": 0.5},
            {"level": 6, "weight": 0.3},
            {"level": 7, "weight": 0.2},
        ]
        
        # Run 1000 iterations
        num_iterations = 1000
        level_counts = Counter()
        
        for _ in range(num_iterations):
            level = AdaptiveDistributionService.select_level_from_distribution(test_distribution)
            level_counts[level] += 1
        
        # Verify each level appears with expected frequency
        total = sum(level_counts.values())
        for item in test_distribution:
            level = item["level"]
            expected_prop = item["weight"]
            observed_count = level_counts[level]
            
            is_valid, z_score, (lower_ci, upper_ci) = check_distribution_proportion(
                observed_count, total, expected_prop, confidence=0.95
            )
            
            assert is_valid, (
                f"Level {level} selection frequency does not match weight.\n"
                f"Expected: {expected_prop * 100:.1f}%\n"
                f"Observed: {observed_count / total * 100:.1f}%\n"
                f"95% CI: [{lower_ci:.1f}%, {upper_ci:.1f}%]\n"
                f"Z-score: {z_score:.2f}"
            )


def test_bottom_performers_fallback(app, test_user):
    """STAT-004: Bottom performers category handles missing data gracefully.
    
    Verifies that when a user has no response history, the bottom_performers
    category falls back to level 1 as expected.
    """
    with app.app_context():
        set_user_level_directly(test_user.id, 5)
        
        # User with no response history
        distribution = AdaptiveDistributionService.generate_bottom_performers_category_distribution(
            test_user.id
        )
        
        # Should fallback to level 1
        assert len(distribution) == 1, "Should have one fallback level"
        assert distribution[0]["level"] == 1, "Should fallback to level 1"
        assert distribution[0]["weight"] == 1.0, "Should have full weight on fallback level"


def test_requirements_category_fallback(app, test_user):
    """STAT-005: Requirements category falls back to level category when no requirements.
    
    Verifies that when no requirements are found, the service falls back
    to the level category distribution.
    """
    with app.app_context():
        set_user_level_directly(test_user.id, 1)
        
        # Get requirements category levels (may be empty for low level)
        requirements_levels = AdaptiveDistributionService.get_requirements_category_levels(test_user)
        
        # Generate distribution (should fallback if no requirements)
        distribution = AdaptiveDistributionService.generate_requirements_category_distribution(test_user)
        
        # Should have at least one level (either from requirements or fallback)
        assert len(distribution) > 0, "Should have at least one level in distribution"
        
        # Verify all levels are valid (<= user level)
        for item in distribution:
            assert item["level"] <= test_user.level, \
                f"Level {item['level']} should be <= user level {test_user.level}"
        
        # Verify weights sum to 1.0
        total_weight = sum(item["weight"] for item in distribution)
        assert abs(total_weight - 1.0) < 0.001, \
            f"Weights should sum to 1.0. Got: {total_weight}"



