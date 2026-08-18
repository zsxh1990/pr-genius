#!/usr/bin/env python3
"""Enrich case studies with real PR data and evidence chains.

Phase 1: Data Enrichment
- Fetch PR details from GitHub API
- Extract review data
- Build evidence chains
- Save to evidence/ directory
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Paths
CASES_DIR = Path(__file__).parent.parent / "review-cases"
EVIDENCE_DIR = Path(__file__).parent.parent / "evidence"
EVIDENCE_DIR.mkdir(exist_ok=True)


def gh_api(endpoint: str) -> dict:
    """Call GitHub API via gh CLI."""
    try:
        result = subprocess.run(
            ["gh", "api", endpoint],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
        if result.returncode != 0:
            return None
        return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError):
        return None


def fetch_pr_details(repo: str, pr_number: int) -> dict:
    """Fetch PR details from GitHub."""
    pr = gh_api(f"repos/{repo}/pulls/{pr_number}")
    if not pr:
        return None

    # Fetch reviews
    reviews = gh_api(f"repos/{repo}/pulls/{pr_number}/reviews") or []

    # Fetch issue comments
    comments = gh_api(f"repos/{repo}/issues/{pr_number}/comments") or []

    return {
        "pr": pr,
        "reviews": reviews,
        "comments": comments,
    }


def classify_reviews(reviews: list) -> dict:
    """Classify reviews into bot vs human."""
    bot_keywords = ["bot", "copilot", "coderabbit", "dependabot", "renovate"]

    bot_reviews = []
    human_reviews = []
    maintainer_reviews = []

    for r in reviews:
        author = r.get("user", {}).get("login", "").lower()
        association = r.get("author_association", "NONE")

        is_bot = any(kw in author for kw in bot_keywords)

        if is_bot:
            bot_reviews.append(r)
        else:
            human_reviews.append(r)
            if association in ("OWNER", "MEMBER", "COLLABORATOR"):
                maintainer_reviews.append(r)

    # Calculate review depth
    review_bodies = [(r.get("body") or "") for r in reviews if r.get("body")]
    avg_depth = sum(len(b) for b in review_bodies) / max(len(review_bodies), 1)

    # Check approval status
    states = [r.get("state", "") for r in reviews]
    has_approval = "APPROVED" in states
    has_changes_requested = "CHANGES_REQUESTED" in states

    return {
        "total_reviews": len(reviews),
        "bot_reviews": len(bot_reviews),
        "human_reviews": len(human_reviews),
        "maintainer_reviews": len(maintainer_reviews),
        "avg_review_depth": round(avg_depth),
        "has_approval": has_approval,
        "has_changes_requested": has_changes_requested,
        "review_states": states,
    }


def build_evidence_chain(pr_data: dict, case: dict) -> dict:
    """Build evidence chain for a case."""
    pr = pr_data["pr"]
    reviews = pr_data["reviews"]

    # Determine outcome
    if pr.get("merged_at"):
        outcome = "merged"
    elif pr.get("closed_at"):
        outcome = "rejected"
    else:
        outcome = "open"

    # Classify reviews
    review_engagement = classify_reviews(reviews)

    # Build evidence
    evidence = {
        "case_id": f"{case['repo'].split('/')[-1].lower()}-{case['pr_number']}",
        "pr_url": pr.get("html_url", ""),
        "outcome": outcome,
        "merged_at": pr.get("merged_at"),
        "closed_at": pr.get("closed_at"),
        "created_at": pr.get("created_at"),
        "author": pr.get("user", {}).get("login", ""),
        "author_association": pr.get("author_association", "NONE"),
        "additions": pr.get("additions", 0),
        "deletions": pr.get("deletions", 0),
        "changed_files": pr.get("changed_files", 0),
        "labels": [l.get("name", "") for l in pr.get("labels", [])],
        "review_engagement": review_engagement,
        "evidence_source": {
            "api": "github",
            "fetched_at": datetime.now().isoformat(),
            "endpoints": [
                f"/repos/{case['repo']}/pulls/{case['pr_number']}",
                f"/repos/{case['repo']}/pulls/{case['pr_number']}/reviews",
            ],
        },
        "verification": {
            "source": "github_api",
            "timestamp": datetime.now().isoformat(),
            "status": "verified",
        },
    }

    # Calculate merge probability signal
    evidence["signals"] = calculate_signals(evidence)

    return evidence


def calculate_signals(evidence: dict) -> dict:
    """Calculate key signals from evidence."""
    re = evidence["review_engagement"]

    # Merge probability factors
    association_map = {
        "OWNER": 0.95,
        "MEMBER": 0.85,
        "COLLABORATOR": 0.70,
        "CONTRIBUTOR": 0.40,
        "NONE": 0.15,
    }

    association_score = association_map.get(evidence["author_association"], 0.15)

    # Review engagement score
    if re["human_reviews"] > 0:
        review_score = 0.70 + min(re["human_reviews"] * 0.10, 0.25)
    else:
        review_score = 0.05

    # Approval score
    approval_score = 0.20 if re["has_approval"] else 0.0

    # Size score (smaller = easier to merge)
    total_changes = evidence["additions"] + evidence["deletions"]
    if total_changes < 50:
        size_score = 0.15
    elif total_changes < 200:
        size_score = 0.10
    elif total_changes < 500:
        size_score = 0.05
    else:
        size_score = 0.0

    # Calculate merge probability
    merge_probability = (
        association_score * 0.30
        + review_score * 0.40
        + approval_score * 0.20
        + size_score * 0.10
    )

    return {
        "merge_probability": round(merge_probability, 3),
        "association_score": association_score,
        "review_score": review_score,
        "approval_score": approval_score,
        "size_score": size_score,
        "has_human_review": re["human_reviews"] > 0,
        "has_approval": re["has_approval"],
    }


def enrich_case(case_file: Path) -> bool:
    """Enrich a single case with evidence."""
    with open(case_file) as f:
        case = json.load(f)

    repo = case.get("repo", "")
    pr_number = case.get("pr_number", 0)

    if not repo or not pr_number:
        return False

    # Check if evidence already exists
    evidence_file = EVIDENCE_DIR / f"{case_file.stem}.json"
    if evidence_file.exists():
        print(f"  SKIP: {case_file.stem} (evidence exists)")
        return True

    # Fetch PR data
    print(f"  Fetching: {repo}#{pr_number}...")
    pr_data = fetch_pr_details(repo, pr_number)
    if not pr_data:
        print(f"  FAILED: Could not fetch PR data")
        return False

    # Build evidence chain
    evidence = build_evidence_chain(pr_data, case)

    # Save evidence
    with open(evidence_file, "w") as f:
        json.dump(evidence, f, indent=2, ensure_ascii=False)

    print(f"  OK: {evidence['outcome']} | {evidence['review_engagement']['human_reviews']} human reviews")
    return True


def main():
    """Main entry point."""
    print("=== Case Enrichment ===\n")

    # Find all case files
    case_files = sorted(CASES_DIR.glob("*.json"))
    print(f"Found {len(case_files)} cases\n")

    # Enrich each case
    success = 0
    failed = 0

    for case_file in case_files:
        if enrich_case(case_file):
            success += 1
        else:
            failed += 1

    print(f"\n=== Results ===")
    print(f"Success: {success}")
    print(f"Failed: {failed}")
    print(f"Total: {len(case_files)}")

    # Verify evidence
    evidence_files = list(EVIDENCE_DIR.glob("*.json"))
    print(f"\nEvidence files: {len(evidence_files)}")


if __name__ == "__main__":
    main()
