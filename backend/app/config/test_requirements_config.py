"""Declarative configuration for test requirements for all 45 levels.

DEPRECATED: This file is maintained for backward compatibility.
New code should import from app.config.test_requirements instead.
"""

import warnings
from typing import Any

# Import from new structure
from .test_requirements import (
    TEST_REQUIREMENTS as _TEST_REQUIREMENTS,
    get_all_test_requirements as _get_all_test_requirements,
    get_test_requirements as _get_test_requirements,
)

# Re-export for backward compatibility
TEST_REQUIREMENTS: dict[int, dict[str, Any]] = _TEST_REQUIREMENTS

# Issue deprecation warning
warnings.warn(
    "Importing from test_requirements_config is deprecated. Use app.config.test_requirements instead.",
    DeprecationWarning,
    stacklevel=2
)


def get_test_requirements(level: int) -> dict[str, Any] | None:
    """Get test requirements for a specific level."""
    return _get_test_requirements(level)


def get_all_test_requirements() -> dict[int, dict[str, Any]]:
    """Get test requirements for all levels."""
    return _get_all_test_requirements()
