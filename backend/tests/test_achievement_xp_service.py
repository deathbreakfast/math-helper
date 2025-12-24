"""Tests for AchievementXPService."""

import pytest

from app.config.achievement_xp import ACHIEVEMENT_XP_TABLE
from app.services.achievement_xp_service import AchievementXPService
from app.utils.tier_utils import ALL_TIERS


class TestAchievementXPService:
    """Comprehensive tests for AchievementXPService."""
    
    # ========================================================================
    # Tests for achievements WITH multipliers
    # ========================================================================
    
    def test_reward_for_first_steps(self):
        """Test first-steps achievement returns correct bonus XP and multiplier."""
        reward = AchievementXPService.reward_for_achievement_code("first-steps")
        assert reward.bonus_xp == 50
        assert abs(reward.multiplier - 1.01) < 1e-9
        assert reward.base_code == "first-steps"
        assert reward.tier == "bronze"
    
    def test_reward_for_first_victory(self):
        """Test first-victory achievement returns correct bonus XP and multiplier."""
        reward = AchievementXPService.reward_for_achievement_code("first-victory")
        assert reward.bonus_xp == 100
        assert abs(reward.multiplier - 1.02) < 1e-9
        assert reward.base_code == "first-victory"
        assert reward.tier == "silver"
    
    def test_accuracy_ace_bronze(self):
        """Test accuracy-ace-bronze returns correct bonus XP and multiplier."""
        reward = AchievementXPService.reward_for_achievement_code("accuracy-ace-bronze")
        assert reward.bonus_xp == 10
        assert abs(reward.multiplier - 1.01) < 1e-9
    
    def test_accuracy_ace_silver(self):
        """Test accuracy-ace-silver returns correct bonus XP and multiplier."""
        reward = AchievementXPService.reward_for_achievement_code("accuracy-ace-silver")
        assert reward.bonus_xp == 25
        assert abs(reward.multiplier - 1.02) < 1e-9
    
    def test_accuracy_ace_gold(self):
        """Test accuracy-ace-gold returns correct bonus XP and multiplier."""
        reward = AchievementXPService.reward_for_achievement_code("accuracy-ace-gold")
        assert reward.bonus_xp == 50
        assert abs(reward.multiplier - 1.03) < 1e-9
    
    def test_level_master_bronze(self):
        """Test level-master-bronze returns correct bonus XP and multiplier."""
        reward = AchievementXPService.reward_for_achievement_code("level-master-bronze")
        assert reward.bonus_xp == 200
        assert abs(reward.multiplier - 1.05) < 1e-9
    
    def test_level_master_gold(self):
        """Test level-master-gold returns correct bonus XP and multiplier."""
        reward = AchievementXPService.reward_for_achievement_code("level-master-gold")
        assert reward.bonus_xp == 512
        assert abs(reward.multiplier - 1.19) < 1e-9
    
    def test_level_master_champion(self):
        """Test level-master-champion returns correct bonus XP and multiplier."""
        reward = AchievementXPService.reward_for_achievement_code("level-master-champion")
        assert reward.bonus_xp == 22000
        assert abs(reward.multiplier - 3.35) < 1e-9
    
    def test_lightning_fast_bronze(self):
        """Test lightning-fast-bronze returns correct bonus XP and multiplier."""
        reward = AchievementXPService.reward_for_achievement_code("lightning-fast-bronze")
        assert reward.bonus_xp == 200
        assert abs(reward.multiplier - 1.05) < 1e-9
    
    def test_lightning_fast_champion(self):
        """Test lightning-fast-champion returns correct bonus XP and multiplier."""
        reward = AchievementXPService.reward_for_achievement_code("lightning-fast-champion")
        assert reward.bonus_xp == 40341
        assert abs(reward.multiplier - 3.48) < 1e-9
    
    def test_question_master_bronze(self):
        """Test question-master-bronze returns correct bonus XP and multiplier."""
        reward = AchievementXPService.reward_for_achievement_code("question-master-bronze")
        assert reward.bonus_xp == 120
        assert abs(reward.multiplier - 1.10) < 1e-9
    
    def test_question_master_champion(self):
        """Test question-master-champion returns correct bonus XP and multiplier."""
        reward = AchievementXPService.reward_for_achievement_code("question-master-champion")
        assert reward.bonus_xp == 24192
        assert abs(reward.multiplier - 3.50) < 1e-9
    
    def test_speed_demon_bronze(self):
        """Test speed-demon-bronze returns correct bonus XP and multiplier."""
        reward = AchievementXPService.reward_for_achievement_code("speed-demon-bronze")
        assert reward.bonus_xp == 6
        assert abs(reward.multiplier - 1.01) < 1e-9
    
    def test_speed_demon_diamond(self):
        """Test speed-demon-diamond returns correct bonus XP and multiplier."""
        reward = AchievementXPService.reward_for_achievement_code("speed-demon-diamond")
        assert reward.bonus_xp == 50
        assert abs(reward.multiplier - 1.152) < 1e-9
    
    def test_speed_demon_champion(self):
        """Test speed-demon-champion returns correct bonus XP and multiplier."""
        reward = AchievementXPService.reward_for_achievement_code("speed-demon-champion")
        assert reward.bonus_xp == 4860
        assert abs(reward.multiplier - 1.875) < 1e-9
    
    def test_perfect_streak_bronze(self):
        """Test perfect-streak-bronze returns correct bonus XP and multiplier."""
        reward = AchievementXPService.reward_for_achievement_code("perfect-streak-bronze")
        assert reward.bonus_xp == 50
        assert abs(reward.multiplier - 1.05) < 1e-9
    
    def test_perfect_streak_champion(self):
        """Test perfect-streak-champion returns correct bonus XP and multiplier."""
        reward = AchievementXPService.reward_for_achievement_code("perfect-streak-champion")
        assert reward.bonus_xp == 17897
        assert abs(reward.multiplier - 4.15) < 1e-9
    
    def test_week_warrior_bronze(self):
        """Test week-warrior-bronze returns correct bonus XP and multiplier."""
        reward = AchievementXPService.reward_for_achievement_code("week-warrior-bronze")
        assert reward.bonus_xp == 500
        assert abs(reward.multiplier - 1.2) < 1e-9
    
    def test_week_warrior_champion(self):
        """Test week-warrior-champion returns correct bonus XP and multiplier."""
        reward = AchievementXPService.reward_for_achievement_code("week-warrior-champion")
        assert reward.bonus_xp == 512000
        assert abs(reward.multiplier - 9.95) < 1e-9
    
    # ========================================================================
    # Tests for achievements WITHOUT multipliers (bonus XP only)
    # ========================================================================
    
    def test_so_wow_bronze(self):
        """Test so-wow-bronze returns bonus XP but no multiplier."""
        reward = AchievementXPService.reward_for_achievement_code("so-wow-bronze")
        assert reward.bonus_xp == 12
        assert reward.multiplier == 0.0
    
    def test_so_wow_champion(self):
        """Test so-wow-champion returns bonus XP but no multiplier."""
        reward = AchievementXPService.reward_for_achievement_code("so-wow-champion")
        assert reward.bonus_xp == 12500
        assert reward.multiplier == 0.0
    
    def test_level_grandmaster_bronze(self):
        """Test level-grandmaster-bronze returns bonus XP but no multiplier."""
        reward = AchievementXPService.reward_for_achievement_code("level-grandmaster-bronze")
        assert reward.bonus_xp == 2200
        assert reward.multiplier == 0.0
    
    def test_level_grandmaster_champion(self):
        """Test level-grandmaster-champion returns bonus XP but no multiplier."""
        reward = AchievementXPService.reward_for_achievement_code("level-grandmaster-champion")
        assert reward.bonus_xp == 242000
        assert reward.multiplier == 0.0
    
    def test_human_calculator_bronze(self):
        """Test human-calculator-bronze returns bonus XP but no multiplier."""
        reward = AchievementXPService.reward_for_achievement_code("human-calculator-bronze")
        assert reward.bonus_xp == 2200
        assert reward.multiplier == 0.0
    
    def test_human_calculator_champion(self):
        """Test human-calculator-champion returns bonus XP but no multiplier."""
        reward = AchievementXPService.reward_for_achievement_code("human-calculator-champion")
        assert reward.bonus_xp == 443751
        assert reward.multiplier == 0.0
    
    def test_master_of_times_tables_bronze(self):
        """Test master-of-times-tables-bronze returns bonus XP but no multiplier."""
        reward = AchievementXPService.reward_for_achievement_code("master-of-times-tables-bronze")
        assert reward.bonus_xp == 4800
        assert reward.multiplier == 0.0
    
    def test_master_of_times_tables_champion(self):
        """Test master-of-times-tables-champion returns bonus XP but no multiplier."""
        reward = AchievementXPService.reward_for_achievement_code("master-of-times-tables-champion")
        assert reward.bonus_xp == 748092
        assert reward.multiplier == 0.0
    
    def test_master_of_division_tables_bronze(self):
        """Test master-of-division-tables-bronze returns bonus XP but no multiplier."""
        reward = AchievementXPService.reward_for_achievement_code("master-of-division-tables-bronze")
        assert reward.bonus_xp == 5200
        assert reward.multiplier == 0.0
    
    def test_master_of_division_tables_champion(self):
        """Test master-of-division-tables-champion returns bonus XP but no multiplier."""
        reward = AchievementXPService.reward_for_achievement_code("master-of-division-tables-champion")
        assert reward.bonus_xp == 810433
        assert reward.multiplier == 0.0
    
    def test_master_of_basic_addition_bronze(self):
        """Test master-of-basic-addition-bronze returns bonus XP but no multiplier."""
        reward = AchievementXPService.reward_for_achievement_code("master-of-basic-addition-bronze")
        assert reward.bonus_xp == 4000
        assert reward.multiplier == 0.0
    
    def test_master_of_basic_addition_champion(self):
        """Test master-of-basic-addition-champion returns bonus XP but no multiplier."""
        reward = AchievementXPService.reward_for_achievement_code("master-of-basic-addition-champion")
        assert reward.bonus_xp == 623410
        assert reward.multiplier == 0.0
    
    def test_master_of_basic_subtraction_bronze(self):
        """Test master-of-basic-subtraction-bronze returns bonus XP but no multiplier."""
        reward = AchievementXPService.reward_for_achievement_code("master-of-basic-subtraction-bronze")
        assert reward.bonus_xp == 4400
        assert reward.multiplier == 0.0
    
    def test_master_of_basic_subtraction_champion(self):
        """Test master-of-basic-subtraction-champion returns bonus XP but no multiplier."""
        reward = AchievementXPService.reward_for_achievement_code("master-of-basic-subtraction-champion")
        assert reward.bonus_xp == 685751
        assert reward.multiplier == 0.0
    
    # ========================================================================
    # Multiplier calculation tests (factor to delta conversion)
    # ========================================================================
    
    def test_multiplier_factor_to_delta_first_steps(self):
        """Test that multiplier factor (1.01) converts to delta (0.01)."""
        reward = AchievementXPService.reward_for_achievement_code("first-steps")
        factor = reward.multiplier
        delta = factor - 1.0
        assert abs(delta - 0.01) < 1e-9
    
    def test_multiplier_factor_to_delta_accuracy_ace_gold(self):
        """Test that multiplier factor (1.03) converts to delta (0.03)."""
        reward = AchievementXPService.reward_for_achievement_code("accuracy-ace-gold")
        factor = reward.multiplier
        delta = factor - 1.0
        assert abs(delta - 0.03) < 1e-9
    
    def test_multiplier_factor_to_delta_speed_demon_diamond(self):
        """Test that multiplier factor (1.152) converts to delta (0.152)."""
        reward = AchievementXPService.reward_for_achievement_code("speed-demon-diamond")
        factor = reward.multiplier
        delta = factor - 1.0
        assert abs(delta - 0.152) < 1e-9
    
    def test_multiplier_factor_to_delta_large_multiplier(self):
        """Test large multiplier factor (1.875) converts to delta (0.875)."""
        reward = AchievementXPService.reward_for_achievement_code("speed-demon-champion")
        factor = reward.multiplier
        delta = factor - 1.0
        assert abs(delta - 0.875) < 1e-9
    
    def test_total_multiplier_calculation_multiple_achievements(self):
        """Test that multiple achievements combine multipliers correctly.
        
        Example: first-steps (1.01) + accuracy-ace-gold (1.03) = 1.0 + 0.01 + 0.03 = 1.04
        NOT sum of factors (2.04)
        """
        reward1 = AchievementXPService.reward_for_achievement_code("first-steps")
        reward2 = AchievementXPService.reward_for_achievement_code("accuracy-ace-gold")
        
        delta1 = reward1.multiplier - 1.0
        delta2 = reward2.multiplier - 1.0
        total_multiplier = 1.0 + delta1 + delta2
        
        assert abs(total_multiplier - 1.04) < 1e-9
        # Verify it's NOT the sum of factors
        assert total_multiplier < 2.0
    
    def test_multiplier_none_returns_zero(self):
        """Test achievements with multiplier=None return multiplier=0.0."""
        reward = AchievementXPService.reward_for_achievement_code("so-wow-bronze")
        assert reward.multiplier == 0.0
    
    # ========================================================================
    # Edge cases and error handling
    # ========================================================================
    
    def test_reward_for_unknown_achievement_defaults_zero(self):
        """Test unknown achievement code returns zero bonus XP and multiplier."""
        reward = AchievementXPService.reward_for_achievement_code("not-a-real-achievement")
        assert reward.bonus_xp == 0
        assert reward.multiplier == 0.0
    
    def test_invalid_tier_defaults_to_index_zero(self):
        """Test achievement code with invalid tier defaults to first tier (index 0)."""
        # Try a tier that doesn't exist for accuracy-ace (which only has bronze/silver/gold)
        reward = AchievementXPService.reward_for_achievement_code("accuracy-ace-platinum")
        # Should default to bronze tier values (index 0)
        assert reward.bonus_xp == 10
        assert abs(reward.multiplier - 1.01) < 1e-9
    
    def test_single_tier_achievement(self):
        """Test single-tier achievements (first-steps, first-victory) work correctly."""
        reward = AchievementXPService.reward_for_achievement_code("first-steps")
        assert reward.tier == "bronze"
        assert reward.bonus_xp == 50
        
        reward2 = AchievementXPService.reward_for_achievement_code("first-victory")
        assert reward2.tier == "silver"
        assert reward2.bonus_xp == 100
    
    # ========================================================================
    # Parametrized tests for tier progression
    # ========================================================================
    
    @pytest.mark.parametrize("tier_index,tier_name", [
        (0, "bronze"), (1, "silver"), (2, "gold"), (3, "platinum"), (4, "diamond"),
        (5, "master"), (6, "grandmaster"), (7, "legendary"), (8, "mythic"),
        (9, "divine"), (10, "champion")
    ])
    def test_level_master_tier_progression(self, tier_index, tier_name):
        """Test level-master tier progression matches config."""
        code = f"level-master-{tier_name}"
        reward = AchievementXPService.reward_for_achievement_code(code)
        
        config = ACHIEVEMENT_XP_TABLE["level-master"]
        expected_bonus = config["bonus_xp"][tier_index]
        expected_multiplier = config["multiplier"][tier_index]
        
        assert reward.bonus_xp == expected_bonus
        assert abs(reward.multiplier - expected_multiplier) < 1e-9
    
    @pytest.mark.parametrize("tier_index,tier_name", [
        (0, "bronze"), (1, "silver"), (2, "gold")
    ])
    def test_accuracy_ace_tier_progression(self, tier_index, tier_name):
        """Test accuracy-ace tier progression matches config."""
        code = f"accuracy-ace-{tier_name}"
        reward = AchievementXPService.reward_for_achievement_code(code)
        
        config = ACHIEVEMENT_XP_TABLE["accuracy-ace"]
        expected_bonus = config["bonus_xp"][tier_index]
        expected_multiplier = config["multiplier"][tier_index]
        
        assert reward.bonus_xp == expected_bonus
        assert abs(reward.multiplier - expected_multiplier) < 1e-9
    
    @pytest.mark.parametrize("tier_index,tier_name", [
        (0, "bronze"), (1, "silver"), (2, "gold"), (3, "platinum"), (4, "diamond"),
        (5, "master"), (6, "grandmaster"), (7, "legendary"), (8, "mythic"),
        (9, "divine"), (10, "champion")
    ])
    def test_so_wow_tier_progression_bonus_only(self, tier_index, tier_name):
        """Test so-wow tier progression (bonus XP only, no multiplier)."""
        code = f"so-wow-{tier_name}"
        reward = AchievementXPService.reward_for_achievement_code(code)
        
        config = ACHIEVEMENT_XP_TABLE["so-wow"]
        expected_bonus = config["bonus_xp"][tier_index]
        
        assert reward.bonus_xp == expected_bonus
        assert reward.multiplier == 0.0  # so-wow has multiplier=None in config
    
    # ========================================================================
    # Comprehensive coverage: all base achievement types
    # ========================================================================
    
    def test_all_achievement_base_types_have_entries(self):
        """Test that all base achievement types in ACHIEVEMENT_XP_TABLE can be looked up."""
        base_types = [
            "level-master", "lightning-fast", "question-master", "speed-demon",
            "perfect-streak", "week-warrior", "so-wow", "accuracy-ace",
            "first-steps", "first-victory", "level-grandmaster", "human-calculator",
            "master-of-times-tables", "master-of-division-tables",
            "master-of-basic-addition", "master-of-basic-subtraction"
        ]
        
        for base_type in base_types:
            assert base_type in ACHIEVEMENT_XP_TABLE, f"{base_type} missing from ACHIEVEMENT_XP_TABLE"
            
            # Try to get reward for bronze tier (if it's a tiered achievement)
            if base_type not in ["first-steps", "first-victory"]:
                code = f"{base_type}-bronze"
            else:
                code = base_type
            
            reward = AchievementXPService.reward_for_achievement_code(code)
            # Should return valid reward (even if bonus_xp is 0)
            assert reward is not None
            assert reward.base_code in [base_type, code]  # May normalize to base or keep full code
