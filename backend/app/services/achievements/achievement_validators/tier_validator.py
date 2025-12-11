"""Tier validator for validating and cleaning up tiered achievements.

Validates tiered test achievements and removes ones that don't meet requirements.
This is primarily for legacy test achievements (b, a, s, ss, sss tiers).
"""

from __future__ import annotations

from ....models import Achievement, PracticeSession, db
from ....database import log_query, transaction


class TierValidator:
    """Validator for tiered achievements."""
    
    @staticmethod
    @log_query
    def validate_and_cleanup_tier_achievements(user_id: int) -> int:
        """Validate tiered test achievements and remove ones that don't meet requirements.
        
        This is a cleanup function to remove incorrectly awarded achievements from before
        the validation was properly implemented. Specifically handles legacy test achievements
        with the old tier system (b, a, s, ss, sss).
        
        Args:
            user_id: The user ID to validate achievements for
            
        Returns:
            Number of achievements removed
        """
        # Get all tiered test achievements for this user
        # Pattern: {test_type}-{tier} where tier is b, a, s, ss, or sss
        tier_achievements = (
            Achievement.query.filter_by(user_id=user_id, category="test")
            .filter(Achievement.code.like("%-b") | Achievement.code.like("%-a") | 
                   Achievement.code.like("%-s") | Achievement.code.like("%-ss") |
                   Achievement.code.like("%-sss"))
            .all()
        )
        
        removed_count = 0
        test_type_mapping = {
            "addition_1digit": "addition-1digit",
            "addition_2digit": "addition-2digit",
            "addition_3digit": "addition-3digit",
            "subtraction_1digit": "subtraction-1digit",
            "subtraction_2digit": "subtraction-2digit",
            "subtraction_3digit": "subtraction-3digit",
            "multiplication_2digit": "multiplication-2digit",
            "multiplication_3digit": "multiplication-3digit",
            "division_1digit": "division-1digit",
        }
        
        for achievement in tier_achievements:
            # Parse the achievement code to get test type and tier
            # Format: {frontend_test_type}-{tier}
            code_parts = achievement.code.rsplit("-", 1)
            if len(code_parts) != 2:
                continue
            
            frontend_test_type, tier_suffix = code_parts
            
            # Find the backend test_type that matches this frontend type
            backend_test_type = None
            for backend_type, frontend_type in test_type_mapping.items():
                if frontend_type == frontend_test_type:
                    backend_test_type = backend_type
                    break
            
            if not backend_test_type:
                continue
            
            # Find all sessions for this test type to check if any meet the requirements
            sessions = (
                PracticeSession.query.filter_by(
                    user_id=user_id,
                    is_test=True,
                    test_type=backend_test_type,
                )
                .filter(PracticeSession.completed_at.isnot(None))
                .order_by(PracticeSession.completed_at.desc())
                .all()
            )
            
            if not sessions:
                # No sessions found, remove the achievement
                with transaction():
                    db.session.delete(achievement)
                    removed_count += 1
                continue
            
            # Define tier requirements
            tier_requirements = {
                "sss": {
                    "min_accuracy": 100,
                    "question_count": 100,
                    "max_speed": 2,
                },
                "ss": {
                    "min_accuracy": 100,
                    "max_question_count": 90,
                    "max_speed": 4,
                },
                "s": {
                    "min_accuracy": 100,
                    "min_question_count": 31,
                    "max_question_count": 59,
                    "max_speed": 6,
                },
                "a": {
                    "min_accuracy": 100,
                    "max_question_count": 29,
                },
                "b": {
                    "min_question_count": 30,
                },
            }
            
            req = tier_requirements.get(tier_suffix)
            if not req:
                continue
            
            # Check if any session meets the tier requirements
            found_valid_session = False
            for session in sessions:
                total_questions = session.total_questions
                accuracy = session.accuracy
                total_duration_ms = session.total_duration_ms or 0
                avg_time_per_question = (total_duration_ms / 1000.0 / total_questions) if total_questions > 0 and total_duration_ms else None
                
                meets_requirements = True
                
                # Check accuracy
                if "min_accuracy" in req and accuracy < req["min_accuracy"]:
                    meets_requirements = False
                
                # Check question counts
                if "min_question_count" in req and total_questions < req["min_question_count"]:
                    meets_requirements = False
                if "max_question_count" in req and total_questions > req["max_question_count"]:
                    meets_requirements = False
                if "question_count" in req and total_questions != req["question_count"]:
                    meets_requirements = False
                
                # Check speed
                if "max_speed" in req:
                    if avg_time_per_question is None:
                        meets_requirements = False
                    elif avg_time_per_question >= req["max_speed"]:
                        meets_requirements = False
                
                if meets_requirements:
                    found_valid_session = True
                    break
            
            # If no session meets the requirements, remove the achievement
            if not found_valid_session:
                with transaction():
                    db.session.delete(achievement)
                    removed_count += 1
        
        if removed_count > 0:
            db.session.commit()
        
        return removed_count


