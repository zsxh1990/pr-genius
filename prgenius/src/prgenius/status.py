"""PR Genius status — in-flight PR health monitoring.

Checks all open PRs for a given author or repo and classifies each by health status.

Usage:
    python3 -m prgenius status --author zsxh1990
    python3 -m prgenius status --repo Ikalus1988/MisakaNet --format json
    python3 -m prgenius status --author zsxh1990 --stale-days 14
"""
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class PRStatus(str, Enum):
    """PR health status, ordered by priority (high → low)."""
    NEEDS_REBASE = "NEEDS_REBASE"
    CI_FAILING = "CI_FAILING"
    STALE_REVIEW = "STALE_REVIEW"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"
    STALE_NO_REVIEW = "STALE_NO_REVIEW"
    BLOCKED = "BLOCKED"
    CLEAN = "CLEAN"
    UNKNOWN = "UNKNOWN"
    WAITING = "WAITING"


STATUS_ICONS = {
    PRStatus.NEEDS_REBASE: "🔴",
    PRStatus.CI_FAILING: "🔴",
    PRStatus.STALE_REVIEW: "🟡",
    PRStatus.CHANGES_REQUESTED: "🔴",
    PRStatus.STALE_NO_REVIEW: "🟡",
    PRStatus.BLOCKED: "🟡",
    PRStatus.CLEAN: "🟢",
    PRStatus.UNKNOWN: "🟡",
    PRStatus.WAITING: "🟢",
}

STATUS_LABELS = {
    PRStatus.NEEDS_REBASE: "NEEDS_REBASE",
    PRStatus.CI_FAILING: "CI_FAILING",
    PRStatus.STALE_REVIEW: "STALE_REVIEW",
    PRStatus.CHANGES_REQUESTED: "CHANGES_REQUESTED",
    PRStatus.STALE_NO_REVIEW: "STALE_NO_REVIEW",
    PRStatus.BLOCKED: "BLOCKED",
    PRStatus.CLEAN: "CLEAN",
    PRStatus.UNKNOWN: "UNKNOWN",
    PRStatus.WAITING: "WAITING",
}

SUGGESTED_ACTIONS = {
    PRStatus.NEEDS_REBASE: "rebase and force push",
    PRStatus.CI_FAILING: "fix CI",
    PRStatus.STALE_REVIEW: "ping maintainer for re-review",
    PRStatus.CHANGES_REQUESTED: "address review feedback",
    PRStatus.STALE_NO_REVIEW: "ping or consider abandoning",
    PRStatus.BLOCKED: "wait for review/hooks/checks",
    PRStatus.CLEAN: "wait for maintainer to merge",
    PRStatus.UNKNOWN: "retry later or mark for review",
    PRStatus.WAITING: "continue waiting",
}


@dataclass
class PRInfo:
    """Raw PR data from GitHub API."""
    repo: str
    number: int
    title: str
    url: str
    author: str
    created_at: str
    updated_at: str
    mergeable: str  # MERGEABLE, CONFLICTING, UNKNOWN
    merge_state: str  # CLEAN, DIRTY, BEHIND, UNSTABLE, BLOCKED, HAS_HOOKS, UNKNOWN
    review_decision: str  # APPROVED, CHANGES_REQUESTED, REVIEW_REQUIRED, ""
    checks_status: str  # success, failure, pending, ""
    last_commit_at: str = ""
    last_review_at: str = ""
    is_own_repo: bool = False


@dataclass
class PRStatusResult:
    """Classified PR status with suggested action."""
    repo: str
    number: int
    title: str
    url: str
    status: PRStatus
    severity: str  # high, medium, low
    mergeable: str
    merge_state: str
    review_decision: str
    checks_status: str
    days_open: int
    days_since_update: int
    last_commit_at: str
    last_review_at: str
    suggested_action: str
    ignored_reason: str = ""


def _run_gh(args: list[str]) -> str:
    """Run gh CLI and return stdout."""
    result = subprocess.run(
        ["gh"] + args,
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args[:3])}... failed: {result.stderr.strip()}")
    return result.stdout


def _parse_datetime(s: str) -> Optional[datetime]:
    """Parse ISO datetime string."""
    if not s:
        return None
    try:
        # Handle GitHub's format: 2026-08-01T10:00:00Z
        s = s.replace("Z", "+00:00")
        return datetime.fromisoformat(s)
    except (ValueError, TypeError):
        return None


def _days_since(s: str) -> int:
    """Calculate days since a datetime string."""
    dt = _parse_datetime(s)
    if not dt:
        return 0
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return max(0, (now - dt).days)


