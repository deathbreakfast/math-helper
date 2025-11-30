"""Adaptive distribution service for adjusting question distribution based on test performance."""

from __future__ import annotations

import random
from typing import Any

from ..config.levels_config import LEVELS_CONFIG
from ..database import log_query
from ..models import Response, TestAttempt, User
from ..services.test_eligibility_service import TestEligibilityService


class AdaptiveDistributionService:
    """Service for adaptive question distribution based on test performance."""

    # Levels for slowest questions focus (1-37: up to 12x12 multiplication and basic whole number division)
    SLOWEST_QUESTIONS_LEVELS = list(range(1, 38))  # Levels 1-37

    @staticmethod
    @log_query
    def should_apply_adaptive_distribution(user_id: int, level: int) -> bool:
        """Check if adaptive distribution should be applied for a level.
        
        Returns True if:
        - User has passed the test before
        - User has a recent failed retake (<80% OR slower than historical average)
        """
        # Get the most recent test attempt for this level
        recent_attempt = TestAttempt.query.filter(
            TestAttempt.user_id == user_id,
            TestAttempt.level == level,
        ).order_by(TestAttempt.attempted_at.desc()).first()
        
        if not recent_attempt:
            return False
        
        # Check if it's a failed retake (not passed)
        if recent_attempt.passed:
            return False
        
        # Get test requirements to check passing score
        from ..config.test_requirements import get_test_requirements
        test_requirements = get_test_requirements(level)
        if not test_requirements:
            return False
        
        passing_score = test_requirements["passing_score"]
        
        # Failed if score < passing score
        if recent_attempt.score < passing_score:
            return True
        
        # Failed if slower than historical average
        historical_avg = TestEligibilityService.get_user_historical_average_time(user_id, level)
        if historical_avg and recent_attempt.avg_time_per_question_ms:
            if recent_attempt.avg_time_per_question_ms > historical_avg:
                return True
        
        return False

    @staticmethod
    @log_query
    def get_user_slowest_levels(user_id: int, limit: int = 5) -> list[int]:
        """Get user's slowest question levels based on average response time.
        
        Returns list of level numbers sorted by slowest average time.
        """
        from datetime import datetime, timedelta
        
        # Look at responses from last 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        # Get average time per level from responses
        from ..models import Question, db
        
        level_times = (
            db.session.query(
                Question.required_level,
                db.func.avg(Response.duration_ms).label("avg_time")
            )
            .join(Response, Question.id == Response.question_id)
            .filter(
                Response.user_id == user_id,
                Response.duration_ms.isnot(None),
                Response.answered_at >= cutoff_date,
                Question.required_level.in_(AdaptiveDistributionService.SLOWEST_QUESTIONS_LEVELS),
            )
            .group_by(Question.required_level)
            .order_by(db.func.avg(Response.duration_ms).desc())
            .limit(limit)
            .all()
        )
        
        return [level for level, _ in level_times]

    @staticmethod
    @log_query
    def generate_adaptive_question_distribution(
        user: User, target_level: int | None = None
    ) -> list[dict[str, Any]]:
        """Generate question distribution for adaptive practice session.
        
        Distribution:
        - 50% around user's level (40-50% of this = user's current level, so 20-25% of total)
        - 20% slowest questions (levels 1-37)
        - 30% completely random (up to user's level)
        
        Returns list of (level, weight) tuples where weight is the probability.
        """
        user_level = target_level if target_level is not None else user.level
        
        distribution = []
        
        # 50% around user's level
        # 40-50% of this 50% = user's current level (20-25% of total)
        # Remaining = levels around user's level
        around_level_weight = 0.50
        current_level_weight = around_level_weight * 0.45  # 22.5% of total
        nearby_levels_weight = around_level_weight * 0.55  # 27.5% of total
        
        # User's current level
        distribution.append({"level": user_level, "weight": current_level_weight})
        
        # Nearby levels (level-1, level+1 if available)
        nearby_weight_per_level = nearby_levels_weight / 2  # Split between level-1 and level+1
        if user_level > 1:
            distribution.append({"level": user_level - 1, "weight": nearby_weight_per_level})
        if user_level < 45:
            distribution.append({"level": user_level + 1, "weight": nearby_weight_per_level})
        
        # 20% slowest questions (levels 1-37)
        slowest_levels = AdaptiveDistributionService.get_user_slowest_levels(user.id, limit=5)
        if slowest_levels:
            slowest_weight_per_level = 0.20 / len(slowest_levels)
            for level in slowest_levels:
                distribution.append({"level": level, "weight": slowest_weight_per_level})
        else:
            # If no slowest levels found, distribute across levels 1-37
            slowest_weight_per_level = 0.20 / len(AdaptiveDistributionService.SLOWEST_QUESTIONS_LEVELS)
            for level in AdaptiveDistributionService.SLOWEST_QUESTIONS_LEVELS:
                distribution.append({"level": level, "weight": slowest_weight_per_level})
        
        # 30% completely random (up to user's level)
        random_levels = list(range(1, user_level + 1))
        random_weight_per_level = 0.30 / len(random_levels)
        for level in random_levels:
            distribution.append({"level": level, "weight": random_weight_per_level})
        
        # Normalize weights to sum to 1.0
        total_weight = sum(item["weight"] for item in distribution)
        if total_weight > 0:
            for item in distribution:
                item["weight"] = item["weight"] / total_weight
        
        return distribution

    @staticmethod
    @log_query
    def select_level_from_distribution(distribution: list[dict[str, Any]]) -> int:
        """Select a level from the distribution based on weights."""
        if not distribution:
            return 1  # Default to level 1
        
        # Create cumulative weights
        cumulative = 0.0
        rand = random.random()
        
        for item in distribution:
            cumulative += item["weight"]
            if rand <= cumulative:
                return item["level"]
        
        # Fallback to last level
        return distribution[-1]["level"]

    @staticmethod
    @log_query
    def get_operation_for_level(level: int) -> str:
        """Get the operation for a given level from level config."""
        level_config = LEVELS_CONFIG.get(level, {})
        return level_config.get("operation", "addition")  # Default to addition

