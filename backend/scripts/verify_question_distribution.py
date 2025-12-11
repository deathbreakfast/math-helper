"""Statistical verification script for question distribution.

This script generates multiple sessions and verifies that the question distribution
matches the expected percentages for each category.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from collections import Counter
from app.models import User, db
from app.services.adaptive_distribution_service import AdaptiveDistributionService


def verify_distribution(num_sessions: int = 1000):
    """Verify question distribution across categories."""
    # Create or get a test user
    user = User.query.filter_by(email="test@example.com").first()
    if not user:
        user = User(
            email="test@example.com",
            username="test_user",
            level=10,
        )
        db.session.add(user)
        db.session.commit()
    
    category_counts = Counter()
    level_distributions = {
        "level": Counter(),
        "requirements": Counter(),
        "bottom_performers": Counter(),
        "random": Counter(),
    }
    
    print(f"Generating {num_sessions} sessions...")
    
    for i in range(num_sessions):
        # Select category
        category = AdaptiveDistributionService.select_category()
        category_counts[category] += 1
        
        # Generate distribution for this category
        distribution = AdaptiveDistributionService.generate_adaptive_question_distribution(
            user, category=category
        )
        
        # Sample 10 questions from this distribution
        for _ in range(10):
            level = AdaptiveDistributionService.select_level_from_distribution(distribution)
            level_distributions[category][level] += 1
        
        if (i + 1) % 100 == 0:
            print(f"Processed {i + 1} sessions...")
    
    print("\n" + "=" * 60)
    print("CATEGORY DISTRIBUTION")
    print("=" * 60)
    total = sum(category_counts.values())
    expected_percentages = {
        "level": 35,
        "requirements": 35,
        "bottom_performers": 20,
        "random": 10,
    }
    
    for category, count in category_counts.items():
        percentage = (count / total) * 100
        expected = expected_percentages.get(category, 0)
        diff = abs(percentage - expected)
        status = "✓" if diff < 5 else "✗"  # Allow 5% tolerance
        print(f"{category:20s} {percentage:6.2f}% (expected {expected:5.1f}%) {status}")
    
    print("\n" + "=" * 60)
    print("LEVEL DISTRIBUTION BY CATEGORY")
    print("=" * 60)
    
    for category in ["level", "requirements", "bottom_performers", "random"]:
        print(f"\n{category.upper()}:")
        level_counts = level_distributions[category]
        total_levels = sum(level_counts.values())
        
        if total_levels > 0:
            # Show top 10 levels
            for level, count in level_counts.most_common(10):
                percentage = (count / total_levels) * 100
                print(f"  Level {level:2d}: {percentage:6.2f}% ({count} questions)")
    
    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    verify_distribution(1000)










