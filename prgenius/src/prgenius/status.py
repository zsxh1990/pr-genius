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

# Alert severity for transition alerts
_TRANSITION_SEVERITY = {
    ("WAITING", "NEEDS_REBASE"): "critical",
    ("WAITING", "CI_FAILING"): "critical",
    ("BLOCKED", "NEEDS_REBASE"): "critical",
    ("BLOCKED", "CI_FAILING"): "critical",
    ("STALE_REVIEW", "CLEAN"): "info",
    ("STALE_NO_REVIEW", "CLEAN"): "info",
    ("CHANGES_REQUESTED", "CLEAN"): "info",
}

# Recommended action per transition
_TRANSITION_ACTIONS = {
    ("WAITING", "NEEDS_REBASE"): "rebase / update branch",
    ("WAITING", "CI_FAILING"): "investigate CI failure",
    ("BLOCKED", "NEEDS_REBASE"): "rebase to unblock merge queue",
    ("BLOCKED", "CI_FAILING"): "fix CI to unblock",
    ("STALE_REVIEW", "CLEAN"): "ready for merge",
    ("STALE_NO_REVIEW", "CLEAN"): "ready for merge",
    ("CHANGES_REQUESTED", "CLEAN"): "re-request review",
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
        alert_key = (prev_status, curr_status)
        alert = alert_key in _TRANSITION_ALERTS
        severity = _TRANSITION_SEVERITY.get(alert_key) if alert else None

        entry = {
            "repo": pr["repo"],
            "number": pr["number"],
            "title": pr["title"],
            "previous_status": prev_status,
            "current_status": curr_status,
            "changed": changed,
            "alert": alert,
        }
        if severity:
            entry["severity"] = severity
        transitions.append(entry)

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


def format_transitions(transitions: list[dict]) -> str:
    """Format transition alerts as human-readable text with recommended actions."""
    alerts = [t for t in transitions if t.get("alert")]
    changes = [t for t in transitions if t.get("changed") and not t.get("alert")]

    if not alerts and not changes:
        return ""

    lines = ["🔄 TRANSITIONS"]

    for t in alerts:
        sev = t.get("severity", "")
        sev_icon = "🚨" if sev == "critical" else "ℹ️"
        key = (t["previous_status"], t["current_status"])
        action = _TRANSITION_ACTIONS.get(key, "")
        action_str = f" → {action}" if action else ""
        lines.append(f"  {sev_icon} {t['repo']} #{t['number']}: {t['previous_status']} → {t['current_status']} [{sev}]{action_str}")

    for t in changes:
        prev = t['previous_status'] or "NEW"
        lines.append(f"  · {t['repo']} #{t['number']}: {prev} → {t['current_status']}")

    lines.append("")
    return "\n".join(lines)


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
    if transitions:
        lines.append(format_transitions(transitions))

    # Actions
    actions = result.get("actions", [])
    if actions:
        lines.append(f"Action: {', '.join(actions)}")

    return "\n".join(lines)


def format_step_summary(result: dict) -> str:
    """Format status result as GitHub Step Summary markdown."""
    lines = []
    author = result.get("author", "")
    lines.append(f"## 🧬 PR Genius Status — {author}")
    lines.append(f"*{result['checked_at'][:10]} | stale_days={result['stale_days']} ({result['stale_days_source']})*")
    lines.append("")

    prs = result["prs"]
    ignored = result.get("ignored", [])
    summary = result.get("summary", {})
    transitions = result.get("transitions", [])
    alerts = [t for t in transitions if t.get("alert")]

    # Summary badges
    if summary:
        badges = []
        for status in PRStatus:
            key = status.value.lower()
            if key in summary:
                icon = STATUS_ICONS[status]
                badges.append(f"{icon} {summary[key]} {STATUS_LABELS[status]}")
        lines.append(" | ".join(badges))
        lines.append("")

    # Alerts (critical)
    if alerts:
        lines.append("### 🚨 Transition Alerts")
        lines.append("")
        lines.append("| PR | Previous | Current | Severity | Action |")
        lines.append("|-----|----------|---------|----------|--------|")
        for t in alerts:
            sev = t.get("severity", "")
            sev_icon = "🚨" if sev == "critical" else "ℹ️"
            prev = t["previous_status"] or "NEW"
            key = (t["previous_status"], t["current_status"])
            action = _TRANSITION_ACTIONS.get(key, "—")
            lines.append(f"| {t['repo']}#{t['number']} | {prev} | {t['current_status']} | {sev_icon} {sev} | {action} |")
        lines.append("")

    # PR table by status
    if prs:
        lines.append("### PRs")
        lines.append("")
        lines.append("| Status | PR | Title | Days |")
        lines.append("|--------|-----|-------|------|")
        for status in PRStatus:
            group = [p for p in prs if p["status"] == status.value]
            for pr in group:
                icon = STATUS_ICONS[status]
                days = pr.get("days_since_update", "?")
                lines.append(f"| {icon} {status.value} | {pr['repo']}#{pr['number']} | {pr['title'][:50]} | {days}d |")
        lines.append("")

    # Ignored
    if ignored:
        lines.append(f"⏭️ **{len(ignored)} own-repo PRs skipped**")
        lines.append("")

    # Actions
    actions = result.get("actions", [])
    if actions:
        lines.append("### 🎯 Recommended Actions")
        lines.append("")
        for a in actions:
            lines.append(f"- `{a}`")
        lines.append("")

    return "\n".join(lines)


def notify_webhook(result: dict, webhook_url: str, *, dry_run: bool = False) -> dict:
    """Send status result to a webhook (飞书/Slack/generic).

    Args:
        result: check_status() output
        webhook_url: webhook URL (飞书 bot, Slack incoming webhook, or generic)
        dry_run: if True, only return payload without sending

    Returns:
        {ok: bool, status_code: int, payload: dict}
    """
    import urllib.request
    import urllib.error

    transitions = result.get("transitions", [])
    alerts = [t for t in transitions if t.get("alert")]
    summary = result.get("summary", {})
    author = result.get("author", "")

    # Build summary line
    summary_parts = []
    for status in PRStatus:
        key = status.value.lower()
        if key in summary:
            summary_parts.append(f"{summary[key]} {status.value}")
    summary_str = ", ".join(summary_parts) if summary_parts else "no open PRs"

    # Build alert lines
    alert_lines = []
    for t in alerts:
        sev = t.get("severity", "")
        key = (t.get("previous_status"), t.get("current_status"))
        action = _TRANSITION_ACTIONS.get(key, "")
        alert_lines.append(f"{'🚨' if sev == 'critical' else 'ℹ️'} {t['repo']}#{t['number']}: {t['previous_status']} → {t['current_status']}")
        if action:
            alert_lines.append(f"  → {action}")

    # Detect webhook type from URL
    is_feishu = "feishu.cn" in webhook_url or "larksuite.com" in webhook_url
    is_slack = "hooks.slack.com" in webhook_url

    if is_feishu:
        # 飞书 bot message format
        content = f"**PR Genius Status — {author}**\n{summary_str}"
        if alert_lines:
            content += "\n\n**🚨 Alerts:**\n" + "\n".join(alert_lines)
        payload = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {"tag": "plain_text", "content": f"🧬 PR Genius — {author}"},
                    "template": "red" if alerts else "green",
                },
                "elements": [
                    {"tag": "markdown", "content": content},
                ],
            },
        }
    elif is_slack:
        # Slack incoming webhook format
        blocks = [
            {"type": "header", "text": {"type": "plain_text", "text": f"🧬 PR Genius — {author}"}},
            {"type": "section", "text": {"type": "mrkdwn", "text": summary_str}},
        ]
        if alert_lines:
            blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": "*🚨 Alerts:*\n" + "\n".join(alert_lines)}})
        payload = {"blocks": blocks}
    else:
        # Generic webhook
        payload = {
            "author": author,
            "summary": summary_str,
            "alerts": [
                {"repo": t["repo"], "number": t["number"],
                 "previous": t.get("previous_status"), "current": t["current_status"],
                 "severity": t.get("severity"), "action": _TRANSITION_ACTIONS.get((t.get("previous_status"), t["current_status"]), "")}
                for t in alerts
            ],
            "checked_at": result.get("checked_at"),
        }

    if dry_run:
        return {"ok": True, "status_code": 0, "payload": payload, "dry_run": True}

    try:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            webhook_url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return {"ok": True, "status_code": resp.status, "payload": payload}
    except urllib.error.HTTPError as e:
        return {"ok": False, "status_code": e.code, "error": str(e), "payload": payload}
    except Exception as e:
        return {"ok": False, "status_code": 0, "error": str(e), "payload": payload}


