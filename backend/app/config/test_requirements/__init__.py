"""Test requirements aggregated from all math types."""

from typing import Any

from .addition import ADDITION_TEST_REQUIREMENTS
from .division import DIVISION_TEST_REQUIREMENTS
from .multiplication import MULTIPLICATION_TEST_REQUIREMENTS
from .subtraction import SUBTRACTION_TEST_REQUIREMENTS

# Combine all test requirements
TEST_REQUIREMENTS: dict[int, dict[str, Any]] = {
    **ADDITION_TEST_REQUIREMENTS,
    **SUBTRACTION_TEST_REQUIREMENTS,
    **MULTIPLICATION_TEST_REQUIREMENTS,
    **DIVISION_TEST_REQUIREMENTS,
}


def get_test_requirements(level: int) -> dict[str, Any] | None:
    """Get test requirements for a specific level."""
    return TEST_REQUIREMENTS.get(level)


def get_all_test_requirements() -> dict[int, dict[str, Any]]:
    """Get test requirements for all levels."""
    return TEST_REQUIREMENTS.copy()