def fetch_open_prs(author: Optional[str] = None, repo: Optional[str] = None) -> list[PRInfo]:
    """Fetch open PRs from GitHub using gh CLI."""
    args = ["search", "prs", "--state=open", "--json", "repository,number,title,url,author,createdAt,updatedAt", "--limit", "50"]
    if author:
        args.extend(["--author", author])
    if repo:
        args.extend(["--repo", repo])

    raw = _run_gh(args)
    prs_basic = json.loads(raw)

    results = []
    for pr in prs_basic:
        repo_name = pr["repository"]["nameWithOwner"]
        number = pr["number"]

        # Get detailed PR info
        try:
            detail_raw = _run_gh([
                "pr", "view", str(number),
                "--repo", repo_name,
                "--json", "mergeable,mergeStateStatus,reviewDecision,state,createdAt,updatedAt,commits,reviews",
            ])
            detail = json.loads(detail_raw)
        except RuntimeError:
            detail = {}

        # Extract last commit time
        last_commit_at = ""
        commits = detail.get("commits", [])
        if commits:
            last_commit = commits[-1]
            last_commit_at = last_commit.get("committedDate", "") or last_commit.get("oid", "")

        # Extract last review time
        last_review_at = ""
        reviews = detail.get("reviews", [])
        if reviews:
            last_review = reviews[-1]
            last_review_at = last_review.get("submittedAt", "")

        # Determine if own repo
        is_own_repo = False
        if author:
            repo_owner = repo_name.split("/")[0].lower()
            is_own_repo = repo_owner == author.lower()

        checks_status = ""
        # Try to get check status
        try:
            checks_raw = _run_gh([
                "pr", "checks", str(number),
                "--repo", repo_name,
                "--json", "name,bucket",
            ])
            checks = json.loads(checks_raw)
            if any(c.get("bucket") == "failure" for c in checks):
                checks_status = "failure"
            elif any(c.get("bucket") == "pending" for c in checks):
                checks_status = "pending"
            elif all(c.get("bucket") == "success" for c in checks):
                checks_status = "success"
        except RuntimeError:
            pass

        results.append(PRInfo(
            repo=repo_name,
            number=number,
            title=pr["title"],
            url=pr["url"],
            author=author or "",
            created_at=pr.get("createdAt", ""),
            updated_at=pr.get("updatedAt", ""),
            mergeable=detail.get("mergeable", "UNKNOWN"),
            merge_state=detail.get("mergeStateStatus", "UNKNOWN"),
            review_decision=detail.get("reviewDecision", ""),
            checks_status=checks_status,
            last_commit_at=last_commit_at,
            last_review_at=last_review_at,
            is_own_repo=is_own_repo,
        ))

    return results


