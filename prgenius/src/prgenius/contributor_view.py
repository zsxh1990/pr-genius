"""PR Genius — Contributor view (v1.6.0)

Convert per-PR risk signals into a contributor-facing action decision.

Persona = contributor. Output answers one question:
    "Is my PR ready to submit? What should I fix?"

5 actions (mirror maintainer view, contributor perspective):
- READY_TO_SUBMIT: No blocking issues, safe to open PR
- FIX_BEFORE_SUBMIT: Blocking signals must be addressed
- NEEDS_DISCUSSION: Breaking change / core / security — discuss first
- IMPROVE_CHANCE: Not blocking but could be improved
- ASK_MAINTAINER: Unclear — ask maintainer for guidance

Shared with maintainer view (v1.5.0): tier, signals, impact, review, author_info.
Persona-specific: action, next_step, checklist, confidence.

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
from .pr_metadata import assess_impact, assess_review_complexity


class ContributorAction(str, Enum):
    """5 类 contributor 决策动作."""
    READY_TO_SUBMIT = "READY_TO_SUBMIT"
    FIX_BEFORE_SUBMIT = "FIX_BEFORE_SUBMIT"
    NEEDS_DISCUSSION = "NEEDS_DISCUSSION"
    IMPROVE_CHANCE = "IMPROVE_CHANCE"
    ASK_MAINTAINER = "ASK_MAINTAINER"


ACTION_ICONS = {
    ContributorAction.READY_TO_SUBMIT: "✅",
    ContributorAction.FIX_BEFORE_SUBMIT: "🔧",
    ContributorAction.NEEDS_DISCUSSION: "💬",
    ContributorAction.IMPROVE_CHANCE: "📈",
    ContributorAction.ASK_MAINTAINER: "❓",
}

ACTION_LABELS = {
    ContributorAction.READY_TO_SUBMIT: "Ready to submit",
    ContributorAction.FIX_BEFORE_SUBMIT: "Fix before submitting",
    ContributorAction.NEEDS_DISCUSSION: "Discuss first",
    ContributorAction.IMPROVE_CHANCE: "Improve your chances",
    ContributorAction.ASK_MAINTAINER: "Ask maintainer",
}

ACTION_DESCRIPTIONS = {
    ContributorAction.READY_TO_SUBMIT:
        "No blocking issues found. PR is ready to submit.",
    ContributorAction.FIX_BEFORE_SUBMIT:
        "Blocking signals detected. Fix these before submitting.",
    ContributorAction.NEEDS_DISCUSSION:
        "Breaking change / core / security. Open an issue first to discuss.",
    ContributorAction.IMPROVE_CHANCE:
        "Not blocking, but improvements could increase merge probability.",
    ContributorAction.ASK_MAINTAINER:
        "Unclear situation. Ask maintainer for guidance.",
}


def _signal_matches(signal: dict, keywords: list[str]) -> bool:
    """Check if a signal matches any of the given keywords."""
    key = signal.get("key", "").lower()
    desc = signal.get("description", "").lower()
    return any(kw in key or kw in desc for kw in keywords)


def _collect_blocking_items(analysis: dict) -> dict[str, list[dict]]:
    """Collect blocking items from analysis signals."""
    signals = analysis.get("signals", {})
    blocking = {
        "critical": [],
        "high": [],
        "medium": [],
    }

    for signal in signals.get("negative", []):
        severity = signal.get("severity", "medium")
        if severity in blocking:
            blocking[severity].append(signal)

    return blocking


def _build_checklist(analysis: dict, impact) -> list[dict]:
    """Build a checklist of items to address."""
    checklist = []

    # DCO/signoff
    signals = analysis.get("signals", {})
    for s in signals.get("neutral", []):
        if _signal_matches(s, ["dco", "signoff", "signed-off"]):
            checklist.append({
                "item": "Add DCO sign-off",
                "command": "git commit --amend -s --no-edit",
                "priority": "P0",
            })

    # Issue link
    has_issue = any(
        _signal_matches(s, ["issue_linked", "fixes", "closes"])
        for s in signals.get("positive", [])
    )
    if not has_issue:
        checklist.append({
            "item": "Link an issue",
            "command": "Add 'Fixes #NNN' to PR body",
            "priority": "P1",
        })

    # Breaking change
    if impact.breaking_change:
        checklist.append({
            "item": "Provide migration path for breaking change",
            "command": "Add migration guide or deprecation notice",
            "priority": "P0",
        })

    # Security sensitive
    if impact.security_sensitive:
        checklist.append({
            "item": "Security review required",
            "command": "Wait for maintainer security review",
            "priority": "P0",
        })

    # Tests
    if "tests" not in impact.scope:
        checklist.append({
            "item": "Add tests",
            "command": "Add test coverage for changes",
            "priority": "P1",
        })

    return checklist


def route_action(analysis: dict, impact) -> tuple[ContributorAction, str]:
    """Route analysis to a contributor action."""
    blocking = _collect_blocking_items(analysis)
    signals = analysis.get("signals", {})
    tier = analysis.get("tier", "unknown")

    # Critical blocking → FIX_BEFORE_SUBMIT
    if blocking["critical"]:
        return (
            ContributorAction.FIX_BEFORE_SUBMIT,
            f"Critical issues: {', '.join(s.get('key', '') for s in blocking['critical'][:3])}",
        )

    # High blocking → FIX_BEFORE_SUBMIT
    if blocking["high"]:
        return (
            ContributorAction.FIX_BEFORE_SUBMIT,
            f"High-risk issues: {', '.join(s.get('key', '') for s in blocking['high'][:3])}",
        )

    # Breaking change without discussion → NEEDS_DISCUSSION
    if impact.breaking_change:
        return (
            ContributorAction.NEEDS_DISCUSSION,
            "Breaking change detected. Open an issue first to discuss with maintainers.",
        )

    # Security sensitive → NEEDS_DISCUSSION
    if impact.security_sensitive:
        return (
            ContributorAction.NEEDS_DISCUSSION,
            "Security-sensitive changes. Discuss with maintainers first.",
        )

    # Medium blocking → IMPROVE_CHANCE
    if blocking["medium"]:
        return (
            ContributorAction.IMPROVE_CHANCE,
            f"Issues to address: {', '.join(s.get('key', '') for s in blocking['medium'][:3])}",
        )

    # Low risk with positive signals → READY_TO_SUBMIT
    if tier == "low_risk":
        return (
            ContributorAction.READY_TO_SUBMIT,
            "No blocking issues found. PR is ready to submit.",
        )

    # Default → ASK_MAINTAINER
    return (
        ContributorAction.ASK_MAINTAINER,
        "Unclear risk level. Consider asking maintainer for guidance.",
    )


def _build_next_step(action: ContributorAction, analysis: dict) -> str:
    """Build next step instruction for the contributor."""
    if action == ContributorAction.READY_TO_SUBMIT:
        return "Submit your PR. No changes needed."

    if action == ContributorAction.FIX_BEFORE_SUBMIT:
        signals = analysis.get("signals", {})
        fixes = []
        for s in signals.get("negative", [])[:3]:
            fix = s.get("fix_action", "")
            if fix:
                fixes.append(f"- {fix}")
        return "Fix these issues before submitting:\n" + "\n".join(fixes) if fixes else "Review and fix the blocking issues."

    if action == ContributorAction.NEEDS_DISCUSSION:
        return "Open an issue first to discuss your proposed changes with maintainers."

    if action == ContributorAction.IMPROVE_CHANCE:
        return "Consider addressing the medium-severity issues to improve merge probability."

    if action == ContributorAction.ASK_MAINTAINER:
        return "Ask a maintainer for guidance on your proposed changes."

    return ""


def contributor_view(
    title: str,
    description: str,
    repo: str,
    body: str = "",
    labels: Optional[list[str]] = None,
    author: str = "",
    author_association: str = "NONE",
    star_count: int = 0,
    repo_merge_rate: float = 0.0,
    diff_stat: str = "",
    repo_root: Optional[Path] = None,
) -> dict:
    """Build a contributor-facing decision for one PR.

    Returns dict with action, next_step, checklist, confidence,
    impact, review, author_info.
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

    impact = assess_impact(title, body, diff_stat)
    review = assess_review_complexity(impact, title, body)
    action, reason = route_action(analysis, impact)
    next_step = _build_next_step(action, analysis)
    checklist = _build_checklist(analysis, impact)

    # Confidence: how confident are we in this assessment?
    merge_prob = analysis.get("merge_probability", 0.0)
    if action == ContributorAction.READY_TO_SUBMIT:
        confidence = "high"
    elif action == ContributorAction.FIX_BEFORE_SUBMIT:
        confidence = "high"
    elif action == ContributorAction.NEEDS_DISCUSSION:
        confidence = "medium"
    else:
        confidence = "low"

    # Author info
    assoc_upper = author_association.upper().strip()
    is_first_time = assoc_upper in ("NONE", "FIRST_TIMER", "FIRST_TIME_CONTRIBUTOR")

    return {
        "persona": "contributor",
        "repo": repo,
        "title": title,
        "author": author,
        "action": action.value,
        "action_label": ACTION_LABELS.get(action, ""),
        "action_icon": ACTION_ICONS.get(action, ""),
        "reason": reason,
        "next_step": next_step,
        "checklist": checklist,
        "confidence": confidence,
        "merge_probability": merge_prob,
        "impact": asdict(impact),
        "review": asdict(review),
        "author_info": {
            "association": assoc_upper,
            "first_time": is_first_time,
        },
        "context": {
            "tier": analysis.get("tier", "unknown"),
            "signals": analysis.get("signals", {}),
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
