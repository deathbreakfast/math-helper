"""Adaptive distribution service for adjusting question distribution based on test performance."""

from __future__ import annotations

import random
from typing import Any

from sqlalchemy import case

from ..config.level_progression_config import LEVEL_PROGRESSION_CONFIG
from ..config.levels_config import LEVELS_CONFIG
from ..config.tests.test_definitions import get_all_test_definitions, get_test_definition
from ..database import log_query
from ..models import Response, TestAttempt, User, db
from ..services.test_eligibility_service import TestEligibilityService
# TestService imported lazily to avoid circular import


class AdaptiveDistributionService:
    """Service for adaptive question distribution based on test performance.
    
    New category-based system:
    - Level Category (35%): 50% Type A (single-level session), 50% Type B (mixed levels)
      Type A: All questions from one level (uniformly selected from {n-2, n-1, n})
      Type B: Questions distributed across {n-2, n-1, n} with 33% each
    - Requirements Category (35%): 60% questions to earn achievements required by current level + 1,
      40% questions needed to earn achievements required by locked tests
    - Bottom Performers (20%): 50% slowest average level, 50% lowest accuracy level
    - Random (10%): All questions from a single random level (1 to user_level) per session
    
    Category is selected at session level - all questions in a session use the same category.
    """

    @staticmethod
    @log_query
    def select_category() -> str:
        """Select a category for the session.
        
        Returns:
            Category name: "level", "requirements", "bottom_performers", or "random"
        """
        rand = random.random()
        if rand < 0.35:
            return "level"
        elif rand < 0.70:  # 0.35 + 0.35
            return "requirements"
        elif rand < 0.90:  # 0.35 + 0.35 + 0.20
            return "bottom_performers"
        else:  # 0.90 - 1.0
            return "random"

    @staticmethod
    @log_query
    def generate_level_category_distribution(
        user_level: int,
        mode: str | None = None,
    ) -> list[dict[str, Any]]:
        """Generate distribution for Level category.
        
        Supports two modes (50/50 selection if mode is None):
        - Type A (mode='type_a'): Single-level session - pick one level uniformly from {n-2, n-1, n}
        - Type B (mode='type_b'): Mixed-level session - questions distributed across {n-2, n-1, n} with 33% each
        
        Args:
            user_level: The user's current level
            mode: 'type_a', 'type_b', or None for random 50/50 selection
        
        Returns:
            Distribution list with level and weight entries
        """
        # Determine which mode to use
        if mode is None:
            # 50/50 selection between Type A and Type B
            mode = 'type_a' if random.random() < 0.5 else 'type_b'
        
        if mode == 'type_a':
            # Type A: Select one level uniformly from {n-2, n-1, n}
            available_levels = []
            if user_level > 2:
                available_levels.append(user_level - 2)
            if user_level > 1:
                available_levels.append(user_level - 1)
            available_levels.append(user_level)
            
            # Pick one level uniformly
            selected_level = random.choice(available_levels)
            return [{"level": selected_level, "weight": 1.0}]
        
        elif mode == 'type_b':
            # Type B: 3-level distribution with 33% each
            distribution = []
            
            # Current level - 2
            if user_level > 2:
                distribution.append({"level": user_level - 2, "weight": 0.33})
            
            # Level - 1
            if user_level > 1:
                distribution.append({"level": user_level - 1, "weight": 0.33})
            
            # Current level
            distribution.append({"level": user_level, "weight": 0.33})
            
            # Normalize weights
            total_weight = sum(item["weight"] for item in distribution)
            if total_weight > 0:
                for item in distribution:
                    item["weight"] = item["weight"] / total_weight
            
            return distribution
        
        else:
            raise ValueError(f"Invalid mode '{mode}'. Must be 'type_a', 'type_b', or None")

    @staticmethod
    @log_query
    def get_requirements_category_levels(
        user: User,
    ) -> list[int]:
        """Get levels needed for Requirements category.
        
        Returns:
            List of levels needed to earn achievements required by:
            - 60%: Current level + 1 requirements
            - 40%: Locked test requirements
        """
        levels = []
        user_level = user.level
        
        # 60%: Questions to earn achievements required by current level + 1
        next_level = user_level + 1
        if next_level in LEVEL_PROGRESSION_CONFIG:
            requirements = LEVEL_PROGRESSION_CONFIG[next_level]
            for req in requirements:
                achievement_code = req.get("achievement_code")
                metadata_filter = req.get("metadata_filter")
                
                # Extract level from metadata if available
                if metadata_filter and "level" in metadata_filter:
                    levels.append(metadata_filter["level"])
                else:
                    # If no level specified in metadata, default to user's current level
                    # This ensures users get questions appropriate for their level
                    levels.append(user_level)
        
        # 40%: Questions needed to earn achievements required by locked tests
        all_tests = get_all_test_definitions()
        for test_def in all_tests:
            test_type = test_def.get("test_type")
            if not test_type:
                continue
            
            # Check if test is locked (lazy import to avoid circular dependency)
            from ..services.test_service import TestService
            unlock_status = TestService.check_test_unlock_requirements(user.id, test_type)
            if unlock_status.get("is_unlocked", False):
                continue  # Skip unlocked tests
            
            # Get unlock requirements
            unlock_reqs = test_def.get("unlock_requirements", {})
            if not unlock_reqs:
                continue
            
            # Extract levels from achievement requirements
            achievement_codes = unlock_reqs.get("achievement_codes", [])
            if not achievement_codes:
                achievement_code = unlock_reqs.get("achievement_code")
                if achievement_code:
                    achievement_codes = [achievement_code]
            
            metadata_filters = unlock_reqs.get("metadata_filters", {})
            for code in achievement_codes:
                metadata_filter = metadata_filters.get(code)
                if metadata_filter and "level" in metadata_filter:
                    levels.append(metadata_filter["level"])
        
        # FILTER: Only return levels that are <= user's current level
        # This prevents generating questions from levels the user hasn't unlocked yet
        # and prevents division by zero errors from invalid level configurations
        filtered_levels = [level for level in levels if level <= user_level]
        
        return list(set(filtered_levels))  # Remove duplicates

    @staticmethod
    @log_query
    def generate_requirements_category_distribution(
        user: User,
    ) -> list[dict[str, Any]]:
        """Generate distribution for Requirements category.
        
        Distribution:
        - 60%: Questions to earn achievements required by current level + 1
        - 40%: Questions needed to earn achievements required by locked tests
        """
        levels = AdaptiveDistributionService.get_requirements_category_levels(user)
        
        if not levels:
            # Fallback to level category if no requirements found
            return AdaptiveDistributionService.generate_level_category_distribution(user.level)
        
        distribution = []
        
        # Split 60/40 between next level requirements and locked test requirements
        # For simplicity, we'll distribute evenly across all requirement levels
        # The 60/40 split is conceptual - in practice, we'll weight by importance
        weight_per_level = 1.0 / len(levels)
        for level in levels:
            distribution.append({"level": level, "weight": weight_per_level})
        
        return distribution

    @staticmethod
    @log_query
    def get_user_slowest_level(user_id: int) -> int | None:
        """Get user's slowest level based on average response time."""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        from ..models import Question
        
        level_time = (
            db.session.query(
                Question.required_level,
                db.func.avg(Response.duration_ms).label("avg_time")
            )
            .join(Response, Question.id == Response.question_id)
            .filter(
                Response.user_id == user_id,
                Response.duration_ms.isnot(None),
                Response.answered_at >= cutoff_date,
            )
            .group_by(Question.required_level)
            .order_by(db.func.avg(Response.duration_ms).desc())
            .first()
        )
        
        return level_time[0] if level_time else None

    @staticmethod
    @log_query
    def get_user_lowest_accuracy_level(user_id: int) -> int | None:
        """Get user's lowest accuracy level."""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        from ..models import Question
        
        level_accuracy = (
            db.session.query(
                Question.required_level,
                db.func.avg(
                    case(
                        (Response.is_correct == True, 1),
                        else_=0
                    )
                ).label("avg_accuracy")
            )
            .join(Response, Question.id == Response.question_id)
            .filter(
                Response.user_id == user_id,
                Response.answered_at >= cutoff_date,
            )
            .group_by(Question.required_level)
            .order_by(db.func.avg(
                case(
                    (Response.is_correct == True, 1),
                    else_=0
                )
            ).asc())
            .first()
        )
        
        return level_accuracy[0] if level_accuracy else None

    @staticmethod
    @log_query
    def generate_bottom_performers_category_distribution(
        user_id: int,
    ) -> list[dict[str, Any]]:
        """Generate distribution for Bottom Performers category.
        
        Distribution:
        - 50%: Slowest average level
        - 50%: Lowest accuracy level
        """
        distribution = []
        
        slowest_level = AdaptiveDistributionService.get_user_slowest_level(user_id)
        lowest_accuracy_level = AdaptiveDistributionService.get_user_lowest_accuracy_level(user_id)
        
        if slowest_level:
            distribution.append({"level": slowest_level, "weight": 0.5})
        
        if lowest_accuracy_level:
            distribution.append({"level": lowest_accuracy_level, "weight": 0.5})
        
        # If we only have one, give it full weight
        if len(distribution) == 1:
            distribution[0]["weight"] = 1.0
        elif not distribution:
            # Fallback to level 1 if no data
            distribution.append({"level": 1, "weight": 1.0})
        
        return distribution

    @staticmethod
    @log_query
    def generate_random_category_distribution(
        user_level: int,
    ) -> list[dict[str, Any]]:
        """Generate distribution for Random category.
        
        Behavior:
        - Selects a single random level (between 1 and user_level) for the session
        - All questions in the session will be from this same level
        - Different sessions may use different random levels
        
        This provides variety across sessions while maintaining consistency within a session.
        """
        # Pick a random level for this session (all questions will use this level)
        random_level = random.randint(1, user_level)
        return [{"level": random_level, "weight": 1.0}]

    @staticmethod
    @log_query
    def generate_adaptive_question_distribution(
        user: User, target_level: int | None = None, category: str | None = None
    ) -> list[dict[str, Any]]:
        """Generate question distribution for adaptive practice session.
        
        New category-based system where category is selected at session level.
        
        Args:
            user: User object
            target_level: Optional target level (defaults to user.level)
            category: Optional category to use (if None, selects randomly)
        
        Returns:
            List of (level, weight) tuples where weight is the probability.
        """
        user_level = target_level if target_level is not None else user.level
        
        # Select category if not provided
        if category is None:
            category = AdaptiveDistributionService.select_category()
        
        # Generate distribution based on category
        if category == "level":
            # Level category uses 50/50 Type A/B selection (mode=None triggers random selection)
            distribution = AdaptiveDistributionService.generate_level_category_distribution(user_level, mode=None)
        elif category == "requirements":
            distribution = AdaptiveDistributionService.generate_requirements_category_distribution(user)
        elif category == "bottom_performers":
            distribution = AdaptiveDistributionService.generate_bottom_performers_category_distribution(user.id)
        elif category == "random":
            distribution = AdaptiveDistributionService.generate_random_category_distribution(user_level)
        else:
            # Fallback to level category
            distribution = AdaptiveDistributionService.generate_level_category_distribution(user_level)
        
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