def classify_pr(pr: PRInfo, stale_days: int = 14) -> PRStatusResult:
    """Classify a PR's health status based on priority rules.

    Priority order (high → low):
    1. NEEDS_REBASE: CONFLICTING or DIRTY or BEHIND
    2. CI_FAILING: checks failure or UNSTABLE
    3. STALE_REVIEW: last_commit_at > last_review_at, stale, last_review_at != null
    4. CHANGES_REQUESTED: reviewDecision=CHANGES_REQUESTED
    5. STALE_NO_REVIEW: stale and no reviews
    6. BLOCKED: BLOCKED, HAS_HOOKS, PENDING checks
    7. CLEAN: MERGEABLE, CLEAN, APPROVED
    8. UNKNOWN: mergeable=UNKNOWN
    9. WAITING: residual fallback
    """
    days_open = _days_since(pr.created_at)
    days_since_update = _days_since(pr.updated_at)

    # Own repo → ignore
    if pr.is_own_repo:
        return PRStatusResult(
            repo=pr.repo, number=pr.number, title=pr.title, url=pr.url,
            status=PRStatus.WAITING, severity="low",
            mergeable=pr.mergeable, merge_state=pr.merge_state,
            review_decision=pr.review_decision, checks_status=pr.checks_status,
            days_open=days_open, days_since_update=days_since_update,
            last_commit_at=pr.last_commit_at, last_review_at=pr.last_review_at,
            suggested_action="ignored",
            ignored_reason="OWN_REPO",
        )

    # 1. NEEDS_REBASE
    if pr.mergeable == "CONFLICTING" or pr.merge_state in ("DIRTY", "BEHIND"):
        return PRStatusResult(
            repo=pr.repo, number=pr.number, title=pr.title, url=pr.url,
            status=PRStatus.NEEDS_REBASE, severity="high",
            mergeable=pr.mergeable, merge_state=pr.merge_state,
            review_decision=pr.review_decision, checks_status=pr.checks_status,
            days_open=days_open, days_since_update=days_since_update,
            last_commit_at=pr.last_commit_at, last_review_at=pr.last_review_at,
            suggested_action=SUGGESTED_ACTIONS[PRStatus.NEEDS_REBASE],
        )

    # 2. CI_FAILING
    if pr.checks_status == "failure" or pr.merge_state == "UNSTABLE":
        return PRStatusResult(
            repo=pr.repo, number=pr.number, title=pr.title, url=pr.url,
            status=PRStatus.CI_FAILING, severity="high",
            mergeable=pr.mergeable, merge_state=pr.merge_state,
            review_decision=pr.review_decision, checks_status=pr.checks_status,
            days_open=days_open, days_since_update=days_since_update,
            last_commit_at=pr.last_commit_at, last_review_at=pr.last_review_at,
            suggested_action=SUGGESTED_ACTIONS[PRStatus.CI_FAILING],
        )

    # 3. STALE_REVIEW
    # Condition: last_commit_at > last_review_at AND days since commit > stale_days AND last_review_at != null
    if pr.last_review_at and pr.last_commit_at:
        days_since_commit = _days_since(pr.last_commit_at)
        commit_dt = _parse_datetime(pr.last_commit_at)
        review_dt = _parse_datetime(pr.last_review_at)
        if commit_dt and review_dt and commit_dt > review_dt and days_since_commit > stale_days:
            return PRStatusResult(
                repo=pr.repo, number=pr.number, title=pr.title, url=pr.url,
                status=PRStatus.STALE_REVIEW, severity="medium",
                mergeable=pr.mergeable, merge_state=pr.merge_state,
                review_decision=pr.review_decision, checks_status=pr.checks_status,
                days_open=days_open, days_since_update=days_since_update,
                last_commit_at=pr.last_commit_at, last_review_at=pr.last_review_at,
                suggested_action=SUGGESTED_ACTIONS[PRStatus.STALE_REVIEW],
            )

    # 4. CHANGES_REQUESTED
    if pr.review_decision == "CHANGES_REQUESTED":
        return PRStatusResult(
            repo=pr.repo, number=pr.number, title=pr.title, url=pr.url,
            status=PRStatus.CHANGES_REQUESTED, severity="high",
            mergeable=pr.mergeable, merge_state=pr.merge_state,
            review_decision=pr.review_decision, checks_status=pr.checks_status,
            days_open=days_open, days_since_update=days_since_update,
            last_commit_at=pr.last_commit_at, last_review_at=pr.last_review_at,
            suggested_action=SUGGESTED_ACTIONS[PRStatus.CHANGES_REQUESTED],
        )

    # 5. STALE_NO_REVIEW
    if not pr.last_review_at and days_since_update > stale_days:
        return PRStatusResult(
            repo=pr.repo, number=pr.number, title=pr.title, url=pr.url,
            status=PRStatus.STALE_NO_REVIEW, severity="medium",
            mergeable=pr.mergeable, merge_state=pr.merge_state,
            review_decision=pr.review_decision, checks_status=pr.checks_status,
            days_open=days_open, days_since_update=days_since_update,
            last_commit_at=pr.last_commit_at, last_review_at=pr.last_review_at,
            suggested_action=SUGGESTED_ACTIONS[PRStatus.STALE_NO_REVIEW],
        )

    # 6. BLOCKED
    if pr.merge_state in ("BLOCKED", "HAS_HOOKS") or pr.checks_status == "pending":
        return PRStatusResult(
            repo=pr.repo, number=pr.number, title=pr.title, url=pr.url,
            status=PRStatus.BLOCKED, severity="medium",
            mergeable=pr.mergeable, merge_state=pr.merge_state,
            review_decision=pr.review_decision, checks_status=pr.checks_status,
            days_open=days_open, days_since_update=days_since_update,
            last_commit_at=pr.last_commit_at, last_review_at=pr.last_review_at,
            suggested_action=SUGGESTED_ACTIONS[PRStatus.BLOCKED],
        )

    # 7. CLEAN
    if pr.mergeable == "MERGEABLE" and pr.merge_state == "CLEAN" and pr.review_decision == "APPROVED":
        return PRStatusResult(
            repo=pr.repo, number=pr.number, title=pr.title, url=pr.url,
            status=PRStatus.CLEAN, severity="low",
            mergeable=pr.mergeable, merge_state=pr.merge_state,
            review_decision=pr.review_decision, checks_status=pr.checks_status,
            days_open=days_open, days_since_update=days_since_update,
            last_commit_at=pr.last_commit_at, last_review_at=pr.last_review_at,
            suggested_action=SUGGESTED_ACTIONS[PRStatus.CLEAN],
        )

    # 8. UNKNOWN
    if pr.mergeable == "UNKNOWN" or pr.merge_state == "UNKNOWN":
        return PRStatusResult(
            repo=pr.repo, number=pr.number, title=pr.title, url=pr.url,
            status=PRStatus.UNKNOWN, severity="medium",
            mergeable=pr.mergeable, merge_state=pr.merge_state,
            review_decision=pr.review_decision, checks_status=pr.checks_status,
            days_open=days_open, days_since_update=days_since_update,
            last_commit_at=pr.last_commit_at, last_review_at=pr.last_review_at,
            suggested_action=SUGGESTED_ACTIONS[PRStatus.UNKNOWN],
        )

    # 9. WAITING (residual fallback)
    return PRStatusResult(
        repo=pr.repo, number=pr.number, title=pr.title, url=pr.url,
        status=PRStatus.WAITING, severity="low",
        mergeable=pr.mergeable, merge_state=pr.merge_state,
        review_decision=pr.review_decision, checks_status=pr.checks_status,
        days_open=days_open, days_since_update=days_since_update,
        last_commit_at=pr.last_commit_at, last_review_at=pr.last_review_at,
        suggested_action=SUGGESTED_ACTIONS[PRStatus.WAITING],
    )


