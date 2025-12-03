"""Speed achievement definitions - now handled by milestone achievements."""

from typing import Any

# This file is kept for backward compatibility but achievements are now in milestone.py
# Old speed achievements (speed-demon, fast-session-*, fast-question-*) have been replaced with
# speed-demon-{tier} achievements in milestone.py

SPEED_ACHIEVEMENTS: dict[str, dict[str, Any]] = {}
