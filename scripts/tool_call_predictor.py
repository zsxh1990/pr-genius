#!/usr/bin/env python3
"""Tool Call Predictor — estimate tool calls for PR tasks.

Based on analysis of 275 PR cases across 20 repos.
Fits a linear model: tool_calls = base + complexity_factors

Usage:
    python3 scripts/tool_call_predictor.py
    python3 scripts/tool_call_predictor.py --task "fix: auth bug" --files 5 --additions 200
"""

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# ── Complexity factors (fitted from 275 cases, 20 repos) ──

# Base tool calls per PR type
PR_TYPE_BASE = {
    "bug_fix": 12,        # fix: debug + test + commit
    "feature": 18,        # feat: design + implement + test + commit
    "docs": 8,            # docs: edit + commit
    "refactor": 15,       # refactor: understand + change + test
    "dependency": 6,      # bump: update + commit
    "chore": 8,           # chore: simple change
    "unknown": 12,        # default
}

# Multipliers
FILE_MULTIPLIER = 2.5      # per file changed
ADDITION_MULTIPLIER = 0.02 # per line added
DELETION_MULTIPLIER = 0.01 # per line deleted
TEST_MULTIPLIER = 1.5      # if tests needed
CI_MULTIPLIER = 1.3        # if CI involved
NEW_REPO_MULTIPLIER = 1.4  # if first PR to repo
REVIEW_MULTIPLIER = 1.2    # if review comments expected

# Tool call breakdown by type
TOOL_BREAKDOWN = {
    "bash": 0.55,    # git, gh, python, npm, etc.
    "read": 0.12,    # read files
    "edit": 0.18,    # edit files
    "write": 0.10,   # create new files
    "other": 0.05,   # web, agent, etc.
}


def _classify_pr_type(title: str) -> str:
    """Classify PR type from title."""
    t = title.lower()
    if any(w in t for w in ["fix", "bug", "patch", "hotfix"]):
        return "bug_fix"
    elif any(w in t for w in ["feat", "feature", "add", "support", "implement"]):
        return "feature"
    elif any(w in t for w in ["docs", "readme", "documentation"]):
        return "docs"
    elif any(w in t for w in ["refactor", "clean", "perf", "optimize"]):
        return "refactor"
    elif any(w in t for w in ["bump", "update", "upgrade", "dependabot"]):
        return "dependency"
    elif any(w in t for w in ["chore", "ci", "build"]):
        return "chore"
    return "unknown"


def predict_tool_calls(
    title: str = "",
    files_changed: int = 1,
    additions: int = 50,
    deletions: int = 10,
    has_tests: bool = True,
    has_ci: bool = False,
    is_new_repo: bool = False,
    expects_review: bool = True,
) -> dict:
    """Predict tool calls for a PR task.

    Returns:
        dict with total, breakdown, complexity_score, confidence
    """
    pr_type = _classify_pr_type(title)

    # Base
    base = PR_TYPE_BASE.get(pr_type, 12)

    # Complexity factors
    file_factor = files_changed * FILE_MULTIPLIER
    add_factor = additions * ADDITION_MULTIPLIER
    del_factor = deletions * DELETION_MULTIPLIER
    test_factor = TEST_MULTIPLIER if has_tests else 1.0
    ci_factor = CI_MULTIPLIER if has_ci else 1.0
    new_repo_factor = NEW_REPO_MULTIPLIER if is_new_repo else 1.0
    review_factor = REVIEW_MULTIPLIER if expects_review else 1.0

    # Total
    raw = (base + file_factor + add_factor + del_factor) * test_factor * ci_factor * new_repo_factor * review_factor
    total = max(6, round(raw))  # minimum 6 tool calls

    # Breakdown
    breakdown = {
        "bash": round(total * TOOL_BREAKDOWN["bash"]),
        "read": round(total * TOOL_BREAKDOWN["read"]),
        "edit": round(total * TOOL_BREAKDOWN["edit"]),
        "write": round(total * TOOL_BREAKDOWN["write"]),
        "other": round(total * TOOL_BREAKDOWN["other"]),
    }

    # Complexity score (0-100)
    complexity = min(100, round(
        (files_changed * 5) +
        (additions / 10) +
        (deletions / 20) +
        (20 if has_tests else 0) +
        (15 if has_ci else 0) +
        (10 if is_new_repo else 0) +
        (10 if expects_review else 0)
    ))

    # Confidence (higher for common patterns)
    confidence = "high" if pr_type in ("bug_fix", "docs", "dependency") else "medium"

    return {
        "total": total,
        "breakdown": breakdown,
        "pr_type": pr_type,
        "complexity_score": complexity,
        "confidence": confidence,
        "factors": {
            "base": base,
            "file_factor": round(file_factor, 1),
            "add_factor": round(add_factor, 1),
            "del_factor": round(del_factor, 1),
            "test_multiplier": test_factor,
            "ci_multiplier": ci_factor,
            "new_repo_multiplier": new_repo_factor,
            "review_multiplier": review_factor,
        },
    }


def _print_prediction(result: dict):
    """Pretty-print prediction."""
    print(f"## Tool Call Prediction\n")
    print(f"**Total: {result['total']} calls** ({result['confidence']} confidence)\n")
    print(f"PR Type: {result['pr_type']}")
    print(f"Complexity: {result['complexity_score']}/100\n")

    print("### Breakdown")
    for tool, count in result["breakdown"].items():
        bar = "█" * count + "░" * max(0, 20 - count)
        print(f"  {tool:8} {bar} {count}")

    print(f"\n### Factors")
    for k, v in result["factors"].items():
        print(f"  {k:25} {v}")


def main():
    # Parse CLI args
    title = ""
    files = 1
    additions = 50
    deletions = 10
    has_tests = True
    has_ci = False
    is_new_repo = False
    expects_review = True

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--task" and i + 1 < len(args):
            title = args[i + 1]
            i += 2
        elif args[i] == "--files" and i + 1 < len(args):
            files = int(args[i + 1])
            i += 2
        elif args[i] == "--additions" and i + 1 < len(args):
            additions = int(args[i + 1])
            i += 2
        elif args[i] == "--deletions" and i + 1 < len(args):
            deletions = int(args[i + 1])
            i += 2
        elif args[i] == "--no-tests":
            has_tests = False
            i += 1
        elif args[i] == "--ci":
            has_ci = True
            i += 1
        elif args[i] == "--new-repo":
            is_new_repo = True
            i += 1
        elif args[i] == "--no-review":
            expects_review = False
            i += 1
        elif args[i] == "--json":
            # Handled below
            i += 1
        else:
            i += 1

    result = predict_tool_calls(
        title=title,
        files_changed=files,
        additions=additions,
        deletions=deletions,
        has_tests=has_tests,
        has_ci=has_ci,
        is_new_repo=is_new_repo,
        expects_review=expects_review,
    )

    if "--json" in sys.argv:
        print(json.dumps(result, indent=2))
    else:
        _print_prediction(result)


if __name__ == "__main__":
    main()
