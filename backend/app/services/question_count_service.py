"""Service for calculating dynamic question counts based on perfect session history."""

from __future__ import annotations

import math

from ..database import log_query
from ..models import PracticeSession, db


class QuestionCountService:
    """Service for calculating question counts using sigmoid growth curve."""

    # Sigmoid parameters
    SIGMOID_K = 0.6
    SIGMOID_CENTER = 5

    # Normalization points: Q(0)=10, Q(13)=50
    MIN_QUESTIONS = 10
    MAX_QUESTIONS = 50
    NORMALIZATION_N = 13

    @staticmethod
    def _sigmoid(n: float) -> float:
        """Calculate sigmoid function: σ(n) = 1 / (1 + e^(-k(n - center))).
        
        Args:
            n: Input value
            
        Returns:
            Sigmoid value between 0 and 1
        """
        return 1.0 / (1.0 + math.exp(-QuestionCountService.SIGMOID_K * (n - QuestionCountService.SIGMOID_CENTER)))

    @staticmethod
    def calculate_question_count(perfect_sessions: int) -> int:
        """Calculate question count based on number of perfect sessions.
        
        Uses sigmoid growth curve normalized so:
        - Q(0) = 10 questions
        - Q(13) = 50 questions
        - Capped at 50 questions
        
        Args:
            perfect_sessions: Number of perfect sessions completed for the concept
            
        Returns:
            Question count (integer between 10 and 50)
        """
        n = float(perfect_sessions)
        
        # Calculate sigmoid values at key points
        sigma_0 = QuestionCountService._sigmoid(0.0)
        sigma_n = QuestionCountService._sigmoid(n)
        sigma_13 = QuestionCountService._sigmoid(QuestionCountService.NORMALIZATION_N)
        
        # Normalize: Q(n) = 10 + round(40 * (σ(n) - σ(0)) / (σ(13) - σ(0)))
        # This ensures Q(0)=10 and Q(13)=50
        denominator = sigma_13 - sigma_0
        if denominator == 0:
            # Fallback to minimum if denominator is zero (shouldn't happen)
            return QuestionCountService.MIN_QUESTIONS
        
        normalized = (sigma_n - sigma_0) / denominator
        question_count = QuestionCountService.MIN_QUESTIONS + round(40 * normalized)
        
        # Clamp to [10, 50]
        return max(QuestionCountService.MIN_QUESTIONS, min(QuestionCountService.MAX_QUESTIONS, question_count))

    @staticmethod
    @log_query
    def count_perfect_sessions(user_id: int, concept_id: str) -> int:
        """Count perfect sessions (100% accuracy) for a user and concept.
        
        Args:
            user_id: User ID
            concept_id: Concept identifier (e.g., "c_concept_001", "c_add_1s")
            
        Returns:
            Count of perfect sessions for the user/concept combination
        """
        count = (
            PracticeSession.query.filter_by(user_id=user_id, concept_id=concept_id)
            .filter(
                PracticeSession.completed_at.isnot(None),
                PracticeSession.accuracy == 100.0,
            )
            .count()
        )
        return count

    @staticmethod
    @log_query
    def get_question_count_for_concept(user_id: int, concept_id: str) -> int:
        """Get the question count for a concept based on perfect session history.
        
        Args:
            user_id: User ID
            concept_id: Concept identifier
            
        Returns:
            Question count (integer between 10 and 50)
        """
        perfect_sessions = QuestionCountService.count_perfect_sessions(user_id, concept_id)
        return QuestionCountService.calculate_question_count(perfect_sessions)
