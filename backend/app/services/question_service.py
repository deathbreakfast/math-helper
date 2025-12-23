"""Question service for generating questions with solutions and work steps."""

from __future__ import annotations

import json
import math
import random
from fractions import Fraction
from typing import Any

from ..database import log_query
from ..services.level_config_service import LevelConfigService
from ..services.practice_service import PracticeService


class QuestionService:
    """Service for question generation and solving."""

    OPERATIONS = ["addition", "subtraction", "multiplication", "division"]

    @staticmethod
    def get_operation_symbol(operation: str) -> str:
        """Get the symbol for an operation."""
        symbols = {
            "addition": "+",
            "subtraction": "-",
            "multiplication": "×",
            "division": "÷",
        }
        return symbols.get(operation, "+")

    @staticmethod
    def solve(operation: str, a: int, b: int) -> int:
        """Solve a math operation."""
        if operation == "addition":
            return a + b
        elif operation == "subtraction":
            return a - b
        elif operation == "multiplication":
            return a * b
        elif operation == "division":
            if b == 0:
                raise ValueError("Division by zero is not allowed")
            return a // b
        else:
            raise ValueError(f"Unknown operation: {operation}")

    @staticmethod
    def format_answer(
        operation: str,
        operand1: int,
        operand2: int,
        answer_format: str,
    ) -> str:
        """Format answer based on answer format type."""
        if operation != "division":
            return str(QuestionService.solve(operation, operand1, operand2))
        
        # Check for division by zero
        if operand2 == 0:
            return "undefined"
        
        quotient = operand1 // operand2
        remainder = operand1 % operand2
        
        if answer_format == "integer":
            return str(quotient)
        elif answer_format == "remainder":
            if remainder == 0:
                return str(quotient)
            return f"{quotient} R {remainder}"
        elif answer_format == "fraction":
            # Simplify fraction
            frac = Fraction(operand1, operand2)
            return f"{frac.numerator}/{frac.denominator}"
        elif answer_format == "decimal":
            # Calculate decimal with appropriate precision
            result = operand1 / operand2
            if operand2 < 10:
                # Single digit divisor: 2 decimal places
                return f"{result:.2f}".rstrip('0').rstrip('.')
            else:
                # Double digit divisor: 4 decimal places
                return f"{result:.4f}".rstrip('0').rstrip('.')
        else:
            return str(quotient)

    @staticmethod
    def validate_constraints(
        operation: str,
        operand1: int,
        operand2: int,
        constraints: dict[str, Any],
    ) -> bool:
        """Validate operands against constraints."""
        allow_division_by_zero = bool(constraints.get("allow_division_by_zero"))

        # Check exclude_zeros
        if constraints.get("exclude_zeros"):
            if operand1 == 0 or operand2 == 0:
                return False
        
        # Check fixed operand2
        if "fixed_operand2" in constraints:
            if operand2 != constraints["fixed_operand2"]:
                return False
        
        # Check multiple_of constraint
        if "multiple_of" in constraints:
            multiple = constraints["multiple_of"]
            if operand1 % multiple != 0:
                return False
        
        # Check no_remainder for division
        if operation == "division" and constraints.get("no_remainder"):
            if operand2 == 0:
                return allow_division_by_zero and operand1 == 0
            if operand1 % operand2 != 0:
                return False
        
        # Check answer_min
        if "answer_min" in constraints:
            if operation == "division" and operand2 == 0:
                # Undefined has no meaningful ordering constraint
                return allow_division_by_zero
            answer = QuestionService.solve(operation, operand1, operand2)
            if answer < constraints["answer_min"]:
                return False
        
        return True

    @staticmethod
    def _normalize_constraints(
        constraints: dict[str, Any],
        test_constraints: dict[str, Any] | None,
        operation: str,
        level: int,
    ) -> dict[str, Any]:
        """Normalize constraints into a consistent structure for processing.
        
        Returns a dict with normalized constraint values and metadata.
        """
        normalized = {
            "operation": operation,
            "level": level,
            "allow_division_by_zero": constraints.get("allow_division_by_zero", False),
            "no_remainder": constraints.get("no_remainder", False),
            "fixed_operand2": constraints.get("fixed_operand2"),
            "multiple_of": constraints.get("multiple_of"),
            "exclude_zeros": constraints.get("exclude_zeros", False),
            "answer_min": constraints.get("answer_min"),
            "test_multiplication_table": test_constraints.get("multiplication_table") if test_constraints else None,
            "test_division_table": test_constraints.get("division_table") if test_constraints else None,
        }
        return normalized

    @staticmethod
    def _generate_with_test_constraints(
        normalized_constraints: dict[str, Any],
        op1_range: dict[str, int],
        op2_range: dict[str, int],
    ) -> tuple[int, int] | None:
        """Generate operands using test constraints (multiplication_table or division_table).
        
        Returns operands if test constraints are present, None otherwise.
        """
        # Handle multiplication_table test constraint
        if normalized_constraints["test_multiplication_table"] is not None:
            operand2 = normalized_constraints["test_multiplication_table"]
            operand1 = random.randint(op1_range["min"], op1_range["max"])
            return operand1, operand2
        
        # Handle division_table test constraint
        if normalized_constraints["test_division_table"] is not None:
            operand2 = normalized_constraints["test_division_table"]
            if operand2 == 0:
                # Division by zero - use default generation
                operand1 = random.randint(op1_range["min"], op1_range["max"])
            else:
                # Generate operand1 as multiple of operand2
                min_quotient = max(1, op1_range["min"] // operand2)
                max_quotient = op1_range["max"] // operand2
                quotient = random.randint(min_quotient, max_quotient)
                operand1 = operand2 * quotient
            return operand1, operand2
        
        return None

    @staticmethod
    def _generate_with_fixed_operand2(
        normalized_constraints: dict[str, Any],
        op1_range: dict[str, int],
        op2_range: dict[str, int],
        level: int,
    ) -> tuple[int, int] | None:
        """Generate operands when fixed_operand2 constraint is present.
        
        Returns operands if fixed_operand2 is set, None otherwise.
        """
        if normalized_constraints["fixed_operand2"] is None:
            return None
        
        operation = normalized_constraints["operation"]
        constraints = normalized_constraints
        
        operand2 = constraints["fixed_operand2"]
        
        # Handle division by zero case
        if operation == "division" and operand2 == 0:
            if constraints["allow_division_by_zero"]:
                return 0, 0
            # Division by zero - invalid configuration, use operand2_range instead
            if op2_range["min"] > 0 or op2_range["max"] > 0:
                operand2 = random.randint(max(1, op2_range["min"]), max(1, op2_range["max"]))
            else:
                raise ValueError(
                    f"Level {level} has invalid division configuration: fixed_operand2=0 and operand2_range=[0,0]"
                )
        
        # Start with random operand1
        operand1 = random.randint(op1_range["min"], op1_range["max"])
        
        # Apply division no_remainder constraint
        if operation == "division" and constraints["no_remainder"]:
            if operand2 == 0:
                raise ValueError("Division by zero: operand2 cannot be 0 for division operation")
            min_quotient = max(1, op1_range["min"] // operand2)
            max_quotient = op1_range["max"] // operand2
            quotient = random.randint(min_quotient, max_quotient)
            operand1 = operand2 * quotient
        
        # Apply multiple_of constraint
        if constraints["multiple_of"] is not None:
            multiple = constraints["multiple_of"]
            if multiple == 0:
                # Can't generate multiple of 0 - use default
                operand1 = random.randint(op1_range["min"], op1_range["max"])
            else:
                # Generate operand1 as multiple
                min_multiple = max(1, op1_range["min"] // multiple)
                max_multiple = op1_range["max"] // multiple
                if min_multiple <= max_multiple:
                    multiplier = random.randint(min_multiple, max_multiple)
                    operand1 = multiple * multiplier
                else:
                    # Range invalid, use default
                    operand1 = random.randint(op1_range["min"], op1_range["max"])
        
        return operand1, operand2

    @staticmethod
    def _generate_with_general_strategy(
        normalized_constraints: dict[str, Any],
        op1_range: dict[str, int],
        op2_range: dict[str, int],
        max_attempts: int,
    ) -> tuple[int, int]:
        """Generate operands using general random strategy with constraint validation.
        
        Tries multiple attempts, applying constraints during generation when possible.
        """
        operation = normalized_constraints["operation"]
        constraints = normalized_constraints
        
        # Try to generate valid operands
        for _ in range(max_attempts):
            operand1 = random.randint(op1_range["min"], op1_range["max"])
            operand2 = random.randint(op2_range["min"], op2_range["max"])
            
            # Handle division by zero
            if operation == "division" and operand2 == 0:
                if constraints["allow_division_by_zero"]:
                    return 0, 0
                continue
            
            # Apply division no_remainder constraint during generation
            if operation == "division" and constraints["no_remainder"]:
                if operand2 == 0:
                    continue
                operand1 = operand2 * random.randint(
                    max(1, op1_range["min"] // operand2),
                    op1_range["max"] // operand2
                )
            
            # Apply multiple_of constraint during generation
            if constraints["multiple_of"] is not None:
                multiple = constraints["multiple_of"]
                min_multiple = max(1, op1_range["min"] // multiple)
                max_multiple = op1_range["max"] // multiple
                multiplier = random.randint(min_multiple, max_multiple)
                operand1 = multiple * multiplier
            
            # Validate against all constraints (only include keys with actual values)
            validation_constraints = {}
            if constraints["exclude_zeros"]:
                validation_constraints["exclude_zeros"] = True
            if constraints["fixed_operand2"] is not None:
                validation_constraints["fixed_operand2"] = constraints["fixed_operand2"]
            if constraints["multiple_of"] is not None:
                validation_constraints["multiple_of"] = constraints["multiple_of"]
            if constraints["no_remainder"]:
                validation_constraints["no_remainder"] = True
            if constraints["answer_min"] is not None:
                validation_constraints["answer_min"] = constraints["answer_min"]
            if constraints["allow_division_by_zero"]:
                validation_constraints["allow_division_by_zero"] = True
            
            if QuestionService.validate_constraints(operation, operand1, operand2, validation_constraints):
                return operand1, operand2
        
        # Fallback: generate valid operands even if constraints aren't perfectly satisfied
        return QuestionService._generate_fallback_operands(
            normalized_constraints, op1_range, op2_range
        )

    @staticmethod
    def _generate_fallback_operands(
        normalized_constraints: dict[str, Any],
        op1_range: dict[str, int],
        op2_range: dict[str, int],
    ) -> tuple[int, int]:
        """Generate fallback operands when max_attempts is exhausted.
        
        Ensures basic validity (e.g., no division by zero) even if constraints aren't met.
        """
        operation = normalized_constraints["operation"]
        constraints = normalized_constraints
        level = normalized_constraints["level"]
        
        operand1 = random.randint(op1_range["min"], op1_range["max"])
        operand2 = random.randint(op2_range["min"], op2_range["max"])
        
        # For division, ensure operand2 is not 0
        if operation == "division" and operand2 == 0:
            if constraints["allow_division_by_zero"]:
                return 0, 0
            # Use minimum of 1 if range allows, otherwise raise error
            if op2_range["max"] > 0:
                operand2 = max(1, op2_range["min"])
            else:
                raise ValueError(f"Level {level} has invalid division configuration: operand2_range=[0,0]")
        
        return operand1, operand2

    @staticmethod
    def generate_operands_with_constraints(
        operation: str,
        level: int,
        test_constraints: dict[str, Any] | None = None,
        max_attempts: int = 100,
    ) -> tuple[int, int]:
        """Generate operands that satisfy level constraints.
        
        Uses a pipeline pattern:
        1. Normalize constraints from config and test_constraints
        2. Try test constraint strategies first (multiplication_table, division_table)
        3. Try fixed operand2 strategy if applicable
        4. Fall back to general random generation with validation
        
        Args:
            operation: The math operation (addition, subtraction, multiplication, division)
            level: The difficulty level
            test_constraints: Optional test-specific constraints
            max_attempts: Maximum attempts for general strategy generation
            
        Returns:
            Tuple of (operand1, operand2) that satisfy the constraints
        """
        config = LevelConfigService.get_level_config(level)
        if not config:
            raise ValueError(f"Level {level} configuration not found")
        
        constraints = config.get("constraints", {})
        op1_range = config["operand1_range"]
        op2_range = config["operand2_range"]
        
        # Step 1: Normalize constraints
        normalized = QuestionService._normalize_constraints(
            constraints, test_constraints, operation, level
        )
        
        # Step 2: Try test constraint strategies (highest priority)
        result = QuestionService._generate_with_test_constraints(
            normalized, op1_range, op2_range
        )
        if result is not None:
            return result
        
        # Step 3: Try fixed operand2 strategy
        result = QuestionService._generate_with_fixed_operand2(
            normalized, op1_range, op2_range, level
        )
        if result is not None:
            return result
        
        # Step 4: Use general random generation strategy
        return QuestionService._generate_with_general_strategy(
            normalized, op1_range, op2_range, max_attempts
        )

    @staticmethod
    def create_work_steps(operation: str, operand1: int, operand2: int, result: int) -> list[dict[str, Any]]:
        """Generate work steps for showing how to solve the problem."""
        steps = []
        
        if operation == "addition":
            # Simple addition - show carrying if needed
            op1_str = str(operand1)
            op2_str = str(operand2)
            max_len = max(len(op1_str), len(op2_str))
            op1_str = op1_str.zfill(max_len)
            op2_str = op2_str.zfill(max_len)
            
            carry = 0
            for i in range(max_len - 1, -1, -1):
                d1 = int(op1_str[i])
                d2 = int(op2_str[i])
                sum_digit = d1 + d2 + carry
                if sum_digit >= 10:
                    steps.append({
                        "id": f"step-{max_len - i}",
                        "description": f"Add {d1} + {d2} + {carry} = {sum_digit}. Write {sum_digit % 10}, carry {sum_digit // 10}.",
                        "value": str(sum_digit % 10),
                    })
                    carry = sum_digit // 10
                else:
                    steps.append({
                        "id": f"step-{max_len - i}",
                        "description": f"Add {d1} + {d2} + {carry} = {sum_digit}.",
                        "value": str(sum_digit),
                    })
                    carry = 0
            if carry > 0:
                steps.append({
                    "id": f"step-{max_len + 1}",
                    "description": f"Carry {carry} to the next column.",
                    "value": str(carry),
                })
                
        elif operation == "subtraction":
            # Simple subtraction - show borrowing if needed
            op1_str = str(operand1)
            op2_str = str(operand2)
            max_len = max(len(op1_str), len(op2_str))
            op1_str = op1_str.zfill(max_len)
            op2_str = op2_str.zfill(max_len)
            
            borrow = 0
            for i in range(max_len - 1, -1, -1):
                d1 = int(op1_str[i]) - borrow
                d2 = int(op2_str[i])
                if d1 < d2:
                    d1 += 10
                    borrow = 1
                    steps.append({
                        "id": f"step-{max_len - i}",
                        "description": f"Borrow from next column. {d1} - {d2} = {d1 - d2}.",
                        "value": str(d1 - d2),
                    })
                else:
                    steps.append({
                        "id": f"step-{max_len - i}",
                        "description": f"Subtract {d1} - {d2} = {d1 - d2}.",
                        "value": str(d1 - d2),
                    })
                    borrow = 0
                    
        elif operation == "multiplication":
            # Multiplication - show partial products
            op2_str = str(operand2)
            for i, digit in enumerate(reversed(op2_str)):
                d = int(digit)
                partial = operand1 * d
                place_value = 10 ** i
                steps.append({
                    "id": f"step-{i + 1}",
                    "description": f"Multiply {operand1} × {d} = {partial} (place value: {place_value}).",
                    "value": str(partial * place_value),
                })
            steps.append({
                "id": f"step-{len(op2_str) + 1}",
                "description": f"Add all partial products to get {result}.",
                "value": str(result),
            })
            
        elif operation == "division":
            if operand2 == 0:
                return [
                    {
                        "id": "step-1",
                        "description": "Division by 0 is undefined/indeterminate.",
                        "value": "undefined",
                    }
                ]
            # Long division steps
            steps.append({
                "id": "step-1",
                "description": f"Divide {operand1} by {operand2}.",
                "value": str(result),
            })
            remainder = operand1 % operand2
            if remainder > 0:
                steps.append({
                    "id": "step-2",
                    "description": f"Remainder: {remainder}.",
                    "value": str(remainder),
                })
        
        return steps

    @staticmethod
    def create_layout_config(
        operation: str,
        level: int,
        operand1: int,
        operand2: int,
        answer_format: str = "integer",
        test_constraints: dict[str, Any] | None = None,
        config_override: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create layout configuration matching frontend ProblemLayoutConfig type."""
        # Get level config to determine layout type
        config = config_override or LevelConfigService.get_level_config(level)
        layout_type = config.get("layout_type", "vertical") if config else "vertical"
        partial_mode = config.get("partial_products_mode", "easy") if config else "easy"
        
        layout_config: dict[str, Any] = {"type": layout_type}
        
        if layout_type == "partialProducts":
            layout_config = {
                "type": "partialProducts",
                "showWork": True,
                "partialProductsMode": partial_mode,
            }
            # Add work steps
            result = QuestionService.solve(operation, operand1, operand2)
            work_steps = QuestionService.create_work_steps(operation, operand1, operand2, result)
            layout_config["workSteps"] = work_steps
        
        elif layout_type == "longDivision":
            answer_formats = []
            if answer_format == "remainder":
                answer_formats = ["remainder"]
            elif answer_format == "fraction":
                answer_formats = ["fraction"]
            elif answer_format == "decimal":
                answer_formats = ["decimal"]
            else:
                answer_formats = [answer_format] if answer_format != "integer" else ["remainder"]
            
            format_label = answer_format.capitalize() if answer_format != "integer" else "Remainder"
            layout_config = {
                "type": "longDivision",
                "notice": {
                    "tone": "orange",
                    "icon": "lightbulb",
                    "title": "Long Division",
                    "body": f"Use the long division algorithm to solve {operand1} ÷ {operand2}.",
                },
                "tip": {
                    "icon": "lightbulb",
                    "title": "Long Division Tip",
                    "body": "Remember the cycle: Divide, Multiply, Subtract, then Bring Down the next digit.",
                },
                "answerFormats": answer_formats[:1] if answer_formats else ["remainder"],
            }
            # Add work steps
            result = QuestionService.solve(operation, operand1, operand2)
            work_steps = QuestionService.create_work_steps(operation, operand1, operand2, result)
            layout_config["workSteps"] = work_steps
        
        return layout_config

    @staticmethod
    def serialize_work_steps(work_steps: list[dict[str, Any]]) -> str:
        """Serialize work steps to JSON string."""
        return json.dumps(work_steps)

    @staticmethod
    @log_query
    def generate_question(
        operation: str,
        level: int,
        test_constraints: dict[str, Any] | None = None,
        config_override: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate a question with solution and work steps.
        
        Args:
            operation: The operation type (addition, subtraction, multiplication, division)
            level: The difficulty level
            test_constraints: Optional constraints for test sessions (e.g., {"multiplication_table": 5})
        
        Returns:
            Dictionary with question data including id, prompt, operands, correct_answer, layout, etc.
        """
        # Get level configuration
        config = config_override or LevelConfigService.get_level_config(level)
        if not config:
            raise ValueError(f"Level {level} configuration not found")
        
        # Override operation from config if test_constraints don't specify
        if not test_constraints or "operation" not in test_constraints:
            operation = config["operation"]
        
        # Generate operands with constraints
        if config_override is None:
            operand1, operand2 = QuestionService.generate_operands_with_constraints(
                operation, level, test_constraints
            )
        else:
            operand1, operand2 = QuestionService._generate_operands_with_config(
                operation, config, test_constraints
            )
        
        # Get answer format from config
        answer_format = config.get("answer_format", "integer")
        
        # Format answer based on format type
        correct_answer = QuestionService.format_answer(operation, operand1, operand2, answer_format)
        
        # Generate prompt
        prompt = f"{operand1} {QuestionService.get_operation_symbol(operation)} {operand2}"
        
        # Get layout type from config
        layout_type = config.get("layout_type", "vertical")
        partial_mode = config.get("partial_products_mode", "easy")
        
        # Create layout config
        layout_config = QuestionService.create_layout_config(
            operation, level, operand1, operand2, answer_format, test_constraints, config_override=config
        )
        
        # Override layout type if specified in config
        if layout_type == "partialProducts":
            layout_config = {
                "type": "partialProducts",
                "showWork": True,
                "partialProductsMode": partial_mode,
            }
            # Add work steps
            result = QuestionService.solve(operation, operand1, operand2)
            work_steps = QuestionService.create_work_steps(operation, operand1, operand2, result)
            layout_config["workSteps"] = work_steps
        
        # Generate hint and math type label
        hint = "Stack the digits and carry if needed."
        math_type_label = f"{operation.capitalize()} (Standard)"
        
        if operation == "multiplication":
            if layout_config.get("type") == "partialProducts":
                mode = layout_config.get("partialProductsMode", "easy")
                math_type_label = f"Multiplication • Partial Products ({mode.capitalize()})"
                hint = (
                    "Break the multiplier into ones and tens. Fill each row before you add."
                    if mode == "easy"
                    else "Add rows for every digit in the multiplier, then total the partial products."
                )
            else:
                math_type_label = "Multiplication • Normal Up To 12 × 12"
                hint = "Stack the digits and carry when needed."
        elif operation == "division":
            format_label = answer_format.capitalize()
            math_type_label = f"Division • Long Division • {format_label}"
            hint = "Use the long division algorithm: divide, multiply, subtract, bring down."
        
        # Create question in database
        required_level = level
        legacy_level = config.get("legacy_level")
        if isinstance(legacy_level, int) and legacy_level > 0:
            required_level = legacy_level

        difficulty = f"Level {required_level}"
        target_ms = 4000 + required_level * 500
        
        question = PracticeService.create_question(
            operation=operation,
            operand1=operand1,
            operand2=operand2,
            correct_answer=correct_answer,
            prompt=prompt,
            required_level=required_level,
            difficulty=difficulty,
            level_tag=str(required_level),
            target_ms=target_ms,
            hint=hint,
            answer_format=answer_format,
            accepted_answers=None,  # Can be enhanced later
            layout_type=layout_config.get("type"),
            layout_config=layout_config,
            math_type_label=math_type_label,
        )
        
        # Return question data matching frontend format
        return {
            "id": str(question.id),
            "prompt": prompt,
            "operation": operation,
            "operand1": operand1,
            "operand2": operand2,
            "correctAnswer": correct_answer,
            "difficulty": difficulty,
            "targetMs": target_ms,
            "hint": hint,
            "layout": layout_config,
            "answerFormat": answer_format,
            "mathTypeLabel": math_type_label,
            "question_id": question.id,  # For backend use
        }

    @staticmethod
    def _generate_operands_with_config(
        operation: str,
        config: dict[str, Any],
        test_constraints: dict[str, Any] | None = None,
        max_attempts: int = 100,
    ) -> tuple[int, int]:
        """Generate operands using an explicit config dict (no LevelConfigService lookup).
        
        Reuses the same pipeline pattern as generate_operands_with_constraints.
        """
        constraints = config.get("constraints", {}) or {}
        op1_range = config["operand1_range"]
        op2_range = config["operand2_range"]
        # Use a placeholder level since we don't have it from config
        level = 1
        
        # Normalize constraints using the same helper
        normalized = QuestionService._normalize_constraints(
            constraints, test_constraints, operation, level
        )
        
        # Use the same pipeline: test constraints -> fixed operand2 -> general strategy
        result = QuestionService._generate_with_test_constraints(
            normalized, op1_range, op2_range
        )
        if result is not None:
            return result
        
        result = QuestionService._generate_with_fixed_operand2(
            normalized, op1_range, op2_range, level
        )
        if result is not None:
            return result
        
        return QuestionService._generate_with_general_strategy(
            normalized, op1_range, op2_range, max_attempts
        )

