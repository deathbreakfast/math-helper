"""Consecutive correct achievement checker.

Awards achievements for getting 30 consecutive correct answers for specific test types.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from ....models import Achievement, Question, Response, User, db
from ....services.session_engine_service import SessionEngineService
from ....database import transaction
from .base_checker import AchievementChecker


class ConsecutiveChecker(AchievementChecker):
    """Checker for consecutive correct achievements (test type mastery)."""
    
    def __init__(self, achievement_configs: dict[str, Any]):
        """Initialize checker with achievement configs.
        
        Args:
            achievement_configs: Dictionary of achievement configurations
        """
        self.achievement_configs = achievement_configs
    
    def check(
        self,
        user: User,
        metrics: dict[str, Any] | None = None,
        session_id: int | None = None,
        test_type: str | None = None
    ) -> list[Achievement]:
        """Check and award consecutive correct achievements.
        
        Args:
            user: The user to check achievements for
            metrics: Optional pre-computed user metrics (not used)
            session_id: Optional session ID to link achievements
            test_type: Optional test type to check (e.g., "multiplication-by-1")
        
        Returns:
            List of newly created Achievement objects
        """
        new_achievements = []
        
        # If test_type is provided, check only that type
        test_types_to_check = [test_type] if test_type else []
        
        for check_test_type in test_types_to_check:
            if not check_test_type:
                continue
            
            achievement_code = f"{check_test_type}_mastery"
            
            # Check if already earned
            existing = Achievement.query.filter_by(user_id=user.id, code=achievement_code).first()
            if existing:
                continue
            
            # Get test type configuration to determine level and operation
            operation = None
            required_level = None
            
            if check_test_type in SessionEngineService.TEST_TYPES:
                operation, required_level, _, _ = SessionEngineService.TEST_TYPES[check_test_type]
            else:
                # Unknown test type, skip
                continue
            
            # First, check if user has ANY responses for this test type (level + operation)
            # If they've never done questions for this type, skip it
            has_attempted = (
                Response.query.filter_by(user_id=user.id)
                .join(Question)
                .filter(
                    Question.required_level == required_level,
                    Question.operation == operation
                )
                .first()
            )
            
            if not has_attempted:
                # User has never attempted this test type, skip
                continue
            
            # Get recent responses for this specific test type (level + operation)
            # ordered by answered_at descending
            recent_responses = (
                Response.query.filter_by(user_id=user.id, is_correct=True)
                .join(Question)
                .filter(
                    Question.required_level == required_level,
                    Question.operation == operation
                )
                .order_by(Response.answered_at.desc())
                .limit(30)
                .all()
            )
            
            # Check if we have at least 30 consecutive correct answers for this test type
            if len(recent_responses) >= 30:
                # Verify they are consecutive (no gaps/incorrect answers in between)
                # Get the 30 most recent responses for this test type (including incorrect ones)
                all_recent = (
                    Response.query.filter_by(user_id=user.id)
                    .join(Question)
                    .filter(
                        Question.required_level == required_level,
                        Question.operation == operation
                    )
                    .order_by(Response.answered_at.desc())
                    .limit(30)
                    .all()
                )
                
                # Check if all 30 most recent for this test type are correct
                all_correct = all(r.is_correct for r in all_recent) if all_recent else False
                
                if len(all_recent) == 30 and all_correct:
                    # Award achievement
                    with transaction():
                        achievement = Achievement(
                            user=user,
                            code=achievement_code,
                            title=f"{check_test_type.replace('_', ' ').title()} Mastery",
                            description="Answered 30 questions correctly in a row.",
                            icon="🏆",
                            category="mastery",
                            earned_at=datetime.utcnow(),
                        )
                        db.session.add(achievement)
                        new_achievements.append(achievement)
        
        if new_achievements:
            db.session.commit()
        
        return new_achievements




