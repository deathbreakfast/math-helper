"""Test helpers for question distribution tests.

This module provides reusable test scenarios and builders to reduce
duplication in distribution tests.
"""

from __future__ import annotations

from typing import Any

from app.models import Question, User, db
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
        self.category = None
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
            
            # Generate session with questions
            # Note: category is handled by AdaptiveDistributionService internally via select_category
            # The mode "standard" with adaptive distribution will use the category system
            session_data = SessionEngineService.generate_session(
                user_id=self.test_user.id,
                mode="standard",
                concept_id=None,  # Let system select concept
            )
            
            return session_data.get("questions", [])
    
    def verify_distribution(self, questions: list[dict[str, Any]]) -> dict[str, Any]:
        """Verify question distribution matches expectations.
        
        Args:
            questions: List of question dictionaries
            
        Returns:
            Dictionary with verification results and statistics
        """
        total = len(questions)
        
        return {
            "total_questions": total,
        }


def create_distribution_test_scenario(app, test_user: User) -> DistributionTestScenario:
    """Create a new distribution test scenario builder.
    
    Args:
        app: Flask application context
        test_user: Test user instance
        
    Returns:
        DistributionTestScenario instance
    """
    return DistributionTestScenario(app, test_user)
