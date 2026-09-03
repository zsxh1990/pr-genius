#!/usr/bin/env python3
"""Post (or update) a full PR Genius analysis as a visible PR comment.

Mirrors pr-agent's /review behavior: the complete analysis (tier, signals,
checklist, anti-patterns, repo context) is rendered to Markdown and posted as
an issue comment on the PR page. Existing comments from the same bot carrying
the marker are updated in place so repeated syncs do not spam the thread.

Usage (from the composite action):
    echo "$RESULT" | python3 post_comment.py \
        --repo OWNER/NAME --pr-number N --token "$GH_TOKEN" \
        [--marker "<!-- pr-genius:report -->"]
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request

TIER_ICONS = {"low_risk": "\U0001F7E2", "medium_risk": "\U0001F7E1", "high_risk": "\U0001F534"}
TIER_LABELS = {"low_risk": "Low Risk", "medium_risk": "Medium Risk", "high_risk": "High Risk"}
SEV_ICONS = {"critical": "\U0001F6A8", "high": "\u26A0\uFE0F", "medium": "\U0001F4CB", "low": "\u2022"}
MARKER = "<!-- pr-genius:report -->"


def _api(url: str, token: str, data: dict | None = None, method: str | None = None):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    }
    body = json.dumps(data).encode() if data is not None else None
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = response.read()
        return json.loads(payload) if payload else None


def render_comment(result: dict) -> str:
    """Render the full analysis as a PR comment (mirror pr-agent /review)."""
    tier = result.get("tier", "unknown")
    icon = TIER_ICONS.get(tier, "\u26AA")
    label = TIER_LABELS.get(tier, tier)
    repo = result.get("repo", "")
    signals = result.get("signals", {}) or {}
    neg = signals.get("negative") or []
    pos = signals.get("positive") or []
    neu = signals.get("neutral") or []

    lines = ["## \U0001F9EC PR Genius Analysis", ""]
    lines.append(f"**{icon} Risk tier: {label}** ({len(pos)} positive / {len(neg)} negative)")
    if repo:
        lines.append(f"*{repo}*")
    lines.append("")

    if neg:
        lines.append("### \u26A0\uFE0F Issues")
        lines.append("")
        for s in neg:
            sev_icon = SEV_ICONS.get(s.get("severity", ""), "\u2022")
            lines.append(f"- {sev_icon} **{s.get('description', '')}**")
            if s.get("fix_action"):
                lines.append(f"  - \u2192 {s['fix_action']}")
            if s.get("source_pr"):
                lines.append(f"  - (case: {s['source_pr']})")
        lines.append("")

    if pos:
        lines.append("### \u2705 Positive")
        lines.append("")
        for s in pos:
            lines.append(f"- {s.get('description', '')}")
        lines.append("")

    if neu:
        lines.append("### \u2139\uFE0F Info")
        lines.append("")
        for s in neu:
            lines.append(f"- {s.get('description', '')}")
        lines.append("")

    checklist = result.get("checklist") or []
    if checklist:
        lines.append("### \U0001F4CB Checklist")
        lines.append("")
        for item in checklist:
            mark = "\u2705" if item.get("done") else "\u2610"
            lines.append(f"- [{mark}] **[{item.get('priority', '')}]** {item.get('hint', '')}")
        lines.append("")

    # Prefer anti_patterns_detail (dicts with severity/fix_action),
    # fall back to anti_patterns_hit (list of key strings).
    anti_detail = result.get("anti_patterns_detail") or []
    anti_keys = result.get("anti_patterns_hit") or []
    if anti_detail or anti_keys:
        lines.append("### \U0001F50E Anti-Patterns")
        lines.append("")
        if anti_detail:
            for a in anti_detail:
                sev_icon = SEV_ICONS.get(a.get("severity", ""), "\u2022")
                lines.append(f"- {sev_icon} **{a.get('description', a.get('key', ''))}**")
                if a.get("fix_action"):
                    lines.append(f"  - \u2192 {a['fix_action']}")
        else:
            for key in anti_keys:
                lines.append(f"- \u2022 **{key}**")
        lines.append("")

    ctx = result.get("repo_context") or {}
    parts = []
    if ctx.get("star_count"):
        parts.append(f"{ctx['star_count']:,}\u2B50")
    if ctx.get("repo_size"):
        parts.append(str(ctx["repo_size"]))
    if ctx.get("merge_rate") is not None:
        parts.append(f"merge rate {ctx['merge_rate']:.0%}")
    if parts:
        lines.append(f"*Repo: {' | '.join(parts)}*")
        lines.append("")

    lines.append("*This is a non-blocking advisory from PR Genius. It does not request changes or block merge.*")
    lines.append("")
    lines.append(MARKER)
    return "\n".join(lines)


def post_or_update(repo: str, number: int, token: str, body: str, marker: str = MARKER) -> None:
    """POST the comment, or PATCH the bot's existing comment carrying the marker."""
    base = f"https://api.github.com/repos/{repo}/issues/{number}/comments"
    existing = []
    try:
        existing = _api(base, token) or []
    except Exception:
        pass
    for comment in existing:
        if marker in (comment.get("body") or ""):
            _api(comment["url"], token, {"body": body}, method="PATCH")
            return
    _api(base, token, {"body": body}, method="POST")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--pr-number", required=True, type=int)
    parser.add_argument("--token", default="")
    parser.add_argument("--marker", default=MARKER)
    args = parser.parse_args()
    result = json.load(sys.stdin)
    body = render_comment(result)
    try:
        post_or_update(args.repo, args.pr_number, args.token, body, args.marker)
    except Exception as exc:  # advisory only — never fail the workflow
        print(f"  \u26A0\uFE0F Could not post PR Genius comment: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
