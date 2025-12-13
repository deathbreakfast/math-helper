"""Champion validator for checking and awarding Champion tier achievements.

Champion tier achievements are awarded when a user sets a new server record
for a specific achievement type. This validator checks if a session qualifies
for Champion tier and awards it if eligible.
"""

from __future__ import annotations

from ....models import PracticeSession
from ....database import log_query


class ChampionValidator:
    """Validator for Champion tier achievements."""
    
    @staticmethod
    @log_query
    def check_eligibility(
        achievement_code: str, 
        session: PracticeSession, 
        tier: str
    ) -> bool:
        """Check if a session qualifies for Champion tier and award if eligible.
        
        Args:
            achievement_code: Achievement code (e.g., "addition-basics-champion")
            session: PracticeSession that achieved the requirements
            tier: Tier name (should be "champion")
            
        Returns:
            True if Champion tier was awarded, False otherwise
        """
        from ....services.server_record_service import ServerRecordService
        
        if tier.lower() != "champion":
            return False
        
        # Check if this achievement can have Champion tier
        if not ServerRecordService.canAchievementHaveChampionTier(achievement_code):
            return False
        
        # Determine record type and value
        record_type = ServerRecordService._determine_record_type(achievement_code)
        if not record_type:
            return False
        
        record_value = ServerRecordService._determine_record_value(session, record_type)
        if record_value is None:
            return False
        
        # Check and update record
        record_set = ServerRecordService.checkAndUpdateRecord(
            achievement_type=achievement_code,
            record_type=record_type,
            value=record_value,
            user_id=session.user_id,
            session_id=session.id,
        )
        
        return record_set





