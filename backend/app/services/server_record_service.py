"""Service for managing server records for Champion tier achievements."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from ..database import log_query, transaction
from ..models import PracticeSession, ServerRecord, db


class ServerRecordService:
    """Service for server record tracking and Champion tier qualification."""

    # Achievement types that can qualify for Champion tier
    CHAMPION_QUALIFYING_TYPES = {
        # Speed-based achievements
        "speed": [
            "{operation}-basics-champion",
            "{test-type}-champion",
            "speed-demon-*",
            "fast-session-*",
            "fast-question-*",
        ],
        # Accuracy-based achievements
        "accuracy": [
            "{operation}-basics-champion",
        ],
        # Volume-based achievements
        "volume": [
            "question-master-*",
        ],
        # Streak-based achievements
        "streak": [
            "week-warrior-*",
            "perfect-streak-*",
        ],
    }

    @staticmethod
    @log_query
    def getCurrentRecord(achievement_type: str) -> ServerRecord | None:
        """Get current server record for an achievement type.
        
        Args:
            achievement_type: The achievement type code (e.g., "addition-basics-champion")
            
        Returns:
            ServerRecord object if found, None otherwise
        """
        return ServerRecord.query.filter_by(achievement_type=achievement_type).first()

    @staticmethod
    @log_query
    def isChampionEligible(
        achievement_type: str, record_type: str, value: float
    ) -> bool:
        """Check if a value qualifies for Champion tier (beats current record, first place only, no ties).
        
        Args:
            achievement_type: The achievement type code
            record_type: Type of record ('speed', 'accuracy', 'volume', 'streak')
            value: The value to check
            
        Returns:
            True if value beats current record (or no record exists) and is strictly better (no ties)
        """
        current_record = ServerRecordService.getCurrentRecord(achievement_type)
        
        if current_record is None:
            # No existing record, qualifies
            return True
        
        # Check if value beats current record based on record type
        # For speed: lower is better
        # For accuracy, volume, streak: higher is better
        if record_type == "speed":
            # Must be strictly lower (no ties)
            return value < current_record.record_value
        else:
            # Must be strictly higher (no ties)
            return value > current_record.record_value

    @staticmethod
    @log_query
    def checkAndUpdateRecord(
        achievement_type: str,
        record_type: str,
        value: float,
        user_id: int,
        session_id: int | None = None,
    ) -> bool:
        """Check if value qualifies for Champion tier and update record if so.
        
        Args:
            achievement_type: The achievement type code
            record_type: Type of record ('speed', 'accuracy', 'volume', 'streak')
            value: The value to check
            user_id: ID of user who achieved this value
            session_id: Optional session ID where this was achieved
            
        Returns:
            True if record was set/updated, False otherwise
        """
        if not ServerRecordService.isChampionEligible(achievement_type, record_type, value):
            return False
        
        # Get or create record
        current_record = ServerRecordService.getCurrentRecord(achievement_type)
        
        with transaction():
            if current_record:
                # Update existing record
                current_record.record_type = record_type
                current_record.record_value = value
                current_record.user_id = user_id
                current_record.achieved_at = datetime.utcnow()
                current_record.session_id = session_id
                db.session.add(current_record)
            else:
                # Create new record
                new_record = ServerRecord(
                    achievement_type=achievement_type,
                    record_type=record_type,
                    record_value=value,
                    user_id=user_id,
                    achieved_at=datetime.utcnow(),
                    session_id=session_id,
                )
                db.session.add(new_record)
        
        return True

    @staticmethod
    def getChampionQualifyingTypes() -> list[str]:
        """Get list of achievement type patterns that can qualify for Champion tier.
        
        Returns:
            List of achievement type patterns that can have Champion tier
        """
        qualifying_types = []
        for record_type, patterns in ServerRecordService.CHAMPION_QUALIFYING_TYPES.items():
            qualifying_types.extend(patterns)
        return qualifying_types

    @staticmethod
    def _determine_record_type(achievement_code: str) -> str | None:
        """Extract record type from achievement code.
        
        Args:
            achievement_code: Achievement code (e.g., "addition-basics-champion", "speed-demon-champion")
            
        Returns:
            Record type ('speed', 'accuracy', 'volume', 'streak') or None if not determinable
        """
        code_lower = achievement_code.lower()
        
        if "speed" in code_lower or "fast" in code_lower:
            return "speed"
        elif "accuracy" in code_lower or "-basics-" in code_lower:
            return "accuracy"
        elif "question-master" in code_lower or "volume" in code_lower:
            return "volume"
        elif "streak" in code_lower or "warrior" in code_lower:
            return "streak"
        
        return None

    @staticmethod
    def _determine_record_value(
        session: PracticeSession, record_type: str
    ) -> float | None:
        """Calculate record value from session based on record type.
        
        Args:
            session: PracticeSession object
            record_type: Type of record ('speed', 'accuracy', 'volume', 'streak')
            
        Returns:
            Record value as float, or None if cannot be determined
        """
        if record_type == "speed":
            # Average time per question in seconds (lower is better)
            if session.total_questions > 0 and session.total_duration_ms:
                return (session.total_duration_ms / 1000.0) / session.total_questions
            return None
        elif record_type == "accuracy":
            # Accuracy percentage (higher is better)
            return float(session.accuracy) if session.accuracy else None
        elif record_type == "volume":
            # Total questions answered (higher is better)
            return float(session.total_questions) if session.total_questions else None
        elif record_type == "streak":
            # Streak value - this would need to be calculated from user stats
            # For now, return None as streaks are tracked differently
            return None
        
        return None

    @staticmethod
    def canAchievementHaveChampionTier(achievement_code: str) -> bool:
        """Check if an achievement type can have Champion tier.
        
        Args:
            achievement_code: Achievement code to check
            
        Returns:
            True if achievement can have Champion tier, False otherwise
        """
        # Milestones like "first-steps", "first-victory" cannot have Champion
        non_qualifying = ["first-steps", "first-victory"]
        if any(nq in achievement_code.lower() for nq in non_qualifying):
            return False
        
        # Check if it matches any qualifying patterns
        code_lower = achievement_code.lower()
        
        # Speed-based
        if "speed" in code_lower or "fast" in code_lower:
            return True
        
        # Accuracy-based (basics achievements)
        if "-basics-" in code_lower and "champion" in code_lower:
            return True
        
        # Operation-based achievements with champion tier (legacy pattern, no longer used for tests)
        if "-champion" in code_lower and ("addition-" in code_lower or 
                                          "subtraction-" in code_lower or
                                          "multiplication-" in code_lower or
                                          "division-" in code_lower):
            return True
        
        # Volume-based
        if "question-master" in code_lower:
            return True
        
        # Streak-based
        if "streak" in code_lower or "warrior" in code_lower:
            return True
        
        return False

