"""Risk assessment helper functions for PR Genius."""

from typing import Dict, Any


def calculate_risk_score(
    factors: Dict[str, Any],
    weights: Dict[str, float] = None
) -> float:
    """Calculate a weighted risk score from multiple factors.

    Args:
        factors: Dictionary of risk factors with their values
        weights: Optional custom weights for each factor

    Returns:
        Risk score between 0.0 and 1.0
    """
    if weights is None:
        weights = {
            "complexity": 0.3,
            "test_coverage": 0.25,
            "review_depth": 0.2,
            "change_size": 0.15,
            "author_experience": 0.1,
        }

    score = 0.0
    total_weight = 0.0

    for factor, value in factors.items():
        if factor in weights:
            weight = weights[factor]
            # Normalize value to 0-1 range
            normalized = min(max(float(value), 0.0), 1.0)
            score += normalized * weight
            total_weight += weight

    if total_weight > 0:
        score /= total_weight

    return round(score, 3)


def classify_risk(score: float) -> str:
    """Classify risk score into categories.

    Args:
        score: Risk score between 0.0 and 1.0

    Returns:
        Risk category: 'low', 'medium', or 'high'
    """
    if score < 0.3:
        return "low"
    elif score < 0.7:
        return "medium"
    else:
        return "high"


def generate_risk_report(factors: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a comprehensive risk report.

    Args:
        factors: Dictionary of risk factors

    Returns:
        Risk report with score, category, and recommendations
    """
    score = calculate_risk_score(factors)
    category = classify_risk(score)

    recommendations = []
    if factors.get("test_coverage", 1.0) < 0.5:
        recommendations.append("Increase test coverage before merging")
    if factors.get("complexity", 0.0) > 0.7:
        recommendations.append("Consider simplifying complex logic")
    if factors.get("change_size", 0.0) > 0.8:
        recommendations.append("Consider splitting into smaller PRs")

    return {
        "score": score,
        "category": category,
        "factors": factors,
        "recommendations": recommendations,
    }
