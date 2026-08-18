#!/usr/bin/env python3
"""Score merge probability using weighted rules.

Phase 3: Scoring Model
- Load features from features/
- Apply weighted scoring rules
- Generate merge probability predictions
- Save predictions to predictions/
"""

import json
from pathlib import Path
from typing import Dict, List

# Paths
FEATURES_DIR = Path(__file__).parent.parent / "features"
PREDICTIONS_DIR = Path(__file__).parent.parent / "predictions"
PREDICTIONS_DIR.mkdir(exist_ok=True)


def load_features() -> List[Dict]:
    """Load features from features directory."""
    with open(FEATURES_DIR / "features.json") as f:
        return json.load(f)


def calculate_merge_score(features: Dict) -> Dict:
    """Calculate merge probability using weighted rules."""
    weights = {
        "review_engagement": 0.40,  # Most important signal
        "author_association": 0.25,
        "approval": 0.20,
        "size": 0.10,
        "labels": 0.05,
    }

    scores = {}

    # Review engagement score (0-1)
    human_reviews = features.get("human_reviews", 0)
    maintainer_reviews = features.get("maintainer_reviews", 0)
    if human_reviews > 0:
        review_score = min(0.7 + human_reviews * 0.1, 1.0)
        if maintainer_reviews > 0:
            review_score = min(review_score + 0.15, 1.0)
    else:
        review_score = 0.05
    scores["review_engagement"] = review_score

    # Author association score (0-1)
    association_map = {
        "OWNER": 0.95,
        "MEMBER": 0.85,
        "COLLABORATOR": 0.70,
        "CONTRIBUTOR": 0.40,
        "NONE": 0.15,
    }
    association = features.get("author_association", "NONE")
    scores["author_association"] = association_map.get(association, 0.15)

    # Approval score (0-1)
    if features.get("has_approval"):
        scores["approval"] = 0.95
    elif features.get("has_changes_requested"):
        scores["approval"] = 0.10
    else:
        scores["approval"] = 0.30  # No approval, no changes requested

    # Size score (0-1) - smaller is better
    total_changes = features.get("additions", 0) + features.get("deletions", 0)
    if total_changes < 50:
        scores["size"] = 0.90
    elif total_changes < 200:
        scores["size"] = 0.70
    elif total_changes < 500:
        scores["size"] = 0.50
    elif total_changes < 1000:
        scores["size"] = 0.30
    else:
        scores["size"] = 0.15

    # Label bonus
    label_score = 0.0
    if features.get("has_help_wanted"):
        label_score += 0.15
    if features.get("has_good_first_issue"):
        label_score += 0.10
    if features.get("has_bug_label"):
        label_score += 0.05
    scores["labels"] = min(label_score, 0.20)

    # Calculate weighted score
    weighted_score = sum(scores[k] * weights[k] for k in weights)

    # Determine prediction
    if weighted_score >= 0.60:
        prediction = "merge"
        confidence = "high"
    elif weighted_score >= 0.40:
        prediction = "likely_merge"
        confidence = "medium"
    else:
        prediction = "unlikely_merge"
        confidence = "low"

    return {
        "case_id": features.get("case_id", ""),
        "actual_outcome": features.get("outcome", ""),
        "prediction": prediction,
        "confidence": confidence,
        "merge_probability": round(weighted_score, 3),
        "component_scores": {k: round(v, 3) for k, v in scores.items()},
        "weights": weights,
        "features_used": {
            "human_reviews": human_reviews,
            "maintainer_reviews": maintainer_reviews,
            "association": association,
            "has_approval": features.get("has_approval", False),
            "has_changes_requested": features.get("has_changes_requested", False),
            "total_changes": total_changes,
            "has_help_wanted": features.get("has_help_wanted", False),
            "has_good_first_issue": features.get("has_good_first_issue", False),
        },
    }


def evaluate_predictions(predictions: List[Dict]) -> Dict:
    """Evaluate prediction accuracy."""
    correct = 0
    total = 0
    true_positives = 0
    false_positives = 0
    true_negatives = 0
    false_negatives = 0

    for pred in predictions:
        actual = pred["actual_outcome"]
        predicted = pred["prediction"]

        if actual == "merged":
            if predicted in ("merge", "likely_merge"):
                true_positives += 1
                correct += 1
            else:
                false_negatives += 1
            total += 1
        elif actual == "rejected":
            if predicted == "unlikely_merge":
                true_negatives += 1
                correct += 1
            else:
                false_positives += 1
            total += 1

    precision = true_positives / max(true_positives + false_positives, 1)
    recall = true_positives / max(true_positives + false_negatives, 1)
    f1 = 2 * precision * recall / max(precision + recall, 0.001)
    accuracy = correct / max(total, 1)

    return {
        "total": total,
        "correct": correct,
        "accuracy": round(accuracy, 3),
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "true_positives": true_positives,
        "false_positives": false_positives,
        "true_negatives": true_negatives,
        "false_negatives": false_negatives,
    }


def main():
    """Main entry point."""
    print("=== Merge Scoring ===\n")

    # Load features
    features = load_features()
    print(f"Loaded {len(features)} feature sets\n")

    # Score each case
    predictions = []
    for feat in features:
        pred = calculate_merge_score(feat)
        predictions.append(pred)

    # Save predictions
    output_file = PREDICTIONS_DIR / "predictions.json"
    with open(output_file, "w") as f:
        json.dump(predictions, f, indent=2, ensure_ascii=False)

    print(f"Generated {len(predictions)} predictions")
    print(f"Saved to: {output_file}")

    # Evaluate
    eval_result = evaluate_predictions(predictions)
    print(f"\n=== Evaluation ===")
    print(f"Accuracy: {eval_result['accuracy']:.1%}")
    print(f"Precision: {eval_result['precision']:.3f}")
    print(f"Recall: {eval_result['recall']:.3f}")
    print(f"F1: {eval_result['f1']:.3f}")
    print(f"TP: {eval_result['true_positives']}, FP: {eval_result['false_positives']}")
    print(f"TN: {eval_result['true_negatives']}, FN: {eval_result['false_negatives']}")

    # Save evaluation
    eval_file = PREDICTIONS_DIR / "evaluation.json"
    with open(eval_file, "w") as f:
        json.dump(eval_result, f, indent=2)


if __name__ == "__main__":
    main()
