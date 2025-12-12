"""Operation statistics builder for analytics."""

from __future__ import annotations

from typing import Any


class OperationStatsBuilder:
    """Builder for operation-specific statistics."""
    
    @staticmethod
    def build(rows: list[Any]) -> dict[str, Any]:
        """Build operation-specific statistics from query rows.
        
        Args:
            rows: Query result rows with operation, attempts, correct, avg_duration_ms
            
        Returns:
            Dictionary with operation statistics (accuracy and speed per operation)
        """
        stats = {
            "additionAccuracy": 0,
            "subtractionAccuracy": 0,
            "multiplicationAccuracy": 0,
            "divisionAccuracy": 0,
            "additionSpeed": 0.0,
            "subtractionSpeed": 0.0,
            "multiplicationSpeed": 0.0,
            "divisionSpeed": 0.0,
        }

        key_map = {
            "addition": ("additionAccuracy", "additionSpeed"),
            "subtraction": ("subtractionAccuracy", "subtractionSpeed"),
            "multiplication": ("multiplicationAccuracy", "multiplicationSpeed"),
            "division": ("divisionAccuracy", "divisionSpeed"),
        }

        for row in rows:
            operation = (row.operation or "").lower()
            mapping = key_map.get(operation)
            if not mapping or row.attempts == 0:
                continue

            accuracy_key, speed_key = mapping
            correct = row.correct or 0
            stats[accuracy_key] = round((correct / row.attempts) * 100)
            stats[speed_key] = OperationStatsBuilder._format_speed(row.avg_duration_ms)

        return stats
    
    @staticmethod
    def _format_speed(duration_ms: float | None) -> float:
        """Format duration in milliseconds to seconds."""
        if duration_ms is None:
            return 0.0
        return round(duration_ms / 1000, 1)
