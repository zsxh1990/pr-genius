#!/usr/bin/env python3
"""Generate evidence chain reports for PR scoring.

Phase 4: Evidence Closure
- Generate evidence reports for each case
- Verify evidence chain completeness
- Create validation report
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Paths
EVIDENCE_DIR = Path(__file__).parent.parent / "evidence"
FEATURES_DIR = Path(__file__).parent.parent / "features"
PREDICTIONS_DIR = Path(__file__).parent.parent / "predictions"
REPORTS_DIR = Path(__file__).parent.parent / "reports"
REPORTS_DIR.mkdir(exist_ok=True)


def load_all_data() -> Dict:
    """Load all data sources."""
    # Load features
    with open(FEATURES_DIR / "features.json") as f:
        features = {item["case_id"]: item for item in json.load(f)}

    # Load predictions
    with open(PREDICTIONS_DIR / "predictions.json") as f:
        predictions = {item["case_id"]: item for item in json.load(f)}

    # Load evidence files
    evidence = {}
    for evidence_file in EVIDENCE_DIR.glob("*.json"):
        with open(evidence_file) as f:
            data = json.load(f)
            case_id = data.get("case_id", "")
            if case_id:
                evidence[case_id] = data

    return {
        "features": features,
        "predictions": predictions,
        "evidence": evidence,
    }


def generate_case_report(case_id: str, data: Dict) -> Dict:
    """Generate evidence report for a single case."""
    evidence = data["evidence"].get(case_id, {})
    features = data["features"].get(case_id, {})
    prediction = data["predictions"].get(case_id, {})

    if not evidence:
        return None

    # Build evidence chain
    chain = {
        "case_id": case_id,
        "generated_at": datetime.now().isoformat(),

        # Source data
        "source": {
            "pr_url": evidence.get("pr_url", ""),
            "repo": evidence.get("pr_url", "").split("/pr-genius/")[0] if "/pr-genius/" in evidence.get("pr_url", "") else "",
            "pr_number": int(case_id.split("-")[-1]) if case_id.split("-")[-1].isdigit() else 0,
            "author": evidence.get("author", ""),
            "author_association": evidence.get("author_association", "NONE"),
        },

        # Outcome verification
        "outcome": {
            "actual": evidence.get("outcome", ""),
            "predicted": prediction.get("prediction", ""),
            "correct": evidence.get("outcome") == "merged" and prediction.get("prediction") in ("merge", "likely_merge") or
                       evidence.get("outcome") == "rejected" and prediction.get("prediction") == "unlikely_merge",
            "verification": evidence.get("verification", {}),
        },

        # Feature evidence
        "feature_evidence": {
            "review_engagement": {
                "value": {
                    "human_reviews": features.get("human_reviews", 0),
                    "maintainer_reviews": features.get("maintainer_reviews", 0),
                    "has_approval": features.get("has_approval", False),
                },
                "source": "github_api",
                "confidence": "high" if features.get("human_reviews", 0) > 0 else "low",
            },
            "author_association": {
                "value": features.get("author_association", "NONE"),
                "source": "github_api",
                "confidence": "high",
            },
            "size": {
                "value": {
                    "additions": features.get("additions", 0),
                    "deletions": features.get("deletions", 0),
                    "changed_files": features.get("changed_files", 0),
                },
                "source": "github_api",
                "confidence": "high",
            },
        },

        # Score explanation
        "score_explanation": {
            "merge_probability": prediction.get("merge_probability", 0),
            "component_scores": prediction.get("component_scores", {}),
            "weights": prediction.get("weights", {}),
            "interpretation": interpret_score(prediction),
        },

        # Evidence chain completeness
        "completeness": {
            "has_source_data": bool(evidence.get("pr_url")),
            "has_features": bool(features),
            "has_prediction": bool(prediction),
            "has_verification": bool(evidence.get("verification")),
            "score": calculate_completeness_score(evidence, features, prediction),
        },
    }

    return chain


def interpret_score(prediction: Dict) -> str:
    """Interpret the merge score in plain language."""
    prob = prediction.get("merge_probability", 0)
    pred = prediction.get("prediction", "")

    if pred == "merge":
        return f"High merge probability ({prob:.0%}). Strong review engagement and/or contributor status."
    elif pred == "likely_merge":
        return f"Moderate merge probability ({prob:.0%}). Some positive signals present."
    else:
        return f"Low merge probability ({prob:.0%}). Needs more engagement or changes."


def calculate_completeness_score(evidence: Dict, features: Dict, prediction: Dict) -> float:
    """Calculate evidence chain completeness score."""
    checks = [
        bool(evidence.get("pr_url")),
        bool(evidence.get("author")),
        bool(evidence.get("outcome")),
        bool(features),
        bool(prediction),
        bool(evidence.get("verification")),
        bool(evidence.get("evidence_source")),
    ]
    return sum(checks) / len(checks)


def generate_validation_report(data: Dict) -> Dict:
    """Generate overall validation report."""
    cases = []
    for case_id in data["evidence"]:
        report = generate_case_report(case_id, data)
        if report:
            cases.append(report)

    # Summary statistics
    total = len(cases)
    complete = sum(1 for c in cases if c["completeness"]["score"] >= 0.8)
    correct = sum(1 for c in cases if c["outcome"]["correct"])

    return {
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_cases": total,
            "complete_cases": complete,
            "completeness_rate": round(complete / max(total, 1), 3),
            "correct_predictions": correct,
            "accuracy": round(correct / max(total, 1), 3),
        },
        "cases": cases,
    }


def main():
    """Main entry point."""
    print("=== Evidence Generation ===\n")

    # Load all data
    data = load_all_data()
    print(f"Loaded evidence for {len(data['evidence'])} cases")
    print(f"Loaded features for {len(data['features'])} cases")
    print(f"Loaded predictions for {len(data['predictions'])} cases\n")

    # Generate validation report
    report = generate_validation_report(data)

    # Save report
    output_file = REPORTS_DIR / "evidence_report.json"
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"Generated evidence report")
    print(f"Saved to: {output_file}")

    # Print summary
    summary = report["summary"]
    print(f"\n=== Summary ===")
    print(f"Total cases: {summary['total_cases']}")
    print(f"Complete cases: {summary['complete_cases']} ({summary['completeness_rate']:.0%})")
    print(f"Correct predictions: {summary['correct_predictions']} ({summary['accuracy']:.0%})")


if __name__ == "__main__":
    main()
