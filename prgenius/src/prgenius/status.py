"""PR Genius status — in-flight PR health monitoring.

Checks all open PRs for a given author or repo and classifies each by health status.

Usage:
    python3 -m prgenius status --author zsxh1990
    python3 -m prgenius status --repo Ikalus1988/MisakaNet --format json
    python3 -m prgenius status --author zsxh1990 --stale-days 14
"""
from __future__ import annotations

import glob
import json
import subprocess
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

from .parser import profile_get

DEFAULT_STALE_DAYS = 14


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


_GRAPHQL_QUERY = """query {
  search(query: "SEARCH_QUERY", type: ISSUE, first: 50) {
    nodes {
      ... on PullRequest {
        number
        title
        url
        repository { nameWithOwner }
        author { login }
        createdAt
        updatedAt
        mergeable
        mergeStateStatus
        reviewDecision
        commits(last: 1) {
          nodes { commit { committedDate } }
        }
        reviews(last: 1) {
          nodes { submittedAt state }
        }
        statusCheckRollup { state }
      }
    }
  }
}"""


def _build_search_query(author: Optional[str] = None, repo: Optional[str] = None) -> str:
    """Build GitHub search query string."""
    parts = ["is:pr", "is:open"]
    if author:
        parts.append(f"author:{author}")
    if repo:
        parts.append(f"repo:{repo}")
    return " ".join(parts)


def _map_check_state(state: Optional[str]) -> str:
    """Map GraphQL statusCheckRollup.state to checks_status."""
    if not state:
        return ""
    state = state.upper()
    if state == "FAILURE":
        return "failure"
    if state in ("PENDING", "EXPECTED"):
        return "pending"
    if state == "SUCCESS":
        return "success"
    return ""


