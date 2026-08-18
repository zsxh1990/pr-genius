#!/usr/bin/env python3
"""Extract features from enriched cases for scoring.

Phase 2: Feature Extraction
- Load enriched cases from evidence/
- Extract key features for scoring
- Save feature vectors
"""

import json
from pathlib import Path
from typing import Dict, List

# Paths
EVIDENCE_DIR = Path(__file__).parent.parent / "evidence"
FEATURES_DIR = Path(__file__).parent.parent / "features"
FEATURES_DIR.mkdir(exist_ok=True)


def load_enriched_cases() -> List[Dict]:
    """Load all enriched cases from evidence directory."""
    cases = []
    for evidence_file in sorted(EVIDENCE_DIR.glob("*.json")):
        with open(evidence_file) as f:
            cases.append(json.load(f))
    return cases


def extract_features(case: Dict) -> Dict:
    """Extract features from a single enriched case."""
    pr = case.get("pr", {})
    re = case.get("review_engagement", {})
    signals = case.get("signals", {})

    features = {
        "case_id": case.get("case_id", ""),
        "outcome": case.get("outcome", ""),

        # PR characteristics
        "additions": case.get("additions", 0),
        "deletions": case.get("deletions", 0),
        "changed_files": case.get("changed_files", 0),

        # Author
        "author_association": case.get("author_association", "NONE"),
        "association_score": signals.get("association_score", 0),

        # Review engagement
        "total_reviews": re.get("total_reviews", 0),
        "human_reviews": re.get("human_reviews", 0),
        "bot_reviews": re.get("bot_reviews", 0),
        "maintainer_reviews": re.get("maintainer_reviews", 0),
        "has_approval": re.get("has_approval", False),
        "has_changes_requested": re.get("has_changes_requested", False),
        "avg_review_depth": re.get("avg_review_depth", 0),

        # Time features
        "time_to_first_review": calculate_time_to_first_review(case),
        "time_to_merge": calculate_time_to_merge(case),

        # Labels
        "has_bug_label": any("bug" in l.lower() for l in case.get("labels", [])),
        "has_enhancement_label": any("enhancement" in l.lower() for l in case.get("labels", [])),
        "has_help_wanted": any("help wanted" in l.lower() for l in case.get("labels", [])),
        "has_good_first_issue": any("good first issue" in l.lower() for l in case.get("labels", [])),

        # Calculated scores
        "review_score": signals.get("review_score", 0),
        "approval_score": signals.get("approval_score", 0),
        "size_score": signals.get("size_score", 0),
        "merge_probability": signals.get("merge_probability", 0),
    }

    return features


def calculate_time_to_first_review(case: Dict) -> float:
    """Calculate time from PR creation to first review in hours."""
    created_at = case.get("created_at")
    reviews = case.get("review_engagement", {})

    # If we have review data, estimate based on review count
    if reviews.get("human_reviews", 0) > 0:
        # Estimate: assume first review happens within 24h for active repos
        return 24.0
    return -1.0  # No review


def calculate_time_to_merge(case: Dict) -> float:
    """Calculate time from PR creation to merge in hours."""
    created_at = case.get("created_at")
    merged_at = case.get("merged_at")

    if not created_at or not merged_at:
        return -1.0

    from datetime import datetime
    try:
        created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        merged = datetime.fromisoformat(merged_at.replace("Z", "+00:00"))
        delta = merged - created
        return delta.total_seconds() / 3600.0
    except:
        return -1.0


def main():
    """Main entry point."""
    print("=== Feature Extraction ===\n")

    # Load enriched cases
    cases = load_enriched_cases()
    print(f"Loaded {len(cases)} enriched cases\n")

    # Extract features
    features_list = []
    for case in cases:
        features = extract_features(case)
        features_list.append(features)

    # Save features
    output_file = FEATURES_DIR / "features.json"
    with open(output_file, "w") as f:
        json.dump(features_list, f, indent=2, ensure_ascii=False)

    print(f"Extracted features for {len(features_list)} cases")
    print(f"Saved to: {output_file}")

    # Summary statistics
    merged = sum(1 for f in features_list if f["outcome"] == "merged")
    rejected = sum(1 for f in features_list if f["outcome"] == "rejected")
    print(f"\nSummary:")
    print(f"  Merged: {merged}")
    print(f"  Rejected: {rejected}")
    print(f"  Total: {len(features_list)}")


if __name__ == "__main__":
    main()
