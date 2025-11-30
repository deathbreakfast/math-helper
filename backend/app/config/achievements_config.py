"""Achievement definitions with requirements.

DEPRECATED: This file is maintained for backward compatibility.
New code should import from app.config.achievements instead.
"""

import warnings
from typing import Any

# Import from new structure
from .achievements import ACHIEVEMENTS_CONFIG as _ACHIEVEMENTS_CONFIG

# Re-export for backward compatibility
ACHIEVEMENTS_CONFIG: dict[str, dict[str, Any]] = _ACHIEVEMENTS_CONFIG

# Issue deprecation warning
warnings.warn(
    "Importing from achievements_config is deprecated. Use app.config.achievements instead.",
    DeprecationWarning,
    stacklevel=2
)
