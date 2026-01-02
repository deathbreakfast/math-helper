"""Service for pure question generation logic."""

from __future__ import annotations

from typing import Any

from ..services.concept_config_service import ConceptConfigService
from ..services.question_service import QuestionService


class QuestionGenerationService:
    """Service for question generation with deterministic inputs."""

    @staticmethod
    def generate_questions_for_concept(
        concept_id: str,
        question_count: int = 10,
        max_retries: int = 3,
    ) -> list[dict[str, Any]]:
        """Generate questions for a concept with retry logic.
        
        Args:
            concept_id: The concept identifier (e.g., "c_concept_001", "c_add_1s")
            question_count: Number of questions to generate (default: 10)
            max_retries: Maximum retry attempts per question (default: 3)
        
        Returns:
            List of question dictionaries
        
        Raises:
            ValueError: If concept_id is unsupported or generation fails after max_retries
        """
        # Get concept configuration
        config = ConceptConfigService.get_concept_config(concept_id)
        if not config:
            raise ValueError(f"Unsupported concept_id for practice session: {concept_id}")
        
        operation = config["operation"]
        questions: list[dict[str, Any]] = []
        
        # Generate questions with retry logic
        for i in range(question_count):
            question_data = None
            for retry in range(max_retries):
                try:
                    question_data = QuestionService.generate_question(
                        operation=operation,
                        concept_id=concept_id,
                        test_constraints=None,
                        config_override=config,
                    )
                    break  # Success, exit retry loop
                except ValueError:
                    # Invalid configuration (e.g., division by zero)
                    if retry >= max_retries - 1:
                        raise
            
            if question_data:
                questions.append(question_data)
        
        return questions

