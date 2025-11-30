"""Test achievement definitions."""

from typing import Any

# Test achievements
TEST_ACHIEVEMENTS: dict[str, dict[str, Any]] = {
    "multiply-by-two": {
        "title": "Multiply by Two",
        "description": "Complete Level 9 test (20 questions, 90%+)",
        "icon": "✖️",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "multiplication_1",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "multiply-by-three": {
        "title": "Multiply by Three",
        "description": "Complete Level 10 test (20 questions, 90%+)",
        "icon": "✖️",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "multiplication_2",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "multiply-by-four": {
        "title": "Multiply by Four",
        "description": "Complete Level 11 test (20 questions, 90%+)",
        "icon": "✖️",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "multiplication_3",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "multiply-by-five": {
        "title": "Multiply by Five",
        "description": "Complete Level 12 test (20 questions, 90%+)",
        "icon": "✖️",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "multiplication_4",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "multiply-by-six": {
        "title": "Multiply by Six",
        "description": "Complete Level 13 test (20 questions, 90%+)",
        "icon": "✖️",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "multiplication_5",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "multiply-by-seven": {
        "title": "Multiply by Seven",
        "description": "Complete Level 14 test (20 questions, 90%+)",
        "icon": "✖️",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "multiplication_6",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "multiply-by-eight": {
        "title": "Multiply by Eight",
        "description": "Complete Level 15 test (20 questions, 90%+)",
        "icon": "✖️",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "multiplication_7",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "multiply-by-nine": {
        "title": "Multiply by Nine",
        "description": "Complete Level 16 test (20 questions, 90%+)",
        "icon": "✖️",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "multiplication_8",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "multiply-by-zero": {
        "title": "Multiply by Zero",
        "description": "Complete Level 17 test (20 questions, 90%+)",
        "icon": "✖️",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "multiplication_9",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "multiply-by-ten": {
        "title": "Multiply by Ten",
        "description": "Complete Level 18 test (20 questions, 90%+)",
        "icon": "✖️",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "multiplication_10",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "multiply-by-eleven": {
        "title": "Multiply by Eleven",
        "description": "Complete Level 19 test (20 questions, 90%+)",
        "icon": "✖️",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "multiplication_11",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "multiply-by-twelve": {
        "title": "Multiply by Twelve",
        "description": "Complete Level 20 test (20 questions, 90%+)",
        "icon": "✖️",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "multiplication_12",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "multiplication-easy": {
        "title": "Multiplication Easy",
        "description": "Complete Level 21 test (20 questions, 90%+)",
        "icon": "✖️",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "multiplication_12",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "divide-by-two": {
        "title": "Divide by Two",
        "description": "Complete Level 26 test (20 questions, 90%+)",
        "icon": "➗",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "division_2",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "divide-by-three": {
        "title": "Divide by Three",
        "description": "Complete Level 27 test (20 questions, 90%+)",
        "icon": "➗",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "division_3",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "divide-by-four": {
        "title": "Divide by Four",
        "description": "Complete Level 28 test (20 questions, 90%+)",
        "icon": "➗",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "division_4",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "divide-by-five": {
        "title": "Divide by Five",
        "description": "Complete Level 29 test (20 questions, 90%+)",
        "icon": "➗",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "division_5",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "divide-by-six": {
        "title": "Divide by Six",
        "description": "Complete Level 30 test (20 questions, 90%+)",
        "icon": "➗",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "division_6",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "divide-by-seven": {
        "title": "Divide by Seven",
        "description": "Complete Level 31 test (20 questions, 90%+)",
        "icon": "➗",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "division_7",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "divide-by-eight": {
        "title": "Divide by Eight",
        "description": "Complete Level 32 test (20 questions, 90%+)",
        "icon": "➗",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "division_8",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "divide-by-nine": {
        "title": "Divide by Nine",
        "description": "Complete Level 33 test (20 questions, 90%+)",
        "icon": "➗",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "division_9",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "divide-by-ten": {
        "title": "Divide by Ten",
        "description": "Complete Level 34 test (20 questions, 90%+)",
        "icon": "➗",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "division_10",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "divide-by-eleven": {
        "title": "Divide by Eleven",
        "description": "Complete Level 35 test (20 questions, 90%+)",
        "icon": "➗",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "division_11",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "divide-by-twelve": {
        "title": "Divide by Twelve",
        "description": "Complete Level 36 test (20 questions, 90%+)",
        "icon": "➗",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "division_12",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    # Multiplication Test Rank A Achievements
    "multiply-by-two-test-a": {
        "title": "Multiply by Two Test (Rank A)",
        "description": "Complete Level 9 test (multiplication_1) with Rank A (100% accuracy, under 30 questions)",
        "icon": "📗",
        "category": "test",
        "requirements": {
            "type": "test_tier",
            "test_type": "multiplication_1",
            "tier": "a",
            "min_accuracy": 100,
            "max_question_count": 29
        }
    },
    "multiply-by-three-test-a": {
        "title": "Multiply by Three Test (Rank A)",
        "description": "Complete Level 10 test (multiplication_2) with Rank A (100% accuracy, under 30 questions)",
        "icon": "📗",
        "category": "test",
        "requirements": {
            "type": "test_tier",
            "test_type": "multiplication_2",
            "tier": "a",
            "min_accuracy": 100,
            "max_question_count": 29
        }
    },
    "multiply-by-four-test-a": {
        "title": "Multiply by Four Test (Rank A)",
        "description": "Complete Level 11 test (multiplication_3) with Rank A (100% accuracy, under 30 questions)",
        "icon": "📗",
        "category": "test",
        "requirements": {
            "type": "test_tier",
            "test_type": "multiplication_3",
            "tier": "a",
            "min_accuracy": 100,
            "max_question_count": 29
        }
    },
    "multiply-by-five-test-a": {
        "title": "Multiply by Five Test (Rank A)",
        "description": "Complete Level 12 test (multiplication_4) with Rank A (100% accuracy, under 30 questions)",
        "icon": "📗",
        "category": "test",
        "requirements": {
            "type": "test_tier",
            "test_type": "multiplication_4",
            "tier": "a",
            "min_accuracy": 100,
            "max_question_count": 29
        }
    },
    "multiply-by-six-test-a": {
        "title": "Multiply by Six Test (Rank A)",
        "description": "Complete Level 13 test (multiplication_5) with Rank A (100% accuracy, under 30 questions)",
        "icon": "📗",
        "category": "test",
        "requirements": {
            "type": "test_tier",
            "test_type": "multiplication_5",
            "tier": "a",
            "min_accuracy": 100,
            "max_question_count": 29
        }
    },
    "multiply-by-seven-test-a": {
        "title": "Multiply by Seven Test (Rank A)",
        "description": "Complete Level 14 test (multiplication_6) with Rank A (100% accuracy, under 30 questions)",
        "icon": "📗",
        "category": "test",
        "requirements": {
            "type": "test_tier",
            "test_type": "multiplication_6",
            "tier": "a",
            "min_accuracy": 100,
            "max_question_count": 29
        }
    },
    "multiply-by-eight-test-a": {
        "title": "Multiply by Eight Test (Rank A)",
        "description": "Complete Level 15 test (multiplication_7) with Rank A (100% accuracy, under 30 questions)",
        "icon": "📗",
        "category": "test",
        "requirements": {
            "type": "test_tier",
            "test_type": "multiplication_7",
            "tier": "a",
            "min_accuracy": 100,
            "max_question_count": 29
        }
    },
    "multiply-by-nine-test-a": {
        "title": "Multiply by Nine Test (Rank A)",
        "description": "Complete Level 16 test (multiplication_8) with Rank A (100% accuracy, under 30 questions)",
        "icon": "📗",
        "category": "test",
        "requirements": {
            "type": "test_tier",
            "test_type": "multiplication_8",
            "tier": "a",
            "min_accuracy": 100,
            "max_question_count": 29
        }
    },
    "multiply-by-zero-test-a": {
        "title": "Multiply by Zero Test (Rank A)",
        "description": "Complete Level 17 test (multiplication_9) with Rank A (100% accuracy, under 30 questions)",
        "icon": "📗",
        "category": "test",
        "requirements": {
            "type": "test_tier",
            "test_type": "multiplication_9",
            "tier": "a",
            "min_accuracy": 100,
            "max_question_count": 29
        }
    },
    "multiply-by-ten-test-a": {
        "title": "Multiply by Ten Test (Rank A)",
        "description": "Complete Level 18 test (multiplication_10) with Rank A (100% accuracy, under 30 questions)",
        "icon": "📗",
        "category": "test",
        "requirements": {
            "type": "test_tier",
            "test_type": "multiplication_10",
            "tier": "a",
            "min_accuracy": 100,
            "max_question_count": 29
        }
    },
    "multiply-by-eleven-test-a": {
        "title": "Multiply by Eleven Test (Rank A)",
        "description": "Complete Level 19 test (multiplication_11) with Rank A (100% accuracy, under 30 questions)",
        "icon": "📗",
        "category": "test",
        "requirements": {
            "type": "test_tier",
            "test_type": "multiplication_11",
            "tier": "a",
            "min_accuracy": 100,
            "max_question_count": 29
        }
    },
    "multiply-by-twelve-test-a": {
        "title": "Multiply by Twelve Test (Rank A)",
        "description": "Complete Level 20 test (multiplication_12) with Rank A (100% accuracy, under 30 questions)",
        "icon": "📗",
        "category": "test",
        "requirements": {
            "type": "test_tier",
            "test_type": "multiplication_12",
            "tier": "a",
            "min_accuracy": 100,
            "max_question_count": 29
        }
    },
    "basic-math-test": {
        "title": "Basic Math Test",
        "description": "Complete basic math test (50 problems covering levels 1-4)",
        "icon": "📝",
        "category": "test",
        "requirements": {
            "type": "basic_math_test",
            "max_level": 4,
            "question_count": 50,
            "min_accuracy": 0.80
        }
    },
    "multiplication-mastery": {
        "title": "Multiplication Mastery",
        "description": "Complete all multiplication tests 1-12 with Rank S (100% accuracy, 31-59 questions, <6s/question)",
        "icon": "💎",
        "category": "test",
        "requirements": {
            "type": "multiplication_tests_s_rank",
            "test_types": ["multiplication_1", "multiplication_2", "multiplication_3", "multiplication_4", "multiplication_5", "multiplication_6", "multiplication_7", "multiplication_8", "multiplication_9", "multiplication_10", "multiplication_11", "multiplication_12"],
            "tier": "s"
        }
    },
}


def _generate_test_tier_achievements() -> dict[str, dict[str, Any]]:
    """Generate test tier achievement definitions for all test types."""
    test_types = [
        ("addition-1digit", "1-Digit Addition"),
        ("addition-2digit", "2-Digit Addition"),
        ("addition-3digit", "3-Digit Addition"),
        ("subtraction-1digit", "1-Digit Subtraction"),
        ("subtraction-2digit", "2-Digit Subtraction"),
        ("subtraction-3digit", "3-Digit Subtraction"),
        ("multiplication-2", "Times Table ×2"),
        ("multiplication-3", "Times Table ×3"),
        ("multiplication-4", "Times Table ×4"),
        ("multiplication-5", "Times Table ×5"),
        ("multiplication-6", "Times Table ×6"),
        ("multiplication-7", "Times Table ×7"),
        ("multiplication-8", "Times Table ×8"),
        ("multiplication-9", "Times Table ×9"),
        ("multiplication-10", "Times Table ×10"),
        ("multiplication-11", "Times Table ×11"),
        ("multiplication-12", "Times Table ×12"),
        ("multiplication-2digit", "2-Digit Multiplication"),
        ("multiplication-3digit", "3-Digit Multiplication"),
        ("division-1digit", "1-Digit Division"),
        ("division-2digit", "2-Digit Division"),
        ("division-3digit", "3-Digit Division"),
    ]
    
    tiers = [
        {
            "suffix": "b",
            "title_suffix": "Rank B",
            "description": "Complete test",
            "icon": "📘",
            "category": "test",
            "requirements": {
                "type": "test_tier",
                "tier": "b",
                "min_question_count": 30,
            }
        },
        {
            "suffix": "a",
            "title_suffix": "Rank A",
            "description": "100% accuracy (under 30 questions)",
            "icon": "📗",
            "category": "test",
            "requirements": {
                "type": "test_tier",
                "tier": "a",
                "min_accuracy": 100,
                "max_question_count": 29,
            }
        },
        {
            "suffix": "s",
            "title_suffix": "Rank S",
            "description": "Perfect score with speed",
            "icon": "⭐",
            "category": "test",
            "requirements": {
                "type": "test_tier",
                "tier": "s",
                "min_accuracy": 100,
                "min_question_count": 31,
                "max_question_count": 59,
                "max_speed": 6,
            }
        },
        {
            "suffix": "ss",
            "title_suffix": "Rank SS",
            "description": "Elite performance",
            "icon": "🌟",
            "category": "test",
            "requirements": {
                "type": "test_tier",
                "tier": "ss",
                "min_accuracy": 100,
                "max_question_count": 90,
                "max_speed": 4,
            }
        },
        {
            "suffix": "sss",
            "title_suffix": "Rank SSS",
            "description": "Legendary mastery",
            "icon": "💎",
            "category": "test",
            "requirements": {
                "type": "test_tier",
                "tier": "sss",
                "min_accuracy": 100,
                "question_count": 100,
                "max_question_count": 100,
                "max_speed": 2,
            }
        },
    ]
    
    achievements = {}
    for test_type, display_name in test_types:
        for tier_config in tiers:
            code = f"{test_type}-{tier_config['suffix']}"
            achievements[code] = {
                "title": f"{display_name} - {tier_config['title_suffix']}",
                "description": tier_config["description"],
                "icon": tier_config["icon"],
                "category": tier_config["category"],
                "requirements": {
                    **tier_config["requirements"],
                    "test_type": test_type,
                }
            }
    
    return achievements

