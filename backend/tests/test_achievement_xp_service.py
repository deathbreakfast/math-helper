"""Tests for AchievementXPService."""

from app.services.achievement_xp_service import AchievementXPService


def test_reward_for_tiered_achievement():
    reward = AchievementXPService.reward_for_achievement_code("speed-demon-diamond")
    assert reward.bonus_xp == 50
    assert abs(reward.multiplier - 1.16) < 1e-9


def test_reward_for_non_tiered_unique_achievement():
    reward = AchievementXPService.reward_for_achievement_code("first-steps")
    assert reward.bonus_xp == 50
    assert abs(reward.multiplier - 1.01) < 1e-9


def test_reward_for_unknown_achievement_defaults_zero():
    reward = AchievementXPService.reward_for_achievement_code("not-a-real-achievement")
    assert reward.bonus_xp == 0
    assert reward.multiplier == 0.0

