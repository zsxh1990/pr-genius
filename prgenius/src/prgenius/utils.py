"""Shared utilities for pr-genius scripts and CLI.

Extracted from scripts/coach_cases.py and scripts/daily_content_expand.py
to avoid code duplication.
"""

import json
import re
import subprocess
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def run_gh(args: list[str], timeout: int = 30) -> dict | list | None:
    """Run gh CLI and return JSON result."""
    cmd = ["gh"] + args
    if "--json" not in args:
        cmd += ["--json", "number,title,state,mergedAt,closedAt,author,createdAt,additions,deletions,changedFiles,reviews,comments,labels"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        pass
    return None


def fetch_recent_prs(repo: str, state: str = "all", limit: int = 10) -> list[dict]:
    """Fetch recent PRs from a repo using gh pr list."""
    try:
        result = subprocess.run(
            ["gh", "pr", "list", "--repo", repo, "--state", state,
             "--limit", str(limit), "--json",
             "number,title,state,mergedAt,closedAt,author,createdAt,additions,deletions,changedFiles,reviews,comments,labels,updatedAt"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout.strip():
            prs = json.loads(result.stdout)
            for pr in prs:
                pr["_repo"] = repo
            return prs
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        pass
    return []


def get_merge_rate(repo: str, repo_root: Optional[Path] = None) -> float:
    """Read external_merge_rate from repo profile."""
    root = repo_root or REPO_ROOT
    profile_dir = root / repo.replace("/", "-")
    index_file = profile_dir / "index.md"
    if not index_file.exists():
        return 0.0
    try:
        text = index_file.read_text()
        m = re.search(r'external_merge_rate:\s*([\d.]+)', text)
        return float(m.group(1)) if m else 0.0
    except (ValueError, AttributeError):
        return 0.0


def get_star_count(repo: str, repo_root: Optional[Path] = None) -> int:
    """Read star count from repo profile."""
    root = repo_root or REPO_ROOT
    profile_dir = root / repo.replace("/", "-")
    index_file = profile_dir / "index.md"
    if not index_file.exists():
        return 0
    try:
        text = index_file.read_text()
        m = re.search(r'^star:\s*(\d+)', text, re.MULTILINE)
        return int(m.group(1)) if m else 0
    except (ValueError, AttributeError):
        return 0


def classify_pr(pr: dict) -> str:
    """Classify PR into quality category."""
    state = pr.get("state", "").lower()
    merged = pr.get("mergedAt") is not None
    reviews = pr.get("reviews", [])
    comments = pr.get("comments", [])

    if merged:
        return "merged_success"
    elif state == "closed":
        comment_bodies = " ".join((c.get("body", "") or "").lower() for c in comments)
        if "duplicate" in comment_bodies:
            return "closed_duplicate"
        elif "already" in comment_bodies or "superseded" in comment_bodies:
            return "closed_already_done"
        else:
            return "closed_rejected"
    elif len(reviews) > 0:
        has_critical = any(
            (r.get("state", "") or "").lower() in ("changes_requested", "dismissed")
            for r in reviews
        )
        if has_critical:
            return "review_changes_requested"
        else:
            return "review_approved_pending"
    else:
        return "open_pending"


def extract_signals(pr: dict) -> dict:
    """Extract learning signals from a PR (text + metadata)."""
    body = pr.get("body", "") or ""
    title = pr.get("title", "") or ""
    title_lower = title.lower()
    body_lower = body.lower()

    files = pr.get("changedFiles", 0)
    additions = pr.get("additions", 0)
    deletions = pr.get("deletions", 0)
    total_changes = additions + deletions

    return {
        "has_issue_link": "fixes #" in body_lower or "closes #" in body_lower,
        "has_description": len(body) > 100,
        "has_test_mention": any(w in body_lower for w in ["test", "spec", "coverage"]),
        "has_breaking_change": any(w in title_lower for w in ["breaking", "major", "v2"]),
        "is_docs_only": any(w in title_lower for w in ["docs", "readme", "documentation", ".md"]),
        "is_bug_fix": any(w in title_lower for w in ["fix", "bug", "patch", "hotfix"]),
        "is_feature": any(w in title_lower for w in ["feat", "feature", "add", "support"]),
        "is_refactor": any(w in title_lower for w in ["refactor", "clean", "chore", "perf"]),
        "is_small_pr": files <= 3 and total_changes < 50,
        "is_large_pr": files > 10 or total_changes > 500,
        "is_backport": "backport" in title_lower or "release" in title_lower,
        "is_dependency_update": any(w in title_lower for w in ["bump", "update", "upgrade", "dependabot"]),
        "is_bot_pr": any(w in title_lower for w in ["dependabot", "renovate", "bot", "auto-", "[ci"]),
        "has_reviews": len(pr.get("reviews", [])) > 0,
        "has_comments": len(pr.get("comments", [])) > 0,
        "files_changed": files,
        "additions": additions,
        "deletions": deletions,
        "review_count": len(pr.get("reviews", [])),
        "comment_count": len(pr.get("comments", [])),
        "change_ratio": round(deletions / max(additions, 1), 2),
    }
