"""Achievement orchestrator for coordinating achievement checking.

This module handles the orchestration of achievement checking, coordinating
between different checkers and managing the overall achievement flow.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from ...database import flush_or_commit
from ...models import Achievement, PracticeSession, Question, Response, User, db
from ...services.analytics_service import AnalyticsService
from ...utils.tier_utils import ALL_TIERS
from .achievement_utils import debug_print
from .achievement_checkers import (
    MilestoneChecker,
    LevelAchievementChecker,
    LevelMasterChecker,
    MathGrandmasterChecker,
    HumanCalculatorChecker,
    MasterOfBasicChecker,
)


class AchievementOrchestrator:
    """Orchestrator for achievement checking operations."""
    
    def __init__(self, achievement_configs: dict[str, Any]):
        """Initialize the orchestrator with achievement configs.
        
        Args:
            achievement_configs: Dictionary of achievement configurations
        """
        self.achievement_configs = achievement_configs
        self.milestone_checker = MilestoneChecker(achievement_configs)
        self.level_checker = LevelAchievementChecker(achievement_configs)
        self.level_master_checker = LevelMasterChecker(achievement_configs)
        self.math_grandmaster_checker = MathGrandmasterChecker(achievement_configs)
        self.human_calculator_checker = HumanCalculatorChecker(achievement_configs)
        self.master_of_basic_checker = MasterOfBasicChecker(achievement_configs)
    
    def ensure_achievements(
        self,
        user: User,
        metrics: dict[str, Any] | None = None,
        session_id: int | None = None
    ) -> list[Achievement]:
        """Ensure required achievements exist for a user based on their metrics.
        
        Optimized to skip expensive checking if user has no new activity since last check.
        
        Args:
            user: User to check achievements for
            metrics: Optional pre-computed user metrics
            session_id: Optional session ID to link achievements to a specific session
        
        Returns:
            List of all achievements for the user
        """
        # Get current achievements first to check if we can skip
        current_achievements = Achievement.query.filter_by(user_id=user.id).all()
        
        # Optimization: Skip expensive achievement checking if user has no new activity
        # Check if user has any responses at all
        last_response = (
            Response.query.filter_by(user_id=user.id)
            .order_by(Response.answered_at.desc())
            .first()
        )
        
        if last_response:
            # Get the most recent achievement timestamp
            most_recent_achievement = (
                Achievement.query.filter_by(user_id=user.id)
                .order_by(Achievement.earned_at.desc())
                .first()
            )
            
            # If user has achievements and last response is older than most recent achievement,
            # and user's updated_at hasn't changed, we can skip checking
            if most_recent_achievement:
                # Check if last response is before the most recent achievement
                # (meaning no new activity since last achievement was awarded)
                if last_response.answered_at <= most_recent_achievement.earned_at:
                    # Also check if user's updated_at hasn't changed (no level ups, etc.)
                    # This is a simple optimization - if nothing changed, skip expensive checks
                    # Note: We still return achievements, just skip the expensive checking
                    debug_print(f"[ACHIEVEMENT DEBUG] Skipping achievement check for user {user.id} - no new activity since last achievement")
                    return current_achievements
        
        if metrics is None:
            metrics = AnalyticsService.compute_user_metrics(user.id)

        # DEBUG: Print user info and metrics
        debug_print("\n" + "="*80)
        debug_print(f"[ACHIEVEMENT DEBUG] ensure_achievements called for User ID: {user.id}, Name: {user.display_name}")
        debug_print(f"[ACHIEVEMENT DEBUG] Metrics: {metrics}")
        
        current_codes = [a.code for a in current_achievements]
        debug_print(f"[ACHIEVEMENT DEBUG] Current achievements ({len(current_achievements)}): {current_codes}")
        debug_print("="*80 + "\n")

        total_answers = metrics.get("questions_answered", 0)
        avg_speed = metrics.get("average_speed_seconds", 0.0)
        stats = metrics.get("operation_stats", {})
        current_streak = stats.get("currentStreak", 0)
        earned_at = metrics.get("last_activity_at") or user.created_at or datetime.utcnow()

        accuracy_candidates = [
            stats.get("additionAccuracy", 0),
            stats.get("subtractionAccuracy", 0),
            stats.get("multiplicationAccuracy", 0),
            stats.get("divisionAccuracy", 0),
        ]
        max_accuracy = max(accuracy_candidates) if accuracy_candidates else 0

        # Check all achievements from config (including milestone, speed, streak, accuracy)
        # Use AchievementService.check_all_achievements which handles both tiered and non-tiered milestones
        from ...services.achievement_service import AchievementService
        debug_print(f"[ACHIEVEMENT DEBUG] Checking all achievements from config...")
        print(f"[ACHIEVEMENT INFO] User {user.id} metrics: {total_answers} questions, {avg_speed:.2f}s avg speed, {max_accuracy}% max accuracy, {current_streak} day streak")
        all_achievements = AchievementService.check_all_achievements(user, metrics, session_id=session_id)
        if all_achievements:
            # Extract codes and titles immediately before flush to avoid detached object issues
            all_achievement_codes = [a.code for a in all_achievements]
            all_achievement_titles = [a.title for a in all_achievements]
            debug_print(f"[ACHIEVEMENT DEBUG] Awarded {len(all_achievements)} achievement(s) from config: {all_achievement_codes}")
            print(f"[ACHIEVEMENT INFO] Awarded {len(all_achievements)} general achievement(s): {all_achievement_titles}")
            flush_or_commit()
        
        # Check level-specific achievements (operation_count, level_accuracy, level_correct_count, test_completion)
        debug_print(f"[ACHIEVEMENT DEBUG] Checking level-specific achievements...")
        level_achievements = self.level_checker.check(user, session_id=session_id)
        if level_achievements:
            # Extract codes and titles immediately before flush to avoid detached object issues
            level_achievement_codes = [a.code for a in level_achievements]
            level_achievement_titles = [a.title for a in level_achievements]
            debug_print(f"[ACHIEVEMENT DEBUG] Awarded {len(level_achievements)} level-specific achievement(s): {level_achievement_codes}")
            print(f"[ACHIEVEMENT INFO] Awarded {len(level_achievements)} level-specific achievement(s): {level_achievement_titles}")
            flush_or_commit()
        else:
            debug_print(f"[ACHIEVEMENT DEBUG] No new level-specific achievements awarded")
        
        # Check Math Master achievements (consecutive correct per concept)
        debug_print(f"[ACHIEVEMENT DEBUG] Checking Math Master achievements...")
        level_master_achievements = self.level_master_checker.check(user)
        if level_master_achievements:
            level_master_codes = [a.code for a in level_master_achievements]
            level_master_titles = [a.title for a in level_master_achievements]
            debug_print(f"[ACHIEVEMENT DEBUG] Awarded {len(level_master_achievements)} Math Master achievement(s): {level_master_codes}")
            print(f"[ACHIEVEMENT INFO] Awarded {len(level_master_achievements)} Math Master achievement(s): {level_master_titles}")
            flush_or_commit()

        # Check Master of Basic Addition/Subtraction achievements (concept coverage based on Level Master buckets)
        debug_print(f"[ACHIEVEMENT DEBUG] Checking Master of Basic achievements...")
        master_of_basic_achievements = self.master_of_basic_checker.check(user)
        if master_of_basic_achievements:
            master_of_basic_codes = [a.code for a in master_of_basic_achievements]
            master_of_basic_titles = [a.title for a in master_of_basic_achievements]
            debug_print(
                f"[ACHIEVEMENT DEBUG] Awarded {len(master_of_basic_achievements)} Master of Basic achievement(s): {master_of_basic_codes}"
            )
            print(
                f"[ACHIEVEMENT INFO] Awarded {len(master_of_basic_achievements)} Master of Basic achievement(s): {master_of_basic_titles}"
            )
            flush_or_commit()
        
        # Check Math Grandmaster milestone achievements (Math Master tier on all concepts)
        debug_print(f"[ACHIEVEMENT DEBUG] Checking Math Grandmaster achievement...")
        math_grandmaster_achievements = []
        for tier in ALL_TIERS:
            math_grandmaster_achievements.extend(self.math_grandmaster_checker.check(user, tier=tier))
        if math_grandmaster_achievements:
            math_grandmaster_codes = [a.code for a in math_grandmaster_achievements]
            math_grandmaster_titles = [a.title for a in math_grandmaster_achievements]
            debug_print(
                f"[ACHIEVEMENT DEBUG] Awarded {len(math_grandmaster_achievements)} Math Grandmaster achievement(s): {math_grandmaster_codes}"
            )
            print(
                f"[ACHIEVEMENT INFO] Awarded {len(math_grandmaster_achievements)} Math Grandmaster achievement(s): {math_grandmaster_titles}"
            )
            flush_or_commit()
        
        # Check Human Calculator milestone achievement (Lightning Fast Bronze/Silver on all concepts)
        debug_print(f"[ACHIEVEMENT DEBUG] Checking Human Calculator achievement...")
        human_calculator_bronze = self.human_calculator_checker.check(user, tier="bronze")
        human_calculator_silver = self.human_calculator_checker.check(user, tier="silver")
        human_calculator_achievements = human_calculator_bronze + human_calculator_silver
        if human_calculator_achievements:
            human_calculator_codes = [a.code for a in human_calculator_achievements]
            human_calculator_titles = [a.title for a in human_calculator_achievements]
            debug_print(f"[ACHIEVEMENT DEBUG] Awarded {len(human_calculator_achievements)} Human Calculator achievement(s): {human_calculator_codes}")
            print(f"[ACHIEVEMENT INFO] Awarded {len(human_calculator_achievements)} Human Calculator achievement(s): {human_calculator_titles}")
            flush_or_commit()

        achievements = (
            Achievement.query.filter_by(user_id=user.id)
            .order_by(Achievement.earned_at.desc())
            .all()
        )
        return achievements
    
    def ensure_achievements_with_data(
        self,
        user: User,
        metrics: dict[str, Any],
        existing_achievements: list[Achievement],
        user_responses: list[Response],
        user_sessions: list[PracticeSession]
    ) -> list[Achievement]:
        """Internal helper to ensure achievements using pre-loaded data.
        
        This is optimized for batch processing where responses and sessions
        are already loaded in memory.
        
        Args:
            user: User object
            metrics: Pre-computed metrics for the user
            existing_achievements: Pre-loaded achievements for the user
            user_responses: Pre-loaded responses for the user
            user_sessions: Pre-loaded sessions for the user
            
        Returns:
            List of all achievements for the user
        """
        # Check all achievements from config (including milestone, speed, streak, accuracy)
        # Use AchievementService.check_all_achievements which handles both tiered and non-tiered milestones
        from ...services.achievement_service import AchievementService
        all_achievements = AchievementService.check_all_achievements(user, metrics)
        if all_achievements:
            flush_or_commit()
        
        # Check level-specific achievements using pre-loaded data
        # Note: We still call the original method but it will benefit from composite indexes
        # For full optimization, we'd need to refactor check_level_specific_achievements
        # to accept pre-loaded data, but that's a larger refactoring
        level_achievements = self.level_checker.check(user)
        if level_achievements:
            flush_or_commit()

        # Refresh achievements list
        achievements = (
            Achievement.query.filter_by(user_id=user.id)
            .order_by(Achievement.earned_at.desc())
            .all()
        )
        return achievements
    
    def ensure_achievements_batch(
        self,
        users: list[User],
        all_metrics: dict[int, dict[str, Any]]
    ) -> dict[int, list[Achievement]]:
        """Ensure achievements for multiple users in batch.
        
        This batches the achievement queries but still processes each user individually
        to maintain the complex achievement checking logic.
        
        Args:
            users: List of User objects
            all_metrics: Dictionary mapping user_id to metrics dict
            
        Returns:
            Dictionary mapping user_id to list of achievements
        """
        if not users:
            return {}
        
        user_ids = [user.id for user in users]
        
        # Batch load all achievements for all users at once
        all_achievements = (
            Achievement.query
            .filter(Achievement.user_id.in_(user_ids))
            .order_by(Achievement.user_id, Achievement.earned_at.desc())
            .all()
        )
        
        # Group achievements by user_id for quick lookup
        achievements_by_user: dict[int, list[Achievement]] = {}
        for achievement in all_achievements:
            if achievement.user_id not in achievements_by_user:
                achievements_by_user[achievement.user_id] = []
            achievements_by_user[achievement.user_id].append(achievement)
        
        # Batch load responses and sessions for all users to reduce queries
        # Group responses by user_id for quick lookup
        all_responses = (
            Response.query
            .filter(Response.user_id.in_(user_ids))
            .join(Question)
            .all()
        )
        responses_by_user: dict[int, list[Response]] = {}
        for response in all_responses:
            if response.user_id not in responses_by_user:
                responses_by_user[response.user_id] = []
            responses_by_user[response.user_id].append(response)
        
        # Batch load sessions for all users
        all_sessions = (
            PracticeSession.query
            .filter(PracticeSession.user_id.in_(user_ids))
            .all()
        )
        sessions_by_user: dict[int, list[PracticeSession]] = {}
        for session in all_sessions:
            if session.user_id not in sessions_by_user:
                sessions_by_user[session.user_id] = []
            sessions_by_user[session.user_id].append(session)
        
        # Process each user to ensure achievements are up to date
        # Use batch-loaded data to reduce database queries
        result: dict[int, list[Achievement]] = {}
        for user in users:
            metrics = all_metrics.get(user.id, {})
            user_responses = responses_by_user.get(user.id, [])
            user_sessions = sessions_by_user.get(user.id, [])
            
            # Check and award new achievements using batch-loaded data
            achievements = self.ensure_achievements_with_data(
                user, metrics, achievements_by_user.get(user.id, []), user_responses, user_sessions
            )
            result[user.id] = achievements
        
        return result

