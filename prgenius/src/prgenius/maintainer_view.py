"""PR Genius — Maintainer view (v1.5.0)

Convert per-PR risk signals into a maintainer-facing action decision.

Persona = maintainer. Output answers one question:
    "What should I do with this PR right now?"

5 actions (克莱恩 2026-08-04 拍板):
- READY_FOR_REVIEW: DCO/audit/shape 绿, 可人工 review
- WAIT_FOR_AUTHOR: DCO/CI/requested changes, 等作者
- CLOSE_DUPLICATE: 明显重复或已有 clean-room absorption
- CLOSE_STALE_OR_RISKY: DCO failed + shape-risk / destructive rewrite
- HOLD_MAINTAINER_DECISION: workflow/core/security/roadmap, 需要 maintainer 判断

Shared with contributor view (v1.6.0): tier, signals.
Persona-specific: action, next_step (amend command), review_ready, blocking_signals.

read-only / advisory-only. Does not write GitHub, comment, label, close, or merge.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

from .evaluator import analyze_pr


class MaintainerAction(str, Enum):
    """5 类 maintainer 决策动作."""
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    WAIT_FOR_AUTHOR = "WAIT_FOR_AUTHOR"
    CLOSE_DUPLICATE = "CLOSE_DUPLICATE"
    CLOSE_STALE_OR_RISKY = "CLOSE_STALE_OR_RISKY"
    HOLD_MAINTAINER_DECISION = "HOLD_MAINTAINER_DECISION"


ACTION_ICONS = {
    MaintainerAction.READY_FOR_REVIEW: "✅",
    MaintainerAction.WAIT_FOR_AUTHOR: "⏸️",
    MaintainerAction.CLOSE_DUPLICATE: "🗑️",
    MaintainerAction.CLOSE_STALE_OR_RISKY: "🛑",
    MaintainerAction.HOLD_MAINTAINER_DECISION: "🤔",
}

ACTION_LABELS = {
    MaintainerAction.READY_FOR_REVIEW: "Ready for review",
    MaintainerAction.WAIT_FOR_AUTHOR: "Wait for author",
    MaintainerAction.CLOSE_DUPLICATE: "Suggested close (duplicate)",
    MaintainerAction.CLOSE_STALE_OR_RISKY: "Suggested close (stale/risky)",
    MaintainerAction.HOLD_MAINTAINER_DECISION: "Hold for maintainer decision",
}

ACTION_DESCRIPTIONS = {
    MaintainerAction.READY_FOR_REVIEW:
        "DCO/audit/shape checks pass. Author attached issue, signed off, "
        "and PR is within scope. Ready for human review.",
    MaintainerAction.WAIT_FOR_AUTHOR:
        "Author must address blocking signals before review. Common: "
        "DCO failed, CI failing, review requested changes not addressed.",
    MaintainerAction.CLOSE_DUPLICATE:
        "Existing PR or merged fix already covers this change. Close with "
        "reference to canonical PR.",
    MaintainerAction.CLOSE_STALE_OR_RISKY:
        "DCO failed + shape risk + destructive rewrite + no response > 14d. "
        "Suggest close with polite explanation.",
    MaintainerAction.HOLD_MAINTAINER_DECISION:
        "Workflow / core / security / roadmap change. Needs explicit "
        "maintainer signoff, not regular review.",
}


# Signal key patterns that route to specific actions
_BLOCKING_KEYWORDS_DCO = ["dco", "signed-off", "sign-off", "signoff"]
_BLOCKING_KEYWORDS_AUDIT = ["audit", "fossa", "license-check"]
_BLOCKING_KEYWORDS_SHAPE = ["shape", "destructive", "rewrite", "out-of-scope", "breaking"]
_BLOCKING_KEYWORDS_CI = ["ci", "check", "test", "build", "pipeline"]
_BLOCKING_KEYWORDS_DUPLICATE = ["duplicate", "already", "merged", "covered"]
_BLOCKING_KEYWORDS_STALE = ["stale", "abandon", "no response", "unmaintained"]
_BLOCKING_KEYWORDS_WORKFLOW = ["workflow", ".github/", "core", "security", "roadmap"]


def _signal_text(signal: dict) -> str:
    """Combine signal key + description for keyword matching."""
    parts = [
        signal.get("key", ""),
        signal.get("description", ""),
        signal.get("fix_action", ""),
    ]
    return " ".join(parts).lower()


def _signal_matches(signal: dict, keywords: list[str]) -> bool:
    """Check if any keyword appears in signal text."""
    text = _signal_text(signal)
    return any(kw in text for kw in keywords)


def _collect_blocking_items(analyze_result: dict) -> dict[str, list[dict]]:
    """Collect blocking items from BOTH negative signals AND P0/P1 checklist.

    analyze_pr 触发 DCO / sign-off / audit 之类的"action items"时是 P0 checklist hint,
    不是 negative signal. maintainer_view 必须把这两类都视为 blocking.
    """
    negative = analyze_result.get("signals", {}).get("negative", [])
    checklist = analyze_result.get("checklist", [])

    # 过滤掉 anti-pattern hit 类型的 negative signal. analyze_pr 把 PR body
    # 跟反模式库做模糊匹配, 命中会产 'key: anthropics-anthropic-sdk-python-1757'
    # 之类的 negative. 这是 contributor advisory (该避免的错误模式),
    # **不是 maintainer 阻塞** (除非命中点是 shape-risk / destructive rewrite
    # 之类硬约束). 把 anti-pattern hit 误当 blocking 会让 maintainer 误报.
    # heuristic: key 含 '-' 且 key 末尾是数字 PR# → 是 anti-pattern 库命中.
    import re as _re
    _ANTI_PATTERN_KEY = _re.compile(r"^[a-z0-9_-]+-\d+$")
    negative = [
        s for s in negative
        if not _ANTI_PATTERN_KEY.match(s.get("key", ""))
    ]

    # 把 P0/P1 checklist 转成跟 negative signal 兼容的 dict
    # 但过滤掉"未确认"类 informational step（如"确认 CI 通过"）—
    # 这些是 confirmation, 不是 fail signal. 当 caller 没传 CI 状态时,
    # 误把 confirm step 算成 blocking 会让所有 PR 都被路由成 WAIT_FOR_AUTHOR.
    _INFORMATIONAL_KEYWORDS = ["确认", "检查", "verify", "confirm", "check ", "review", "ensure"]
    checklist_as_sigs: list[dict] = []
    for item in checklist:
        if item.get("done", False):
            continue
        if item.get("priority") not in ("P0", "P1"):
            continue
        hint_lower = item.get("hint", "").lower()
        if any(kw in hint_lower for kw in _INFORMATIONAL_KEYWORDS):
            continue
        checklist_as_sigs.append({
            "key": item.get("action", "?"),
            "description": item.get("hint", ""),
            "severity": item.get("priority", "?").lower(),
            "fix_action": item.get("hint", ""),
            "source_pr": None,
        })

    all_items = negative + checklist_as_sigs

    return {
        "all": all_items,
        "dco": [s for s in all_items if _signal_matches(s, _BLOCKING_KEYWORDS_DCO)],
        "audit": [s for s in all_items if _signal_matches(s, _BLOCKING_KEYWORDS_AUDIT)],
        "ci": [s for s in all_items if _signal_matches(s, _BLOCKING_KEYWORDS_CI)],
        "shape": [s for s in all_items if _signal_matches(s, _BLOCKING_KEYWORDS_SHAPE)],
        "stale": [s for s in all_items if _signal_matches(s, _BLOCKING_KEYWORDS_STALE)],
        "duplicate": [s for s in all_items if _signal_matches(s, _BLOCKING_KEYWORDS_DUPLICATE)],
        "workflow": [s for s in all_items if _signal_matches(s, _BLOCKING_KEYWORDS_WORKFLOW)],
    }


def route_action(analyze_result: dict) -> tuple[MaintainerAction, str, list[str]]:
    """Map analyze_pr result → (action, reason, blocking_signals).

    Source of blocking items: BOTH negative signals AND P0/P1 checklist.
    Priority (high → low):
    1. HOLD_MAINTAINER_DECISION: workflow/core/security/roadmap change
    2. CLOSE_DUPLICATE: clear duplicate signal
    3. WAIT_FOR_AUTHOR: DCO / CI / requested changes (most common)
    4. CLOSE_STALE_OR_RISKY: DCO failed + shape risk + no response
    5. READY_FOR_REVIEW: all green
    """
    cats = _collect_blocking_items(analyze_result)
    negative = analyze_result.get("signals", {}).get("negative", [])
    blocking: list[str] = []

    # 1. HOLD — workflow/core/security/roadmap
    if cats["workflow"]:
        keys = [s.get("key", "?") for s in cats["workflow"]]
        return (
            MaintainerAction.HOLD_MAINTAINER_DECISION,
            f"Workflow/core/security/roadmap change — needs maintainer signoff",
            keys,
        )

    # 2. CLOSE_DUPLICATE
    if cats["duplicate"]:
        keys = [s.get("key", "?") for s in cats["duplicate"]]
        return (
            MaintainerAction.CLOSE_DUPLICATE,
            f"Duplicate or already-merged change detected",
            keys,
        )

    # Collect blocking signal keys
    blocking = [s.get("key", "?") for s in cats["dco"] + cats["audit"] + cats["ci"] + cats["shape"] + cats["stale"]]

    # 3. CLOSE_STALE_OR_RISKY — DCO failed AND shape-risk AND no author response
    if cats["dco"] and cats["shape"] and cats["stale"]:
        return (
            MaintainerAction.CLOSE_STALE_OR_RISKY,
            f"DCO failed + shape risk + stale (no author response)",
            blocking,
        )

    # 4. WAIT_FOR_AUTHOR — most common: DCO / CI / audit / shape
    if cats["dco"] or cats["audit"] or cats["ci"] or cats["shape"]:
        reasons = []
        if cats["dco"]:
            reasons.append("DCO check failed or P0 sign-off item open")
        if cats["audit"]:
            reasons.append("audit failure")
        if cats["ci"]:
            reasons.append("CI failing")
        if cats["shape"]:
            reasons.append("shape risk")
        return (
            MaintainerAction.WAIT_FOR_AUTHOR,
            f"Blocking signals: {', '.join(reasons)}",
            blocking,
        )

    # 5. READY_FOR_REVIEW
    return (
        MaintainerAction.READY_FOR_REVIEW,
        "All checks pass — ready for human review",
        [],
    )


def _build_next_step(action: MaintainerAction, blocking: list[str]) -> str:
    """Generate the maintainer's next-step command/ask."""
    if action == MaintainerAction.READY_FOR_REVIEW:
        return "Begin human review"
    if action == MaintainerAction.WAIT_FOR_AUTHOR:
        if any("dco" in b.lower() for b in blocking):
            return "Ask author to amend with: git commit --amend -s --no-edit && git push --force-with-lease"
        if any("ci" in b.lower() or "check" in b.lower() for b in blocking):
            return "Wait for author to fix CI; re-run status check after push"
        if any("audit" in b.lower() for b in blocking):
            return "Wait for author to address audit findings; re-run after push"
        return "Wait for author to address review feedback"
    if action == MaintainerAction.CLOSE_DUPLICATE:
        return "Close with reference to canonical PR (find via gh search prs)"
    if action == MaintainerAction.CLOSE_STALE_OR_RISKY:
        return "Close with polite explanation; link to CONTRIBUTING.md re-sign-off"
    if action == MaintainerAction.HOLD_MAINTAINER_DECISION:
        return "Ping core maintainers in maintainer channel for explicit signoff"
    return "Review manually"


