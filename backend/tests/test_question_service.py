"""Comprehensive tests for QuestionService.

Tests cover all methods in QuestionService to achieve >80% coverage.
"""

import pytest
from unittest.mock import patch, MagicMock

from app.services.question_service import QuestionService


class TestQuestionService:
    """Test suite for QuestionService static methods."""

    def test_get_operation_symbol(self):
        """Test get_operation_symbol returns correct symbols."""
        assert QuestionService.get_operation_symbol("addition") == "+"
        assert QuestionService.get_operation_symbol("subtraction") == "-"
        assert QuestionService.get_operation_symbol("multiplication") == "×"
        assert QuestionService.get_operation_symbol("division") == "÷"
        assert QuestionService.get_operation_symbol("unknown") == "+"  # Default

    def test_solve_addition(self):
        """Test solve method for addition."""
        assert QuestionService.solve("addition", 5, 3) == 8
        assert QuestionService.solve("addition", 0, 0) == 0
        assert QuestionService.solve("addition", -5, 10) == 5

    def test_solve_subtraction(self):
        """Test solve method for subtraction."""
        assert QuestionService.solve("subtraction", 10, 3) == 7
        assert QuestionService.solve("subtraction", 5, 5) == 0
        assert QuestionService.solve("subtraction", 3, 10) == -7

    def test_solve_multiplication(self):
        """Test solve method for multiplication."""
        assert QuestionService.solve("multiplication", 5, 3) == 15
        assert QuestionService.solve("multiplication", 0, 10) == 0
        assert QuestionService.solve("multiplication", -5, 3) == -15

    def test_solve_division(self):
        """Test solve method for division."""
        assert QuestionService.solve("division", 10, 2) == 5
        assert QuestionService.solve("division", 15, 3) == 5
        assert QuestionService.solve("division", 7, 2) == 3  # Integer division

    def test_solve_division_by_zero(self):
        """Test solve method raises error for division by zero."""
        with pytest.raises(ValueError, match="Division by zero"):
            QuestionService.solve("division", 10, 0)

    def test_solve_unknown_operation(self):
        """Test solve method raises error for unknown operation."""
        with pytest.raises(ValueError, match="Unknown operation"):
            QuestionService.solve("unknown", 5, 3)

    def test_format_answer_non_division(self):
        """Test format_answer for non-division operations."""
        assert QuestionService.format_answer("addition", 5, 3, "integer") == "8"
        assert QuestionService.format_answer("subtraction", 10, 3, "integer") == "7"
        assert QuestionService.format_answer("multiplication", 5, 3, "integer") == "15"

    def test_format_answer_division_integer(self):
        """Test format_answer for division with integer format."""
        assert QuestionService.format_answer("division", 10, 2, "integer") == "5"
        assert QuestionService.format_answer("division", 15, 3, "integer") == "5"

    def test_format_answer_division_remainder(self):
        """Test format_answer for division with remainder format."""
        assert QuestionService.format_answer("division", 10, 3, "remainder") == "3 R 1"
        assert QuestionService.format_answer("division", 15, 3, "remainder") == "5"  # No remainder
        assert QuestionService.format_answer("division", 7, 2, "remainder") == "3 R 1"

    def test_format_answer_division_fraction(self):
        """Test format_answer for division with fraction format."""
        assert QuestionService.format_answer("division", 10, 2, "fraction") == "5/1"
        assert QuestionService.format_answer("division", 1, 2, "fraction") == "1/2"
        assert QuestionService.format_answer("division", 4, 8, "fraction") == "1/2"  # Simplified

    def test_format_answer_division_decimal(self):
        """Test format_answer for division with decimal format."""
        # Single digit divisor: 2 decimal places
        result = QuestionService.format_answer("division", 1, 2, "decimal")
        assert result == "0.5"
        
        # Double digit divisor: 4 decimal places
        result = QuestionService.format_answer("division", 1, 12, "decimal")
        assert "0.083" in result  # Should have more precision
        
        # Test trailing zero removal
        result = QuestionService.format_answer("division", 10, 2, "decimal")
        assert result == "5"

    def test_format_answer_division_by_zero(self):
        """Test format_answer returns 'undefined' for division by zero."""
        assert QuestionService.format_answer("division", 10, 0, "integer") == "undefined"

    def test_validate_constraints_exclude_zeros(self):
        """Test validate_constraints with exclude_zeros."""
        constraints = {"exclude_zeros": True}
        assert QuestionService.validate_constraints("addition", 5, 3, constraints) is True
        assert QuestionService.validate_constraints("addition", 0, 3, constraints) is False
        assert QuestionService.validate_constraints("addition", 5, 0, constraints) is False

    def test_validate_constraints_fixed_operand2(self):
        """Test validate_constraints with fixed_operand2."""
        constraints = {"fixed_operand2": 5}
        assert QuestionService.validate_constraints("addition", 3, 5, constraints) is True
        assert QuestionService.validate_constraints("addition", 3, 4, constraints) is False

    def test_validate_constraints_multiple_of(self):
        """Test validate_constraints with multiple_of."""
        constraints = {"multiple_of": 5}
        assert QuestionService.validate_constraints("addition", 10, 3, constraints) is True  # 10 is multiple of 5
        assert QuestionService.validate_constraints("addition", 7, 3, constraints) is False  # 7 is not multiple of 5

    def test_validate_constraints_no_remainder_division(self):
        """Test validate_constraints with no_remainder for division."""
        constraints = {"no_remainder": True}
        assert QuestionService.validate_constraints("division", 10, 2, constraints) is True  # 10 % 2 == 0
        assert QuestionService.validate_constraints("division", 10, 3, constraints) is False  # 10 % 3 != 0
        # Non-division operations should not check no_remainder
        assert QuestionService.validate_constraints("addition", 10, 3, constraints) is True

    def test_validate_constraints_answer_min(self):
        """Test validate_constraints with answer_min."""
        constraints = {"answer_min": 10}
        assert QuestionService.validate_constraints("addition", 5, 5, constraints) is True  # 5+5=10 >= 10
        assert QuestionService.validate_constraints("addition", 3, 3, constraints) is False  # 3+3=6 < 10

    def test_validate_constraints_multiple_constraints(self):
        """Test validate_constraints with multiple constraints."""
        constraints = {
            "exclude_zeros": True,
            "fixed_operand2": 5,
            "answer_min": 10
        }
        assert QuestionService.validate_constraints("addition", 10, 5, constraints) is True
        assert QuestionService.validate_constraints("addition", 3, 5, constraints) is False  # 3+5=8 < 10
        assert QuestionService.validate_constraints("addition", 10, 4, constraints) is False  # operand2 != 5

    @patch('app.services.question_service.LevelConfigService.get_level_config')
    def test_generate_operands_with_constraints_basic(self, mock_get_config):
        """Test generate_operands_with_constraints with basic level config."""
        mock_get_config.return_value = {
            "operand1_range": {"min": 1, "max": 10},
            "operand2_range": {"min": 1, "max": 10},
            "constraints": {}
        }
        
        with patch('random.randint') as mock_randint:
            mock_randint.side_effect = [5, 3]
            operand1, operand2 = QuestionService.generate_operands_with_constraints("addition", 1)
            assert operand1 == 5
            assert operand2 == 3

    @patch('app.services.question_service.LevelConfigService.get_level_config')
    def test_generate_operands_with_constraints_level_not_found(self, mock_get_config):
        """Test generate_operands_with_constraints raises error for invalid level."""
        mock_get_config.return_value = None
        
        with pytest.raises(ValueError, match="Level 999 configuration not found"):
            QuestionService.generate_operands_with_constraints("addition", 999)

    @patch('app.services.question_service.LevelConfigService.get_level_config')
    def test_generate_operands_with_constraints_multiplication_table(self, mock_get_config):
        """Test generate_operands_with_constraints with multiplication_table constraint."""
        mock_get_config.return_value = {
            "operand1_range": {"min": 1, "max": 10},
            "operand2_range": {"min": 1, "max": 10},
            "constraints": {}
        }
        
        test_constraints = {"multiplication_table": 5}
        with patch('random.randint') as mock_randint:
            mock_randint.return_value = 7
            operand1, operand2 = QuestionService.generate_operands_with_constraints(
                "multiplication", 1, test_constraints
            )
            assert operand2 == 5
            assert operand1 == 7

    @patch('app.services.question_service.LevelConfigService.get_level_config')
    def test_generate_operands_with_constraints_division_table(self, mock_get_config):
        """Test generate_operands_with_constraints with division_table constraint."""
        mock_get_config.return_value = {
            "operand1_range": {"min": 1, "max": 20},
            "operand2_range": {"min": 1, "max": 10},
            "constraints": {}
        }
        
        test_constraints = {"division_table": 5}
        with patch('random.randint') as mock_randint:
            mock_randint.return_value = 3  # quotient
            operand1, operand2 = QuestionService.generate_operands_with_constraints(
                "division", 1, test_constraints
            )
            assert operand2 == 5
            assert operand1 == 15  # 5 * 3

    @patch('app.services.question_service.LevelConfigService.get_level_config')
    def test_generate_operands_with_constraints_division_table_zero(self, mock_get_config):
        """Test generate_operands_with_constraints with division_table=0."""
        mock_get_config.return_value = {
            "operand1_range": {"min": 1, "max": 10},
            "operand2_range": {"min": 1, "max": 10},
            "constraints": {}
        }
        
        test_constraints = {"division_table": 0}
        with patch('random.randint') as mock_randint:
            mock_randint.return_value = 5
            operand1, operand2 = QuestionService.generate_operands_with_constraints(
                "division", 1, test_constraints
            )
            # Should use default generation (operand2=0, so fallback to operand1_range)
            assert operand1 == 5

    @patch('app.services.question_service.LevelConfigService.get_level_config')
    def test_generate_operands_with_constraints_fixed_operand2(self, mock_get_config):
        """Test generate_operands_with_constraints with fixed_operand2 in config."""
        mock_get_config.return_value = {
            "operand1_range": {"min": 1, "max": 10},
            "operand2_range": {"min": 1, "max": 10},
            "constraints": {"fixed_operand2": 5}
        }
        
        with patch('random.randint') as mock_randint:
            mock_randint.return_value = 7
            operand1, operand2 = QuestionService.generate_operands_with_constraints("addition", 1)
            assert operand2 == 5
            assert operand1 == 7

    @patch('app.services.question_service.LevelConfigService.get_level_config')
    def test_generate_operands_with_constraints_division_fixed_operand2_zero(self, mock_get_config):
        """Test generate_operands_with_constraints handles division by zero with fixed_operand2=0."""
        mock_get_config.return_value = {
            "operand1_range": {"min": 1, "max": 10},
            "operand2_range": {"min": 1, "max": 10},
            "constraints": {"fixed_operand2": 0}
        }
        
        with patch('random.randint') as mock_randint:
            mock_randint.return_value = 5
            operand1, operand2 = QuestionService.generate_operands_with_constraints("division", 1)
            # Should use operand2_range instead (min 1)
            assert operand2 >= 1
            assert operand1 == 5

    @patch('app.services.question_service.LevelConfigService.get_level_config')
    def test_generate_operands_with_constraints_division_no_remainder_fixed(self, mock_get_config):
        """Test generate_operands_with_constraints with no_remainder and fixed_operand2."""
        mock_get_config.return_value = {
            "operand1_range": {"min": 1, "max": 20},
            "operand2_range": {"min": 1, "max": 10},
            "constraints": {"fixed_operand2": 5, "no_remainder": True}
        }
        
        with patch('random.randint') as mock_randint:
            mock_randint.return_value = 3  # quotient
            operand1, operand2 = QuestionService.generate_operands_with_constraints("division", 1)
            assert operand2 == 5
            assert operand1 == 15  # 5 * 3, divisible

    @patch('app.services.question_service.LevelConfigService.get_level_config')
    def test_generate_operands_with_constraints_multiple_of(self, mock_get_config):
        """Test generate_operands_with_constraints with multiple_of constraint."""
        mock_get_config.return_value = {
            "operand1_range": {"min": 1, "max": 20},
            "operand2_range": {"min": 1, "max": 10},
            "constraints": {"fixed_operand2": 5, "multiple_of": 5}
        }
        
        with patch('random.randint') as mock_randint:
            mock_randint.return_value = 2  # multiplier
            operand1, operand2 = QuestionService.generate_operands_with_constraints("addition", 1)
            assert operand2 == 5
            assert operand1 == 10  # 5 * 2

    @patch('app.services.question_service.LevelConfigService.get_level_config')
    def test_generate_operands_with_constraints_multiple_of_zero(self, mock_get_config):
        """Test generate_operands_with_constraints with multiple_of=0."""
        mock_get_config.return_value = {
            "operand1_range": {"min": 1, "max": 10},
            "operand2_range": {"min": 1, "max": 10},
            "constraints": {"fixed_operand2": 5, "multiple_of": 0}
        }
        
        with patch('random.randint') as mock_randint:
            mock_randint.return_value = 7
            operand1, operand2 = QuestionService.generate_operands_with_constraints("addition", 1)
            # Should use default (can't generate multiple of 0)
            assert operand1 == 7
            assert operand2 == 5

    @patch('app.services.question_service.LevelConfigService.get_level_config')
    def test_generate_operands_with_constraints_regular_generation(self, mock_get_config):
        """Test generate_operands_with_constraints with regular generation and validation."""
        mock_get_config.return_value = {
            "operand1_range": {"min": 1, "max": 10},
            "operand2_range": {"min": 1, "max": 10},
            "constraints": {"exclude_zeros": True}
        }
        
        with patch('random.randint') as mock_randint:
            mock_randint.side_effect = [5, 3]  # First attempt passes validation
            operand1, operand2 = QuestionService.generate_operands_with_constraints("addition", 1)
            assert operand1 == 5
            assert operand2 == 3

    @patch('app.services.question_service.LevelConfigService.get_level_config')
    def test_generate_operands_with_constraints_division_skip_zero(self, mock_get_config):
        """Test generate_operands_with_constraints skips operand2=0 for division."""
        mock_get_config.return_value = {
            "operand1_range": {"min": 1, "max": 10},
            "operand2_range": {"min": 0, "max": 10},
            "constraints": {}
        }
        
        with patch('random.randint') as mock_randint:
            # First attempt: operand2=0 (should be skipped), second attempt: valid
            mock_randint.side_effect = [5, 0, 5, 3]
            operand1, operand2 = QuestionService.generate_operands_with_constraints("division", 1)
            assert operand2 != 0
            assert operand2 == 3

    @patch('app.services.question_service.LevelConfigService.get_level_config')
    def test_generate_operands_with_constraints_fallback(self, mock_get_config):
        """Test generate_operands_with_constraints fallback when max_attempts exceeded."""
        mock_get_config.return_value = {
            "operand1_range": {"min": 1, "max": 10},
            "operand2_range": {"min": 1, "max": 10},
            "constraints": {"exclude_zeros": True, "answer_min": 100}  # Impossible constraint
        }
        
        with patch('random.randint') as mock_randint:
            # All attempts fail validation, then fallback
            mock_randint.side_effect = [5, 3] * 101  # 100 attempts + fallback
            operand1, operand2 = QuestionService.generate_operands_with_constraints("addition", 1, max_attempts=100)
            # Should return fallback values
            assert operand1 >= 1
            assert operand2 >= 1

    def test_create_work_steps_addition(self):
        """Test create_work_steps for addition."""
        steps = QuestionService.create_work_steps("addition", 123, 456, 579)
        assert len(steps) > 0
        assert all("id" in step for step in steps)
        assert all("description" in step for step in steps)
        assert all("value" in step for step in steps)

    def test_create_work_steps_addition_with_carry(self):
        """Test create_work_steps for addition with carrying."""
        steps = QuestionService.create_work_steps("addition", 99, 1, 100)
        # Should have steps showing carry
        assert len(steps) >= 2
        # Check for carry in description
        carry_steps = [s for s in steps if "carry" in s["description"].lower()]
        assert len(carry_steps) > 0

    def test_create_work_steps_subtraction(self):
        """Test create_work_steps for subtraction."""
        steps = QuestionService.create_work_steps("subtraction", 100, 23, 77)
        assert len(steps) > 0
        assert all("id" in step for step in steps)

    def test_create_work_steps_subtraction_with_borrow(self):
        """Test create_work_steps for subtraction with borrowing."""
        steps = QuestionService.create_work_steps("subtraction", 100, 23, 77)
        # Should have steps showing borrow
        borrow_steps = [s for s in steps if "borrow" in s["description"].lower()]
        assert len(borrow_steps) > 0

    def test_create_work_steps_multiplication(self):
        """Test create_work_steps for multiplication."""
        steps = QuestionService.create_work_steps("multiplication", 12, 34, 408)
        assert len(steps) > 0
        # Should have partial products
        partial_steps = [s for s in steps if "partial" in s["description"].lower() or "Multiply" in s["description"]]
        assert len(partial_steps) > 0

    def test_create_work_steps_division(self):
        """Test create_work_steps for division."""
        steps = QuestionService.create_work_steps("division", 10, 2, 5)
        assert len(steps) > 0
        assert "Divide" in steps[0]["description"]

    def test_create_work_steps_division_with_remainder(self):
        """Test create_work_steps for division with remainder."""
        steps = QuestionService.create_work_steps("division", 10, 3, 3)
        # Should have remainder step
        remainder_steps = [s for s in steps if "remainder" in s["description"].lower()]
        assert len(remainder_steps) > 0

    def test_serialize_work_steps(self):
        """Test serialize_work_steps converts steps to JSON."""
        steps = [
            {"id": "step-1", "description": "Add 1 + 2", "value": "3"}
        ]
        result = QuestionService.serialize_work_steps(steps)
        assert isinstance(result, str)
        import json
        parsed = json.loads(result)
        assert parsed == steps

    @patch('app.services.question_service.LevelConfigService.get_level_config')
    @patch('app.services.question_service.PracticeService.create_question')
    def test_generate_question_basic(self, mock_create_question, mock_get_config):
        """Test generate_question creates a basic question."""
        mock_get_config.return_value = {
            "operation": "addition",
            "operand1_range": {"min": 1, "max": 10},
            "operand2_range": {"min": 1, "max": 10},
            "constraints": {},
            "answer_format": "integer",
            "layout_type": "vertical"
        }
        
        mock_question = MagicMock()
        mock_question.id = 123
        mock_create_question.return_value = mock_question
        
        with patch('random.randint') as mock_randint:
            mock_randint.side_effect = [5, 3]
            result = QuestionService.generate_question("addition", 1)
            
            assert "id" in result
            assert "prompt" in result
            assert "operation" in result
            assert "operand1" in result
            assert "operand2" in result
            assert "correctAnswer" in result
            assert result["operation"] == "addition"
            assert result["operand1"] == 5
            assert result["operand2"] == 3

    @patch('app.services.question_service.LevelConfigService.get_level_config')
    def test_generate_question_level_not_found(self, mock_get_config):
        """Test generate_question raises error for invalid level."""
        mock_get_config.return_value = None
        
        with pytest.raises(ValueError, match="Level 999 configuration not found"):
            QuestionService.generate_question("addition", 999)

    @patch('app.services.question_service.LevelConfigService.get_level_config')
    @patch('app.services.question_service.PracticeService.create_question')
    def test_generate_question_with_test_constraints(self, mock_create_question, mock_get_config):
        """Test generate_question with test_constraints."""
        mock_get_config.return_value = {
            "operation": "multiplication",
            "operand1_range": {"min": 1, "max": 10},
            "operand2_range": {"min": 1, "max": 10},
            "constraints": {},
            "answer_format": "integer",
            "layout_type": "vertical"
        }
        
        mock_question = MagicMock()
        mock_question.id = 123
        mock_create_question.return_value = mock_question
        
        test_constraints = {"multiplication_table": 5}
        with patch('random.randint') as mock_randint:
            mock_randint.return_value = 7
            result = QuestionService.generate_question("multiplication", 1, test_constraints)
            assert result["operand2"] == 5

    @patch('app.services.question_service.LevelConfigService.get_level_config')
    def test_create_layout_config_vertical(self, mock_get_config):
        """Test create_layout_config for vertical layout."""
        mock_get_config.return_value = {
            "layout_type": "vertical",
            "partial_products_mode": "easy"
        }
        
        config = QuestionService.create_layout_config("addition", 1, 5, 3)
        assert config["type"] == "vertical"

    @patch('app.services.question_service.LevelConfigService.get_level_config')
    def test_create_layout_config_partial_products(self, mock_get_config):
        """Test create_layout_config for partial products layout."""
        mock_get_config.return_value = {
            "layout_type": "partialProducts",
            "partial_products_mode": "easy"
        }
        
        config = QuestionService.create_layout_config("multiplication", 1, 12, 34)
        assert config["type"] == "partialProducts"
        assert config["showWork"] is True
        assert "workSteps" in config
        assert "partialProductsMode" in config

    @patch('app.services.question_service.LevelConfigService.get_level_config')
    def test_create_layout_config_long_division(self, mock_get_config):
        """Test create_layout_config for long division layout."""
        mock_get_config.return_value = {
            "layout_type": "longDivision",
            "partial_products_mode": "easy"
        }
        
        config = QuestionService.create_layout_config("division", 1, 10, 2, "remainder")
        assert config["type"] == "longDivision"
        assert "notice" in config
        assert "tip" in config
        assert "answerFormats" in config
        assert "workSteps" in config

    @patch('app.services.question_service.LevelConfigService.get_level_config')
    def test_create_layout_config_long_division_fraction(self, mock_get_config):
        """Test create_layout_config for long division with fraction format."""
        mock_get_config.return_value = {
            "layout_type": "longDivision",
            "partial_products_mode": "easy"
        }
        
        config = QuestionService.create_layout_config("division", 1, 1, 2, "fraction")
        assert config["type"] == "longDivision"
        assert "fraction" in config["answerFormats"]

    @patch('app.services.question_service.LevelConfigService.get_level_config')
    def test_create_layout_config_long_division_decimal(self, mock_get_config):
        """Test create_layout_config for long division with decimal format."""
        mock_get_config.return_value = {
            "layout_type": "longDivision",
            "partial_products_mode": "easy"
        }
        
        config = QuestionService.create_layout_config("division", 1, 1, 3, "decimal")
        assert config["type"] == "longDivision"
        assert "decimal" in config["answerFormats"]

    @patch('app.services.question_service.LevelConfigService.get_level_config')
    def test_create_layout_config_no_config(self, mock_get_config):
        """Test create_layout_config when level config is None."""
        mock_get_config.return_value = None
        
        config = QuestionService.create_layout_config("addition", 1, 5, 3)
        assert config["type"] == "vertical"  # Default

    @patch('app.services.question_service.LevelConfigService.get_level_config')
    def test_generate_operands_with_constraints_division_invalid_config(self, mock_get_config):
        """Test generate_operands_with_constraints with invalid division config (fixed_operand2=0 and range=[0,0])."""
        mock_get_config.return_value = {
            "operand1_range": {"min": 1, "max": 10},
            "operand2_range": {"min": 0, "max": 0},
            "constraints": {"fixed_operand2": 0}
        }
        
        with pytest.raises(ValueError, match="invalid division configuration"):
            QuestionService.generate_operands_with_constraints("division", 1)

    @patch('app.services.question_service.LevelConfigService.get_level_config')
    def test_generate_operands_with_constraints_division_fixed_zero_fallback(self, mock_get_config):
        """Test generate_operands_with_constraints handles division with fixed_operand2=0 and valid range."""
        mock_get_config.return_value = {
            "operand1_range": {"min": 1, "max": 10},
            "operand2_range": {"min": 1, "max": 10},
            "constraints": {"fixed_operand2": 0}
        }
        
        with patch('random.randint') as mock_randint:
            mock_randint.return_value = 5
            operand1, operand2 = QuestionService.generate_operands_with_constraints("division", 1)
            assert operand2 >= 1  # Should use range instead of 0
            assert operand1 == 5

    @patch('app.services.question_service.LevelConfigService.get_level_config')
    def test_generate_operands_with_constraints_division_no_remainder_zero_check(self, mock_get_config):
        """Test generate_operands_with_constraints division no_remainder with operand2=0 uses range fallback."""
        mock_get_config.return_value = {
            "operand1_range": {"min": 1, "max": 20},
            "operand2_range": {"min": 1, "max": 10},
            "constraints": {"fixed_operand2": 0, "no_remainder": True}
        }
        
        with patch('random.randint') as mock_randint:
            # Flow: fixed_operand2=0, so uses range -> operand2=5 (from max(1, min) to max(1, max))
            # Then for no_remainder: generates quotient (min_quotient=1//5=0->max(1,0)=1, max_quotient=20//5=4)
            # So random.randint(1, 4) -> 3, operand1 = 5 * 3 = 15
            def randint_side_effect(*args):
                if args == (max(1, 1), max(1, 10)):  # operand2 from range
                    return 5
                elif args == (1, 4):  # quotient calculation (min_quotient=1, max_quotient=4)
                    return 3
                return 1  # fallback
            
            mock_randint.side_effect = randint_side_effect
            operand1, operand2 = QuestionService.generate_operands_with_constraints("division", 1)
            # Should use range instead of 0, then generate multiple
            assert operand2 == 5
            assert operand1 == 15  # 5 * 3
            assert operand1 % operand2 == 0  # No remainder

    @patch('app.services.question_service.LevelConfigService.get_level_config')
    def test_generate_operands_with_constraints_multiple_of_invalid_range(self, mock_get_config):
        """Test generate_operands_with_constraints with multiple_of when range is invalid."""
        mock_get_config.return_value = {
            "operand1_range": {"min": 10, "max": 5},  # Invalid: min > max
            "operand2_range": {"min": 1, "max": 10},
            "constraints": {"fixed_operand2": 5, "multiple_of": 5}
        }
        
        with patch('random.randint') as mock_randint:
            mock_randint.return_value = 7
            operand1, operand2 = QuestionService.generate_operands_with_constraints("addition", 1)
            # Should use default when range is invalid
            assert operand1 == 7
            assert operand2 == 5

    @patch('app.services.question_service.LevelConfigService.get_level_config')
    def test_generate_operands_with_constraints_division_no_remainder_regular(self, mock_get_config):
        """Test generate_operands_with_constraints with division no_remainder in regular generation."""
        mock_get_config.return_value = {
            "operand1_range": {"min": 1, "max": 20},
            "operand2_range": {"min": 1, "max": 10},
            "constraints": {"no_remainder": True}
        }
        
        with patch('random.randint') as mock_randint:
            # First attempt: operand2=0 (skip), then generate valid division
            # For no_remainder, operand1 is calculated as operand2 * quotient
            # So we need: operand2, then quotient for operand1 calculation
            mock_randint.side_effect = [0, 5, 3]  # operand2=0 (skip), operand2=5, quotient=3 -> operand1=15
            operand1, operand2 = QuestionService.generate_operands_with_constraints("division", 1)
            assert operand2 == 5
            assert operand1 == 15  # 5 * 3
            assert operand1 % operand2 == 0  # No remainder

    @patch('app.services.question_service.LevelConfigService.get_level_config')
    def test_generate_operands_with_constraints_multiple_of_regular(self, mock_get_config):
        """Test generate_operands_with_constraints with multiple_of in regular generation."""
        mock_get_config.return_value = {
            "operand1_range": {"min": 1, "max": 20},
            "operand2_range": {"min": 1, "max": 10},
            "constraints": {"multiple_of": 5}
        }
        
        with patch('random.randint') as mock_randint:
            # First attempt: operand2=0 (skip), then generate multiple
            mock_randint.side_effect = [2, 3, 10, 3]  # 10 is multiple of 5
            operand1, operand2 = QuestionService.generate_operands_with_constraints("addition", 1)
            assert operand1 % 5 == 0  # Multiple of 5

    @patch('app.services.question_service.LevelConfigService.get_level_config')
    def test_generate_operands_with_constraints_division_fallback_invalid_range(self, mock_get_config):
        """Test generate_operands_with_constraints fallback with invalid division range."""
        mock_get_config.return_value = {
            "operand1_range": {"min": 1, "max": 10},
            "operand2_range": {"min": 0, "max": 0},
            "constraints": {}
        }
        
        with patch('random.randint') as mock_randint:
            mock_randint.side_effect = [5, 0] * 101  # All attempts fail, fallback with operand2=0
            with pytest.raises(ValueError, match="invalid division configuration"):
                QuestionService.generate_operands_with_constraints("division", 1, max_attempts=100)

    @patch('app.services.question_service.LevelConfigService.get_level_config')
    @patch('app.services.question_service.PracticeService.create_question')
    def test_generate_question_partial_products_override(self, mock_create_question, mock_get_config):
        """Test generate_question with partial products layout override."""
        mock_get_config.return_value = {
            "operation": "multiplication",
            "operand1_range": {"min": 1, "max": 10},
            "operand2_range": {"min": 1, "max": 10},
            "constraints": {},
            "answer_format": "integer",
            "layout_type": "partialProducts",
            "partial_products_mode": "normal"
        }
        
        mock_question = MagicMock()
        mock_question.id = 123
        mock_create_question.return_value = mock_question
        
        with patch('random.randint') as mock_randint:
            mock_randint.side_effect = [12, 34]
            result = QuestionService.generate_question("multiplication", 1)
            assert result["layout"]["type"] == "partialProducts"
            assert result["layout"]["partialProductsMode"] == "normal"

    @patch('app.services.question_service.LevelConfigService.get_level_config')
    @patch('app.services.question_service.PracticeService.create_question')
    def test_generate_question_multiplication_hints(self, mock_create_question, mock_get_config):
        """Test generate_question generates correct hints for multiplication."""
        mock_get_config.return_value = {
            "operation": "multiplication",
            "operand1_range": {"min": 1, "max": 10},
            "operand2_range": {"min": 1, "max": 10},
            "constraints": {},
            "answer_format": "integer",
            "layout_type": "vertical"
        }
        
        mock_question = MagicMock()
        mock_question.id = 123
        mock_create_question.return_value = mock_question
        
        with patch('random.randint') as mock_randint:
            mock_randint.side_effect = [5, 3]
            result = QuestionService.generate_question("multiplication", 1)
            assert "Stack the digits" in result["hint"] or "carry" in result["hint"].lower()

    @patch('app.services.question_service.LevelConfigService.get_level_config')
    @patch('app.services.question_service.PracticeService.create_question')
    def test_generate_question_division_hints(self, mock_create_question, mock_get_config):
        """Test generate_question generates correct hints for division."""
        mock_get_config.return_value = {
            "operation": "division",
            "operand1_range": {"min": 1, "max": 10},
            "operand2_range": {"min": 1, "max": 10},
            "constraints": {},
            "answer_format": "remainder",
            "layout_type": "longDivision"
        }
        
        mock_question = MagicMock()
        mock_question.id = 123
        mock_create_question.return_value = mock_question
        
        with patch('random.randint') as mock_randint:
            mock_randint.side_effect = [10, 3]
            result = QuestionService.generate_question("division", 1)
            assert "long division" in result["hint"].lower()