def check_status(
    author: Optional[str] = None,
    repo: Optional[str] = None,
    stale_days: int = 14,
) -> dict:
    """Main entry point: fetch PRs, classify, return structured result."""
    prs = fetch_open_prs(author=author, repo=repo)

    classified = []
    ignored = []
    for pr in prs:
        result = classify_pr(pr, stale_days=stale_days)
        if result.ignored_reason:
            ignored.append(result)
        else:
            classified.append(result)

    # Sort by priority (status enum order)
    status_order = list(PRStatus)
    classified.sort(key=lambda r: status_order.index(r.status))

    # Build summary
    summary = {}
    for s in PRStatus:
        count = sum(1 for r in classified if r.status == s)
        if count > 0:
            summary[s.value.lower()] = count

    # Build action list
    actions = []
    for r in classified:
        if r.severity in ("high", "medium"):
            actions.append(f"{r.suggested_action} {r.repo}#{r.number}")

    return {
        "author": author,
        "repo": repo,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "stale_days": stale_days,
        "prs": [asdict(r) for r in classified],
        "ignored": [asdict(r) for r in ignored],
        "summary": summary,
        "actions": actions,
    }


def format_table(result: dict) -> str:
    """Format status result as human-readable table."""
    lines = []
    author = result.get("author", "")
    header = f"PR Genius Status — {author}" if author else "PR Genius Status"
    lines.append(f"{header} ({result['checked_at'][:10]})")
    lines.append("")

    prs = result["prs"]
    ignored = result.get("ignored", [])

    # Group by status
    grouped = {}
    for pr in prs:
        status = pr["status"]
        if status not in grouped:
            grouped[status] = []
        grouped[status].append(pr)

    # Print in priority order
    for status in PRStatus:
        if status.value not in grouped:
            continue
        icon = STATUS_ICONS[status]
        label = STATUS_LABELS[status]
        lines.append(f"{icon} {label}")
        for pr in grouped[status.value]:
            extra = f" ({pr['days_since_update']}d since update)"
            lines.append(f"  {pr['repo']} #{pr['number']} — {pr['title']}{extra}")
        lines.append("")

    # Ignored
    if ignored:
        lines.append("⏭️ IGNORED (OWN_REPO)")
        for pr in ignored:
            lines.append(f"  {pr['repo']} #{pr['number']} — {pr['title']}")
        lines.append("")

    # Summary
    summary = result["summary"]
    summary_parts = []
    for status in PRStatus:
        key = status.value.lower()
        if key in summary:
            summary_parts.append(f"{summary[key]} {STATUS_LABELS[status]}")
    lines.append(f"Summary: {', '.join(summary_parts)}")

    # Actions
    actions = result.get("actions", [])
    if actions:
        lines.append(f"Action: {', '.join(actions)}")

    return "\n".join(lines)
