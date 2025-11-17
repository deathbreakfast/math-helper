"""Achievement service for rules engine and achievement assignment."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import func

from ..database import log_query, transaction
from ..models import Achievement, PracticeSession, Question, Response, User, db
from ..services.level_config_service import LevelConfigService
from .analytics_service import AnalyticsService


class AchievementService:
    """Service for achievement-related operations."""

    @staticmethod
    @log_query
    def ensure_achievements(user: User, metrics: dict[str, Any] | None = None) -> list[Achievement]:
        """Ensure required achievements exist for a user based on their metrics.

        Returns:
            List of all achievements for the user
        """
        if metrics is None:
            metrics = AnalyticsService.compute_user_metrics(user.id)

        total_answers = metrics.get("questions_answered", 0)
        avg_speed = metrics.get("average_speed_seconds", 0.0)
        stats = metrics.get("operation_stats", {})
        earned_at = metrics.get("last_activity_at") or user.created_at or datetime.utcnow()

        accuracy_candidates = [
            stats.get("additionAccuracy", 0),
            stats.get("subtractionAccuracy", 0),
            stats.get("multiplicationAccuracy", 0),
            stats.get("divisionAccuracy", 0),
        ]
        max_accuracy = max(accuracy_candidates) if accuracy_candidates else 0

        rules = [
            (
                "century",
                total_answers >= 100,
                "Century Club",
                "Answered 100+ questions.",
                "💯",
                "milestone",
            ),
            (
                "speed-demon",
                avg_speed > 0 and avg_speed <= 3 and total_answers >= 10,
                "Speed Demon",
                "Average response time under 3 seconds.",
                "⚡",
                "speed",
            ),
            (
                "perfect-week",
                stats.get("currentStreak", 0) >= 7,
                "Perfect Week",
                "Practiced every day this week.",
                "🌟",
                "consistency",
            ),
            (
                "accuracy-ace",
                max_accuracy >= 95,
                "Accuracy Ace",
                "Maintained 95%+ accuracy in at least one operation.",
                "🎯",
                "accuracy",
            ),
        ]

        created = False
        for code, condition, title, description, icon, category in rules:
            if not condition:
                continue

            exists = Achievement.query.filter_by(user_id=user.id, code=code).first()
            if exists:
                continue

            with transaction():
                db.session.add(
                    Achievement(
                        user=user,
                        code=code,
                        title=title,
                        description=description,
                        icon=icon,
                        category=category,
                        earned_at=earned_at,
                    )
                )
                created = True

        if created:
            db.session.commit()

        # Check level-specific achievements
        level_achievements = AchievementService.check_level_specific_achievements(user)
        if level_achievements:
            db.session.commit()

        achievements = (
            Achievement.query.filter_by(user_id=user.id)
            .order_by(Achievement.earned_at.desc())
            .all()
        )
        return achievements

    @staticmethod
    @log_query
    def get_user_achievements(user_id: int, limit: int | None = None) -> list[Achievement]:
        """Get all achievements for a user."""
        query = Achievement.query.filter_by(user_id=user_id).order_by(Achievement.earned_at.desc())

        if limit:
            query = query.limit(limit)

        return query.all()

    @staticmethod
    @log_query
    def get_achievements_by_category(
        user_id: int | None = None, category: str | None = None, limit: int = 50
    ) -> list[Achievement]:
        """Get achievements filtered by user and/or category."""
        query = Achievement.query

        if user_id:
            query = query.filter_by(user_id=user_id)

        if category:
            query = query.filter_by(category=category)

        return query.order_by(Achievement.earned_at.desc()).limit(limit).all()

    @staticmethod
    @log_query
    def create_achievement(
        user_id: int,
        code: str,
        title: str,
        description: str,
        icon: str,
        category: str,
        earned_at: datetime | None = None,
    ) -> Achievement:
        """Manually create an achievement for a user."""
        if earned_at is None:
            earned_at = datetime.utcnow()

        # Check if already exists
        existing = Achievement.query.filter_by(user_id=user_id, code=code).first()
        if existing:
            return existing

        with transaction():
            achievement = Achievement(
                user_id=user_id,
                code=code,
                title=title,
                description=description,
                icon=icon,
                category=category,
                earned_at=earned_at,
            )
            db.session.add(achievement)
            db.session.flush()

        return achievement

    @staticmethod
    @log_query
    def get_achievement_codes(user_id: int) -> set[str]:
        """Get set of achievement codes earned by a user."""
        achievements = Achievement.query.filter_by(user_id=user_id).all()
        return {a.code for a in achievements}

    @staticmethod
    def serialize_achievement(achievement: Achievement) -> dict[str, Any]:
        """Serialize an achievement to a dictionary."""
        return {
            "id": str(achievement.id),
            "userId": achievement.user_id,
            "title": achievement.title,
            "description": achievement.description,
            "icon": achievement.icon,
            "category": achievement.category,
            "earnedAt": achievement.earned_at.isoformat(),
        }

    @staticmethod
    @log_query
    def check_consecutive_correct_achievements(user: User, test_type: str | None = None) -> list[Achievement]:
        """Check and award '30 correct in a row' achievements for test types.
        
        This checks the user's recent responses to see if they have 30 consecutive
        correct answers for a specific test type, and awards the mastery achievement.
        
        Args:
            user: The user to check
            test_type: Optional test type to check (e.g., "multiplication_1")
        
        Returns:
            List of newly created achievements
        """
        from ..models import Response, Question
        
        new_achievements = []
        
        # If test_type is provided, check only that type
        test_types_to_check = [test_type] if test_type else [
            "multiplication_1", "multiplication_2", "multiplication_3", "multiplication_4",
            "multiplication_5", "multiplication_6", "multiplication_7", "multiplication_8",
            "multiplication_9", "multiplication_10", "multiplication_11", "multiplication_12",
            "division_2digit", "division_3digit", "division_fraction", "division_decimal",
        ]
        
        for check_test_type in test_types_to_check:
            if not check_test_type:
                continue
                
            achievement_code = f"{check_test_type}_mastery"
            
            # Check if already earned
            existing = Achievement.query.filter_by(user_id=user.id, code=achievement_code).first()
            if existing:
                continue
            
            # Get recent responses for this user, ordered by answered_at descending
            recent_responses = (
                Response.query.filter_by(user_id=user.id, is_correct=True)
                .join(Question)
                .order_by(Response.answered_at.desc())
                .limit(30)
                .all()
            )
            
            # Check if we have at least 30 consecutive correct answers
            if len(recent_responses) >= 30:
                # Verify they are consecutive (no gaps/incorrect answers in between)
                # Get the 30 most recent responses (including incorrect ones)
                all_recent = (
                    Response.query.filter_by(user_id=user.id)
                    .order_by(Response.answered_at.desc())
                    .limit(30)
                    .all()
                )
                
                # Check if all 30 most recent are correct
                if len(all_recent) == 30 and all(r.is_correct for r in all_recent):
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

    @staticmethod
    @log_query
    def check_level_specific_achievements(user: User) -> list[Achievement]:
        """Check and award level-specific achievements based on configuration.
        
        Returns:
            List of newly created achievements
        """
        new_achievements = []
        user_achievement_codes = AchievementService.get_achievement_codes(user.id)
        
        # Get all achievement configs
        achievement_configs = LevelConfigService.get_all_achievement_configs()
        
        for achievement_code, config in achievement_configs.items():
            # Skip if already earned
            if achievement_code in user_achievement_codes:
                continue
            
            requirements = config.get("requirements", {})
            req_type = requirements.get("type")
            
            # Check operation_count achievements
            if req_type == "operation_count":
                operation = requirements.get("operation")
                count = requirements.get("count", 0)
                level = requirements.get("level")
                
                # Count correct answers for this operation at this level
                correct_count = (
                    db.session.query(func.count())
                    .select_from(Response)
                    .join(Question)
                    .filter(
                        Response.user_id == user.id,
                        Response.is_correct == True,
                        Question.operation == operation,
                        Question.required_level == level,
                    )
                    .scalar()
                    or 0
                )
                
                if correct_count >= count:
                    achievement = AchievementService.create_achievement(
                        user_id=user.id,
                        code=achievement_code,
                        title=config["title"],
                        description=config["description"],
                        icon=config["icon"],
                        category=config["category"],
                    )
                    new_achievements.append(achievement)
            
            # Check level_accuracy achievements
            elif req_type == "level_accuracy":
                level = requirements.get("level")
                min_accuracy = requirements.get("min_accuracy", 0.0)
                min_questions = requirements.get("min_questions", 0)
                
                # Get all responses for this level
                responses = (
                    db.session.query(Response)
                    .join(Question)
                    .filter(
                        Response.user_id == user.id,
                        Question.required_level == level,
                    )
                    .all()
                )
                
                if len(responses) >= min_questions:
                    correct_count = sum(1 for r in responses if r.is_correct)
                    accuracy = correct_count / len(responses) if responses else 0.0
                    
                    if accuracy >= min_accuracy:
                        achievement = AchievementService.create_achievement(
                            user_id=user.id,
                            code=achievement_code,
                            title=config["title"],
                            description=config["description"],
                            icon=config["icon"],
                            category=config["category"],
                        )
                        new_achievements.append(achievement)
            
            # Check level_correct_count achievements
            elif req_type == "level_correct_count":
                level = requirements.get("level")
                min_correct = requirements.get("min_correct", 0)
                
                # Count correct answers for this level
                correct_count = (
                    db.session.query(func.count())
                    .select_from(Response)
                    .join(Question)
                    .filter(
                        Response.user_id == user.id,
                        Response.is_correct == True,
                        Question.required_level == level,
                    )
                    .scalar()
                    or 0
                )
                
                if correct_count >= min_correct:
                    achievement = AchievementService.create_achievement(
                        user_id=user.id,
                        code=achievement_code,
                        title=config["title"],
                        description=config["description"],
                        icon=config["icon"],
                        category=config["category"],
                    )
                    new_achievements.append(achievement)
            
            # Check test_completion achievements
            elif req_type == "test_completion":
                test_type = requirements.get("test_type")
                min_accuracy = requirements.get("min_accuracy", 0.0)
                question_count = requirements.get("question_count", 0)
                
                # Find completed test sessions for this test type
                sessions = (
                    PracticeSession.query.filter_by(
                        user_id=user.id,
                        is_test=True,
                        test_type=test_type,
                    )
                    .filter(PracticeSession.completed_at.isnot(None))
                    .all()
                )
                
                for session in sessions:
                    if session.total_questions >= question_count:
                        accuracy = session.accuracy / 100.0 if session.accuracy else 0.0
                        if accuracy >= min_accuracy:
                            achievement = AchievementService.create_achievement(
                                user_id=user.id,
                                code=achievement_code,
                                title=config["title"],
                                description=config["description"],
                                icon=config["icon"],
                                category=config["category"],
                            )
                            new_achievements.append(achievement)
                            break  # Only award once
        
        if new_achievements:
            db.session.commit()
        
        return new_achievements