def format_step_summary_analyze(result: dict) -> str:
    """Format analyze result as GitHub Step Summary markdown."""
    lines = []
    tier = result.get("tier", "unknown")
    TIER_ICONS = {"low_risk": "🟢", "medium_risk": "🟡", "high_risk": "🔴"}
    TIER_LABELS = {"low_risk": "Low Risk", "medium_risk": "Medium Risk", "high_risk": "High Risk"}

    icon = TIER_ICONS.get(tier, "⚪")
    label = TIER_LABELS.get(tier, tier)
    repo = result.get("repo", "")

    lines.append(f"## {icon} PR Genius: {label}")
    lines.append(f"*{repo}*")
    lines.append("")

    signals = result.get("signals", {})

    # Negative signals
    if signals.get("negative"):
        lines.append("### ⚠️ Issues")
        lines.append("")
        for s in signals["negative"]:
            sev = s.get("severity", "")
            sev_icon = {"critical": "🚨", "high": "⚠️", "medium": "📋"}.get(sev, "•")
            lines.append(f"- {sev_icon} **{s['description']}**")
            if s.get("fix_action"):
                lines.append(f"  - → {s['fix_action']}")
        lines.append("")

    # Positive signals
    if signals.get("positive"):
        lines.append("### ✅ Positive")
        lines.append("")
        for s in signals["positive"]:
            lines.append(f"- {s['description']}")
        lines.append("")

    # Checklist
    checklist = result.get("checklist", [])
    if checklist:
        lines.append("### 📋 Checklist")
        lines.append("")
        for item in checklist:
            mark = "✅" if item["done"] else "☐"
            lines.append(f"- [{mark}] **[{item['priority']}]** {item['hint']}")
        lines.append("")

    return "\n".join(lines)


