"""Test helpers for question distribution tests.

This module provides reusable test scenarios and builders to reduce
duplication in distribution tests.
"""

from __future__ import annotations

from typing import Any

from app.models import Question, User
from app.services.adaptive_distribution_service import AdaptiveDistributionService


class DistributionTestScenario:
    """Builder for distribution test scenarios."""
    
    def __init__(self, app, test_user: User):
        """Initialize scenario builder.
        
        Args:
            app: Flask application context
            test_user: Test user instance
        """
        self.app = app
        self.test_user = test_user
        self.user_level = test_user.level
        self.category = None
        self.expected_levels = []
        self.question_count = 50
        self.tolerance = 5  # Percentage tolerance for distribution checks
    
    def with_category(self, category: str) -> DistributionTestScenario:
        """Set the distribution category to test.
        
        Args:
            category: Category name (e.g., "level", "bottom_performers", "requirements", "random")
            
        Returns:
            Self for method chaining
        """
        self.category = category
        return self
    
    def with_user_level(self, level: int) -> DistributionTestScenario:
        """Set the user level.
        
        Args:
            level: User level
            
        Returns:
            Self for method chaining
        """
        self.user_level = level
        return self
    
    def expecting_levels(self, levels: list[int]) -> DistributionTestScenario:
        """Set expected levels in distribution.
        
        Args:
            levels: List of expected level numbers
            
        Returns:
            Self for method chaining
        """
        self.expected_levels = levels
        return self
    
    def with_question_count(self, count: int) -> DistributionTestScenario:
        """Set number of questions to generate.
        
        Args:
            count: Number of questions
            
        Returns:
            Self for method chaining
        """
        self.question_count = count
        return self
    
    def with_tolerance(self, tolerance: int) -> DistributionTestScenario:
        """Set percentage tolerance for distribution checks.
        
        Args:
            tolerance: Percentage tolerance (default 5)
            
        Returns:
            Self for method chaining
        """
        self.tolerance = tolerance
        return self
    
    def generate_questions(self) -> list[dict[str, Any]]:
        """Generate questions using the configured scenario.
        
        Returns:
            List of question dictionaries
        """
        with self.app.app_context():
            from app.services.session_engine_service import SessionEngineService
            
            # Set user level if different from current
            if self.test_user.level != self.user_level:
                from tests.helpers.data_helpers import set_user_level_directly
                set_user_level_directly(self.test_user.id, self.user_level)
                self.test_user.level = self.user_level
            
            # Generate session with questions
            # Note: category is handled by AdaptiveDistributionService internally via select_category
            # The mode "standard" with adaptive distribution will use the category system
            session_data = SessionEngineService.generate_session(
                user_id=self.test_user.id,
                mode="standard",
                is_test=False,
                level=self.user_level,
            )
            
            return session_data.get("questions", [])
    
    def verify_distribution(self, questions: list[dict[str, Any]]) -> dict[str, Any]:
        """Verify question distribution matches expectations.
        
        Args:
            questions: List of question dictionaries
            
        Returns:
            Dictionary with verification results and statistics
        """
        from collections import Counter
        
        # Extract levels from questions
        level_counts = Counter()
        for q in questions:
            level = self._extract_level(q)
            level_counts[level] += 1
        
        total = len(questions)
        level_percentages = {level: (count / total) * 100 for level, count in level_counts.items()}
        
        # Verify expected levels are present
        found_levels = set(level_counts.keys())
        expected_set = set(self.expected_levels)
        
        return {
            "level_counts": dict(level_counts),
            "level_percentages": level_percentages,
            "total_questions": total,
            "found_levels": found_levels,
            "expected_levels": expected_set,
            "all_expected_present": expected_set.issubset(found_levels),
            "only_expected_present": found_levels == expected_set,
        }
    
    def _extract_level(self, question: dict[str, Any]) -> int:
        """Extract level from question dictionary.
        
        Args:
            question: Question dictionary
            
        Returns:
            Level number
        """
        # Try to get level from question_id
        question_id = question.get("question_id")
        if question_id:
            question_obj = Question.query.get(question_id)
            if question_obj:
                return question_obj.required_level
        
        # Fall back to difficulty field parsing
        difficulty = question.get("difficulty", "")
        if difficulty.startswith("Level "):
            try:
                return int(difficulty.split(" ")[1])
            except (ValueError, IndexError):
                return 1
        
        return question.get("required_level") or question.get("level") or 1


def verify_level_distribution(
    level_counts: dict[int, int],
    expected_levels: list[int],
    tolerance: int = 5
) -> tuple[bool, str]:
    """Verify that level distribution matches expectations.
    
    Args:
        level_counts: Dictionary mapping level to count
        expected_levels: List of expected levels
        tolerance: Percentage tolerance for distribution checks
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    total = sum(level_counts.values())
    if total == 0:
        return False, "No questions generated"
    
    found_levels = set(level_counts.keys())
    expected_set = set(expected_levels)
    
    # Check all expected levels are present
    if not expected_set.issubset(found_levels):
        missing = expected_set - found_levels
        return False, f"Missing expected levels: {missing}"
    
    # Check distribution is roughly even (if multiple levels expected)
    if len(expected_levels) > 1:
        expected_percentage = 100.0 / len(expected_levels)
        for level in expected_levels:
            count = level_counts.get(level, 0)
            percentage = (count / total) * 100
            min_percentage = expected_percentage - tolerance
            max_percentage = expected_percentage + tolerance
            
            if not (min_percentage <= percentage <= max_percentage):
                return False, (
                    f"Level {level} distribution out of range: "
                    f"got {percentage:.1f}%, expected {min_percentage:.1f}-{max_percentage:.1f}%"
                )
    
    return True, ""


def create_distribution_test_scenario(app, test_user: User) -> DistributionTestScenario:
    """Create a new distribution test scenario builder.
    
    Args:
        app: Flask application context
        test_user: Test user instance
        
    Returns:
        DistributionTestScenario instance
    """
    return DistributionTestScenario(app, test_user)
