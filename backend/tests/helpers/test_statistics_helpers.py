"""Statistical helper functions for backend tests."""

import math
from typing import Tuple, List, Optional

# NOTE: These are helper functions, not tests. Pytest should not collect them.

def calculate_binomial_confidence_interval(
    n: int, 
    p: float, 
    confidence: float = 0.95
) -> Tuple[float, float]:
    """Calculate Wilson score interval for binomial proportion.
    
    The Wilson score interval is more accurate than the normal approximation
    interval, especially for small sample sizes or extreme probabilities.
    
    Args:
        n: Sample size
        p: Observed proportion (or expected proportion for planning)
        confidence: Confidence level (default 0.95)
        
    Returns:
        Tuple of (lower_bound, upper_bound) as percentages
    """
    if n == 0:
        return 0.0, 0.0
        
    z = 1.96  # Approximate z-score for 95% confidence
    if confidence != 0.95:
        # Add other z-scores if needed, defaulting to 1.96
        pass
        
    # Wilson score interval formula
    denominator = 1 + z**2/n
    center_adjusted_probability = p + z**2/(2*n)
    adjusted_standard_deviation = math.sqrt((p*(1 - p) + z**2/(4*n)) / n)
    
    lower_bound = (center_adjusted_probability - z*adjusted_standard_deviation) / denominator
    upper_bound = (center_adjusted_probability + z*adjusted_standard_deviation) / denominator
    
    return max(0.0, lower_bound * 100), min(100.0, upper_bound * 100)

def check_distribution_proportion(
    observed_count: int, 
    total: int, 
    expected_proportion: float, 
    confidence: float = 0.95
) -> Tuple[bool, float, Tuple[float, float]]:
    """Test if observed proportion is consistent with expected proportion.
    
    Renamed from test_distribution_proportion to avoid pytest collection.
    
    Args:
        observed_count: Number of successes
        total: Total sample size
        expected_proportion: Expected probability of success (0-1)
        confidence: Confidence level (default 0.95)
        
    Returns:
        Tuple of (is_valid, z_score, (lower_ci, upper_ci))
        - is_valid: True if expected_proportion falls within the confidence interval of observed
    """
    if total == 0:
        return False, 0.0, (0.0, 0.0)
        
    observed_p = observed_count / total
    
    # Calculate CI around observed proportion
    lower_ci, upper_ci = calculate_binomial_confidence_interval(total, observed_p, confidence)
    
    # Check if expected proportion is within the CI
    expected_percent = expected_proportion * 100
    is_valid = lower_ci <= expected_percent <= upper_ci
    
    # Calculate z-score for difference
    # Standard error under null hypothesis
    se = math.sqrt(expected_proportion * (1 - expected_proportion) / total)
    z_score = (observed_p - expected_proportion) / se if se > 0 else 0.0
    
    return is_valid, z_score, (lower_ci, upper_ci)

# Removed alias to avoid pytest collection
# test_distribution_proportion = check_distribution_proportion

def check_distribution_multinomial(
    observed_counts: List[int], 
    expected_proportions: List[float], 
    confidence: float = 0.95
) -> Tuple[bool, float, float]:
    """Perform Chi-Square Goodness of Fit test for multinomial distribution.
    
    Renamed from test_distribution_multinomial to avoid pytest collection.
    
    Args:
        observed_counts: List of observed counts for each category
        expected_proportions: List of expected proportions for each category (must sum to 1.0)
        confidence: Confidence level (default 0.95)
        
    Returns:
        Tuple of (is_valid, chi_square_statistic, p_value_approx)
        - is_valid: True if p_value > (1 - confidence)
        - Note: p-value is approximated or critical value comparison used
    """
    total_observed = sum(observed_counts)
    if total_observed == 0:
        return False, 0.0, 0.0
        
    expected_counts = [p * total_observed for p in expected_proportions]
    
    # Calculate Chi-Square statistic
    chi_square = 0.0
    for obs, exp in zip(observed_counts, expected_counts):
        if exp > 0:
            chi_square += ((obs - exp) ** 2) / exp
            
    # Critical values for Chi-Square distribution at alpha=0.05
    # df = k - 1
    df = len(observed_counts) - 1
    critical_values = {
        1: 3.841,
        2: 5.991,
        3: 7.815,
        4: 9.488,
        5: 11.070
    }
    
    critical_val = critical_values.get(df, 3.841 + df) # Rough fallback
    is_valid = chi_square <= critical_val
    
    # Rough p-value approximation not implemented to avoid scipy dependency
    # Just returning 1.0 if valid, 0.0 if not for simplicity in this helper
    p_value_approx = 1.0 if is_valid else 0.0
    
    return is_valid, chi_square, p_value_approx

# Removed alias to avoid pytest collection
# test_distribution_multinomial = check_distribution_multinomial

def get_acceptable_range(
    expected_proportion: float, 
    n: int, 
    confidence: float = 0.95
) -> Tuple[float, float]:
    """Get acceptable percentage range for a given expected proportion and sample size.
    
    This calculates the confidence interval around the *expected* proportion,
    giving the range of observed values that would be considered statistically consistent.
    
    Args:
        expected_proportion: Expected probability (0-1)
        n: Sample size
        confidence: Confidence level
        
    Returns:
        Tuple of (min_percentage, max_percentage)
    """
    return calculate_binomial_confidence_interval(n, expected_proportion, confidence)