# ============================================================
# Profile Data Boundary & Writeback
# ============================================================

# Fields that can be shared publicly (schema + community knowledge)
PROFILE_PUBLIC_FIELDS = {
    "allow_unsolicited_pr", "require_signed_off", "require_cla",
    "require_issue_first", "ai_policy", "ai_assisted_disclosure",
    "maintainer_vibe", "bot_review", "ci_first_run_needs_approval",
    "default_branch", "stale_days_threshold", "max_pings",
    "abandon_after_days", "rebase_on_conflict", "one_pr_friendly",
    "close_keywords", "human_required_in",
}

# Fields that are private operational records (never auto-write)
PROFILE_PRIVATE_FIELDS = {
    "last_ping_at", "ping_count", "abandon_history",
    "pr_status_snapshots", "transition_log",
    "response_time_h_median", "external_merge_rate_30",
}


def suggest_profile_writeback(
    result: dict,
    repo_root: Optional[Path] = None,
    mode: str = "suggest",
) -> list[dict]:
    """Analyze PR status results and suggest profile updates.

    Args:
        result: check_status() output
        repo_root: path to pr-genius repo
        mode: 'suggest' (output only) or 'auto' (write if confidence >= 0.8)

    Returns list of writeback suggestions:
        [{field, value, repo, evidence, source, confidence}]
    """
    suggestions = []

    for pr in result.get("prs", []):
        repo = pr.get("repo", "")
        status = pr.get("status", "")

        # Detect CLA/DCO requirements from CI checks
        if status == "CI_FAILING":
            title_lower = pr.get("title", "").lower()
            # If we see CLA/DCO failures, suggest require_signed_off
            # (actual detection would need CI check details)
            pass

        # Detect maintainer response time from review patterns
        if pr.get("last_review_at") and pr.get("created_at"):
            try:
                from datetime import datetime as _dt
                created = _dt.fromisoformat(pr["created_at"].replace("Z", "+00:00"))
                reviewed = _dt.fromisoformat(pr["last_review_at"].replace("Z", "+00:00"))
                hours = (reviewed - created).total_seconds() / 3600
                if hours > 0:
                    suggestions.append({
                        "field": "response_time_h_median",
                        "value": round(hours),
                        "repo": repo,
                        "evidence": f"PR #{pr['number']} reviewed after {round(hours)}h",
                        "source": "status_snapshot",
                        "confidence": 0.6,  # single data point = low confidence
                        "private": True,
                    })
            except (ValueError, TypeError):
                pass

        # Detect stale_days from STALE_NO_REVIEW patterns
        if status == "STALE_NO_REVIEW" and pr.get("days_since_update", 0) > 21:
            suggestions.append({
                "field": "stale_days_threshold",
                "value": max(pr["days_since_update"] - 7, 14),
                "repo": repo,
                "evidence": f"PR #{pr['number']} stale for {pr['days_since_update']}d with no review",
                "source": "status_pattern",
                "confidence": 0.5,  # needs more data points
                "private": False,
            })

    # Filter by mode
    if mode == "auto":
        suggestions = [s for s in suggestions if s["confidence"] >= 0.8]

    return suggestions


def format_writeback_suggestions(suggestions: list[dict]) -> str:
    """Format writeback suggestions as human-readable text."""
    if not suggestions:
        return "No profile writeback suggestions."

    lines = ["Profile Writeback Suggestions (dry-run):", ""]
    for s in suggestions:
        privacy = "🔒 private" if s.get("private") else "🌐 public"
        lines.append(f"  {s['repo']}: {s['field']} = {s['value']}")
        lines.append(f"    evidence: {s['evidence']}")
        lines.append(f"    source: {s['source']} | confidence: {s['confidence']} | {privacy}")
        lines.append("")

    return "\n".join(lines)