@dataclass
class MaintainerView:
    """Maintainer-facing decision for one PR."""
    persona: str
    repo: str
    number: int
    title: str
    url: str
    author: str
    action: str
    reason: str
    blocking_signals: list[str]
    next_step: str
    review_ready: bool
    tier: str
    signals: dict
    generated_at: str


def maintainer_view(
    title: str,
    description: str,
    repo: str,
    body: str = "",
    labels: Optional[list[str]] = None,
    author: str = "",
    author_association: str = "NONE",
    star_count: int = 0,
    repo_merge_rate: float = 0.0,
    repo_root: Optional[Path] = None,
) -> dict:
    """Build a maintainer-facing decision for one PR.

    Returns dict with action, reason, blocking_signals, next_step, review_ready.
    Reuses analyze_pr for shared tier/signals.
    """
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[3]

    analysis = analyze_pr(
        title, description, repo, str(repo_root),
        body=body, labels=labels or [], author=author,
        star_count=star_count, repo_merge_rate=repo_merge_rate,
        author_association=author_association,
    )

    action, reason, blocking = route_action(analysis)
    next_step = _build_next_step(action, blocking)
    review_ready = action == MaintainerAction.READY_FOR_REVIEW

    return {
        "persona": "maintainer",
        "repo": repo,
        "title": title,
        "author": author,
        "action": action.value,
        "reason": reason,
        "blocking_signals": blocking,
        "next_step": next_step,
        "review_ready": review_ready,
        "context": {
            "tier": analysis.get("tier", "unknown"),
            "signals": analysis.get("signals", {}),
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


# ============================================================
# Review Queue Digest
# ============================================================

def _format_digest_md(results: list[dict], title: str = "Maintainer PR Review Queue") -> str:
    """Format maintainer_view results as a markdown digest grouped by action."""
    lines = [f"# {title}", ""]
    lines.append(f"_Generated: {datetime.now(timezone.utc).isoformat()}_")
    lines.append("")

    # Group by action
    grouped: dict[str, list[dict]] = {a.value: [] for a in MaintainerAction}
    for r in results:
        grouped.setdefault(r["action"], []).append(r)

    # Order by action enum
    for action in MaintainerAction:
        items = grouped.get(action.value, [])
        if not items:
            continue
        icon = ACTION_ICONS[action]
        label = ACTION_LABELS[action]
        desc = ACTION_DESCRIPTIONS[action]
        lines.append(f"## {icon} {action.value} — {label}")
        lines.append(f"_{desc}_")
        lines.append("")
        for item in items:
            blocking_str = ", ".join(item["blocking_signals"]) if item["blocking_signals"] else "none"
            lines.append(f"- **{item['repo']}#{item.get('number', '?')}** — {item.get('title', '?')[:80]}")
            lines.append(f"  - reason: {item['reason']}")
            lines.append(f"  - blocking: {blocking_str}")
            lines.append(f"  - next: {item['next_step']}")
            lines.append(f"  - tier: {item.get('context', {}).get('tier', '?')}")
            lines.append("")

    # Summary (always render, even when 0)
    total = len(results)
    summary_parts = [f"{len(grouped[a.value])} {a.value}" for a in MaintainerAction if grouped.get(a.value)]
    lines.append(f"## Summary")
    lines.append(f"Total open PRs: **{total}**")
    if summary_parts:
        for s in summary_parts:
            lines.append(f"- {s}")
    else:
        lines.append("- (no open PRs)")
    lines.append("")

    return "\n".join(lines)


def build_review_queue(
    prs: list[dict],
    repo_root: Optional[Path] = None,
) -> dict:
    """Build a review queue from a list of PR dicts.

    Each PR dict requires: repo, number, title, body, author, labels (optional).
    Returns dict with results (per-PR maintainer_view) + digest_md + summary.
    """
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[3]

    results = []
    for pr in prs:
        view = maintainer_view(
            title=pr.get("title", ""),
            description="",
            repo=pr.get("repo", ""),
            body=pr.get("body", ""),
            labels=pr.get("labels", []),
            author=pr.get("author", ""),
            author_association=pr.get("author_association", "NONE"),
            star_count=pr.get("star_count", 0),
            repo_merge_rate=pr.get("repo_merge_rate", 0.0),
            repo_root=repo_root,
        )
        view["number"] = pr.get("number")
        view["url"] = pr.get("url", "")
        results.append(view)

    digest = _format_digest_md(results)

    # Summary
    summary = {}
    for action in MaintainerAction:
        count = sum(1 for r in results if r["action"] == action.value)
        if count > 0:
            summary[action.value] = count

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total": len(results),
        "summary": summary,
        "results": results,
        "digest_markdown": digest,
    }


def write_review_queue_md(
    review_queue: dict,
    output_path: Path,
) -> Path:
    """Write the digest markdown to disk (git-trackable).

    Caller responsibility: opt-in via CLI flag (`--write-digest`).
    pr-genius never auto-writes.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(review_queue["digest_markdown"], encoding="utf-8")
    return output_path
