"""Session completion orchestration service.

Handles the complete workflow of finishing a practice session:
- Computing session statistics
- Persisting completion
- Aggregating analytics
- Awarding achievements
- Computing and updating XP/level
All within a single transaction boundary for atomicity.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any

from sqlalchemy import select

from ..database import transaction
from ..models import PracticeSession, Response, db
from .achievement_service import AchievementService
from .analytics_service import AnalyticsService
from .concept_xp_service import ConceptXPService
from .practice_service import PracticeService
from .user_service import UserService
from .xp_service import XPService
from .achievement_xp_service import AchievementXPService

logger = logging.getLogger(__name__)


class SessionCompletionService:
    """Service for orchestrating session completion workflow."""

    @staticmethod
    def complete_session(session_id: int, total_duration_ms: int | None = None) -> dict[str, Any]:
        """Complete a practice session with full workflow in a single transaction.
        
        This method orchestrates:
        - Computing session statistics from responses
        - Persisting session completion
        - Aggregating daily analytics
        - Awarding achievements (general + specialized)
        - Computing and updating user XP/level
        
        All operations are performed within a single transaction boundary.
        If any step fails, the entire operation is rolled back.
        
        Args:
            session_id: The practice session ID to complete
            total_duration_ms: Optional total duration in milliseconds (if not provided, calculated from responses)
            
        Returns:
            Dictionary containing:
            - session: Session details
            - achievements: List of newly awarded achievements
            - level_up: XP and leveling information
            
        Raises:
            ValueError: If session or user not found
            Exception: Any other error during completion (will be logged and re-raised)
        """
        # Load session and validate
        session = db.session.get(PracticeSession, session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Load all responses for this session
        responses = list(db.session.scalars(
            select(Response).where(Response.session_id == session_id)
        ))

        # Calculate statistics based on unique questions (not all responses)
        # Group responses by question_id and get the latest response per question
        # This handles cases where a user may have answered the same question multiple times
        latest_responses_by_question: dict[int, Response] = {}
        for response in responses:
            question_id = response.question_id
            if question_id not in latest_responses_by_question:
                latest_responses_by_question[question_id] = response
            else:
                # Keep the response with the latest answered_at timestamp
                if response.answered_at > latest_responses_by_question[question_id].answered_at:
                    latest_responses_by_question[question_id] = response
        
        # Count unique questions and correct answers
        total_questions = len(latest_responses_by_question)
        correct_count = sum(1 for r in latest_responses_by_question.values() if r.is_correct)
        
        # Calculate duration from latest responses (one per question)
        calculated_duration = sum(r.duration_ms or 0 for r in latest_responses_by_question.values() if r.duration_ms)

        # Get user
        user = UserService.get_user(session.user_id)
        if not user:
            raise ValueError(f"User {session.user_id} not found")

        # Run entire workflow in a single transaction
        with transaction():
            # 1. Persist session completion
            PracticeService.complete_session(
                session_id=session_id,
                total_questions=total_questions,
                correct_count=correct_count,
                total_duration_ms=total_duration_ms or (calculated_duration if calculated_duration > 0 else None),
            )
            
            # Refresh session to get updated fields
            db.session.refresh(session)
            
            # 2. Aggregate daily stats
            AnalyticsService.aggregate_daily_stats(user.id)
            
            # 3. Compute user metrics
            metrics = AnalyticsService.compute_user_metrics(user.id)
            
            # 4. Award achievements (general + specialized)
            # Start with general achievements
            AchievementService.ensure_achievements(user, metrics, session_id=session_id)
            
            # Check for specialized achievements
            generic_accuracy_achievements = AchievementService.check_generic_accuracy_achievements(session)
            lightning_fast_achievements = AchievementService.check_lightning_fast_achievements(user, session.id)
            accuracy_ace_achievements = AchievementService.check_accuracy_ace_achievements(session)
            level_master_achievements = AchievementService.check_level_master_achievements(user)
            
            # Flush to ensure achievements are visible for querying
            db.session.flush()
            
            # Get all achievements for this session
            new_achievements = AchievementService.get_achievements_by_session(session_id)
            
            # Check for So, Wow! achievements (must be after all other achievements)
            so_wow_achievements = AchievementService.check_so_wow_achievements(user, new_achievements, session_id=session_id)
            
            # Update new_achievements list to include So, Wow! achievements
            if so_wow_achievements:
                new_achievements.extend(so_wow_achievements)
                db.session.flush()
            
            # 5. Compute XP and update user level
            xp_per_correct = ConceptXPService.xp_per_correct(session.concept_id)
            base_xp = int(correct_count) * int(xp_per_correct)

            # Only achievements earned during this session contribute to multiplier/bonus XP
            achievement_rewards = [AchievementXPService.reward_for_achievement_code(a.code) for a in new_achievements]
            # Convert multiplier factors to deltas (e.g., 1.03 -> 0.03, 1.32 -> 0.32)
            multiplier_factors = [r.multiplier for r in achievement_rewards if r.multiplier and r.multiplier > 0]
            multiplier_deltas = [factor - 1.0 for factor in multiplier_factors]
            bonus_xp = sum(r.bonus_xp for r in achievement_rewards)

            # Calculate total multiplier as 1.0 + sum of deltas
            total_multiplier = 1.0 + sum(multiplier_deltas) if multiplier_deltas else 1.0
            multiplied_xp = float(base_xp) * float(total_multiplier)
            total_awarded_xp_raw = multiplied_xp + float(bonus_xp)
            earned_xp = int(round(total_awarded_xp_raw))
            prev_total_xp = int(getattr(user, "experience", 0) or 0)
            prev_level = int(user.level or 1)

            new_total_xp = prev_total_xp + earned_xp
            new_level = XPService.level_for_total_xp(new_total_xp)

            # Update user XP and level
            user.experience = new_total_xp
            user.level = new_level
            db.session.add(user)
            
            # Build response DTO
            level_up_result = {
                "earned_xp": earned_xp,
                "xp_breakdown": {
                    "concept_id": session.concept_id,
                    "xp_per_correct": xp_per_correct,
                    "correct_count": int(correct_count),
                    "base_xp": base_xp,
                    "multipliers": [
                        {"achievement_code": a.code, "multiplier": r.multiplier - 1.0}  # Return delta, not factor
                        for a, r in zip(new_achievements, achievement_rewards)
                        if r.multiplier and r.multiplier > 0
                    ],
                    "total_multiplier": total_multiplier,
                    "multiplied_xp": multiplied_xp,
                    "bonus_xp": bonus_xp,
                    "bonus_xp_sources": [
                        {"achievement_code": a.code, "bonus_xp": r.bonus_xp}
                        for a, r in zip(new_achievements, achievement_rewards)
                        if r.bonus_xp
                    ],
                    "total_awarded_xp_raw": total_awarded_xp_raw,
                },
                "previous_total_xp": prev_total_xp,
                "total_xp": new_total_xp,
                "previous_level": prev_level,
                "new_level": new_level,
                "leveled_up": new_level > prev_level,
                "xp_progress": XPService.progress_for_total_xp(new_total_xp),
            }
            
            # Return DTO (transaction will commit when exiting context manager)
            return {
                "session": {
                    "id": session.id,
                    "total_questions": total_questions,
                    "correct_count": correct_count,
                    "accuracy": session.accuracy,
                    "completed_at": session.completed_at.isoformat() if session.completed_at else None,
                    "mode": session.mode,
                    "level": session.level,
                    "concept_id": session.concept_id,
                },
                "achievements": [AchievementService.serialize_achievement(a) for a in new_achievements],
                "level_up": level_up_result,
            }