def fetch_open_prs(author: Optional[str] = None, repo: Optional[str] = None) -> list[PRInfo]:
    """Fetch open PRs from GitHub using a single GraphQL query."""
    search_query = _build_search_query(author, repo)
    query = _GRAPHQL_QUERY.replace("SEARCH_QUERY", search_query.replace('"', '\\"'))

    raw = _run_gh(["api", "graphql", "-f", f"query={query}"])
    data = json.loads(raw)
    nodes = data.get("data", {}).get("search", {}).get("nodes", [])

    results = []
    for pr in nodes:
        repo_name = pr["repository"]["nameWithOwner"]

        # Extract last commit time
        last_commit_at = ""
        commits = pr.get("commits", {}).get("nodes", [])
        if commits:
            last_commit_at = commits[-1].get("commit", {}).get("committedDate", "")

        # Extract last review time
        last_review_at = ""
        reviews = pr.get("reviews", {}).get("nodes", [])
        if reviews:
            last_review_at = reviews[-1].get("submittedAt", "")

        # Determine if own repo
        is_own_repo = False
        if author:
            repo_owner = repo_name.split("/")[0].lower()
            is_own_repo = repo_owner == author.lower()

        # Map statusCheckRollup
        rollup = pr.get("statusCheckRollup")
        checks_status = _map_check_state(rollup.get("state") if rollup else None)

        # Map reviewDecision (null → "")
        review_decision = pr.get("reviewDecision") or ""

        results.append(PRInfo(
            repo=repo_name,
            number=pr["number"],
            title=pr["title"],
            url=pr["url"],
            author=pr.get("author", {}).get("login", ""),
            created_at=pr.get("createdAt", ""),
            updated_at=pr.get("updatedAt", ""),
            mergeable=pr.get("mergeable", "UNKNOWN"),
            merge_state=pr.get("mergeStateStatus", "UNKNOWN"),
            review_decision=review_decision,
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


def _resolve_stale_days(
    repo: str,
    cli_stale_days: Optional[int] = None,
    repo_root: Optional[Path] = None,
) -> tuple[int, str]:
    """Resolve stale_days threshold with priority: CLI > profile > default.

    Returns (stale_days, source) where source is 'cli', 'profile', or 'default'.
    """
    # 1. CLI parameter takes priority
    if cli_stale_days is not None:
        return cli_stale_days, "cli"

    # 2. Try repo profile
    if repo_root:
        try:
            profile = profile_get(str(repo_root), repo)
            if profile:
                guidelines = profile.get("frontmatter", {}).get("agent_guidelines", {})
                threshold = guidelines.get("stale_days_threshold")
                if threshold is not None:
                    return int(threshold), "profile"
        except Exception:
            pass

    # 3. Default
    return DEFAULT_STALE_DAYS, "default"


def _load_profile_stale_days(repos: set[str], repo_root: Optional[Path]) -> dict[str, int]:
    """Load stale_days_threshold for all unique repos from profiles."""
    result = {}
    if not repo_root:
        return result
    for repo in repos:
        try:
            profile = profile_get(str(repo_root), repo)
            if profile:
                guidelines = profile.get("frontmatter", {}).get("agent_guidelines", {})
                threshold = guidelines.get("stale_days_threshold")
                if threshold is not None:
                    result[repo] = int(threshold)
        except Exception:
            pass
    return result


# ============================================================
# Snapshot & Transition tracking
# ============================================================

# Status changes that warrant a transition alert
_TRANSITION_ALERTS = {
    # Escalations: WAITING/BLOCKED → critical
    ("WAITING", "NEEDS_REBASE"),
    ("WAITING", "CI_FAILING"),
    ("BLOCKED", "NEEDS_REBASE"),
    ("BLOCKED", "CI_FAILING"),
    # De-escalations: STALE_* → resolved
    ("STALE_REVIEW", "CLEAN"),
    ("STALE_NO_REVIEW", "CLEAN"),
    ("CHANGES_REQUESTED", "CLEAN"),
}


def _find_latest_snapshot(snapshot_dir: Path) -> Optional[Path]:
    """Find the most recent snapshot file in the directory."""
    pattern = str(snapshot_dir / "*.json")
    files = sorted(glob.glob(pattern), reverse=True)
    for f in files:
        # Skip non-snapshot files (e.g. graphql test snapshots)
        name = Path(f).name
        if name[0:4].isdigit() and len(name) >= 14:  # YYYY-MM-DD*.json
            return Path(f)
    return None


def _load_previous_snapshot(snapshot_dir: Path) -> Optional[dict]:
    """Load the most recent snapshot for comparison."""
    path = _find_latest_snapshot(snapshot_dir)
    if not path:
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _build_pr_key(pr: dict) -> str:
    """Build a unique key for a PR: repo#number."""
    return f"{pr['repo']}#{pr['number']}"


def _compute_transitions(current: dict, previous: Optional[dict]) -> list[dict]:
    """Compare current vs previous snapshot, return transition list.

    Each transition: {repo, number, title, previous_status, current_status, changed, alert}
    """
    if not previous:
        return []

    # Build lookup from previous snapshot
    prev_lookup = {}
    for pr in previous.get("prs", []):
        key = _build_pr_key(pr)
        prev_lookup[key] = pr

    transitions = []
    for pr in current.get("prs", []):
        key = _build_pr_key(pr)
        prev = prev_lookup.get(key)

        if not prev:
            # New PR (wasn't in previous snapshot)
            transitions.append({
                "repo": pr["repo"],
                "number": pr["number"],
                "title": pr["title"],
                "previous_status": None,
                "current_status": pr["status"],
                "changed": True,
                "alert": False,
            })
            continue

        prev_status = prev.get("status")
        curr_status = pr["status"]
        changed = prev_status != curr_status
        alert = (prev_status, curr_status) in _TRANSITION_ALERTS

        transitions.append({
            "repo": pr["repo"],
            "number": pr["number"],
            "title": pr["title"],
            "previous_status": prev_status,
            "current_status": curr_status,
            "changed": changed,
            "alert": alert,
        })

    # Check for PRs that disappeared (merged/closed)
    curr_keys = {_build_pr_key(pr) for pr in current.get("prs", [])}
    for key, pr in prev_lookup.items():
        if key not in curr_keys:
            transitions.append({
                "repo": pr["repo"],
                "number": pr["number"],
                "title": pr["title"],
                "previous_status": pr.get("status"),
                "current_status": "CLOSED_OR_MERGED",
                "changed": True,
                "alert": False,
            })

    return transitions


def _save_snapshot(result: dict, snapshot_dir: Path) -> Path:
    """Save current result as a snapshot file."""
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.json"
    path = snapshot_dir / filename
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def check_status(
    author: Optional[str] = None,
    repo: Optional[str] = None,
    stale_days: Optional[int] = None,
    repo_root: Optional[Path] = None,
    save_snapshot: bool = False,
    snapshot_dir: Optional[Path] = None,
) -> dict:
    """Main entry point: fetch PRs, classify, return structured result.

    Priority: CLI stale_days > repo profile stale_days_threshold > default 14.
    If save_snapshot=True, saves result and computes transitions from previous snapshot.
    """
    prs = fetch_open_prs(author=author, repo=repo)

    # Resolve stale_days per repo
    unique_repos = {pr.repo for pr in prs if not pr.is_own_repo}
    profile_thresholds = _load_profile_stale_days(unique_repos, repo_root)

    # Determine overall stale_days and source for output
    if stale_days is not None:
        effective_stale_days = stale_days
        stale_days_source = "cli"
    elif profile_thresholds:
        # Use the first profile threshold found (most common case: single repo)
        effective_stale_days = next(iter(profile_thresholds.values()))
        stale_days_source = "profile"
    else:
        effective_stale_days = DEFAULT_STALE_DAYS
        stale_days_source = "default"

    classified = []
    ignored = []
    for pr in prs:
        # Per-PR stale_days (profile may differ per repo)
        pr_stale_days = stale_days or profile_thresholds.get(pr.repo, DEFAULT_STALE_DAYS)
        result = classify_pr(pr, stale_days=pr_stale_days)
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

    result = {
        "author": author,
        "repo": repo,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "stale_days": effective_stale_days,
        "stale_days_source": stale_days_source,
        "profile": {
            "stale_days_threshold": effective_stale_days,
            "stale_days_source": stale_days_source,
        },
        "prs": [asdict(r) for r in classified],
        "ignored": [asdict(r) for r in ignored],
        "summary": summary,
        "actions": actions,
    }

    # Snapshot & transition tracking
    if save_snapshot:
        if snapshot_dir is None:
            snapshot_dir = Path("data/status-snapshots")
        previous = _load_previous_snapshot(snapshot_dir)
        transitions = _compute_transitions(result, previous)
        result["transitions"] = transitions
        result["transition_summary"] = {
            "total": len(transitions),
            "changed": sum(1 for t in transitions if t["changed"]),
            "alerts": sum(1 for t in transitions if t["alert"]),
        }
        _save_snapshot(result, snapshot_dir)

    return result


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

    # Transitions
    transitions = result.get("transitions", [])
    alerts = [t for t in transitions if t.get("alert")]
    changes = [t for t in transitions if t.get("changed") and not t.get("alert")]
    if alerts or changes:
        lines.append("🔄 TRANSITIONS")
        for t in alerts:
            lines.append(f"  ⚠️ {t['repo']} #{t['number']}: {t['previous_status']} → {t['current_status']}")
        for t in changes:
            prev = t['previous_status'] or "NEW"
            lines.append(f"  · {t['repo']} #{t['number']}: {prev} → {t['current_status']}")
        lines.append("")

    # Actions
    actions = result.get("actions", [])
    if actions:
        lines.append(f"Action: {', '.join(actions)}")

    return "\n".join(lines)
