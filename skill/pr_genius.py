#!/usr/bin/env python3
"""PR Genius — Thin wrapper around the `prgenius` package.

This module re-exports core functions from prgenius.evaluator for backward
compatibility.  All analysis logic lives in the package; this file provides
only:
  - The ``describe`` CLI sub-command (not in the package)
  - ``_print_analysis`` helper for human-readable output (CLI only)

Usage (unchanged):
    python3 pr_genius.py analyze "feat: add feature" --repo org/repo --body "..."
    python3 pr_genius.py eval "feat: add feature" --repo org/repo
    python3 pr_genius.py coach "feat: add feature" --repo org/repo
    python3 pr_genius.py describe "feat: add feature" --repo org/repo --issue 42
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Delegate core logic to the prgenius package
# ---------------------------------------------------------------------------
from prgenius.evaluator import (
    analyze_pr,
    eval_pr,
    is_bot_author,
    # Constants re-exported for backward compatibility
    LABEL_SIGNALS,
    BOT_AUTHORS,
    ISSUE_LINK_RE,
    ASSOCIATION_LABELS,
    ANTI_PATTERN_SEVERITY,
)

# Compute repo_root from this file's location (backward-compatible default)
_REPO_ROOT = Path(__file__).resolve().parent.parent

__all__ = [
    "analyze_pr",
    "eval_pr",
    "is_bot_author",
    "LABEL_SIGNALS",
    "BOT_AUTHORS",
    "ISSUE_LINK_RE",
    "ASSOCIATION_LABELS",
    "ANTI_PATTERN_SEVERITY",
    "main",
]


# ---------------------------------------------------------------------------
# CLI helpers (unique to skill file)
# ---------------------------------------------------------------------------

TIER_ICONS: Dict[str, str] = {"low_risk": "\U0001f7e2", "medium_risk": "\U0001f7e1", "high_risk": "\U0001f534"}
TIER_LABELS: Dict[str, str] = {"low_risk": "低风险", "medium_risk": "中风险", "high_risk": "高风险"}


def _print_analysis(result: dict) -> None:
    """Human-readable analysis output (skill-specific formatting)."""
    tier = result["tier"]
    icon = TIER_ICONS.get(tier, "⚪")
    label = TIER_LABELS.get(tier, tier)
    signals = result["signals"]

    print(f"## PR 分析: {result['repo']}\n")
    print(f"**{icon} 综合评估: {label}** ({len(signals['positive'])} 正面 / {len(signals['negative'])} 负面)\n")

    if signals["negative"]:
        print("### ⚠️ 需要改进\n")
        for i, s in enumerate(signals["negative"], 1):
            sev = s.get("severity", "")
            sev_icon = {"critical": "\U0001f6a8", "high": "⚠️", "medium": "\U0001f4cb"}.get(sev, "•")
            print(f"{i}. {sev_icon} **{s['description']}**")
            if s.get("fix_action"):
                print(f"   → {s['fix_action']}")
            if s.get("source_pr"):
                print(f"   (历史案例: {s['source_pr']})")
        print()

    if signals["positive"]:
        print("### ✅ 已具备\n")
        for s in signals["positive"]:
            print(f"- {s['description']}")
        print()

    if signals["neutral"]:
        print("### ℹ️ 参考信息\n")
        for s in signals["neutral"]:
            print(f"- {s['description']}")
        print()

    if result["checklist"]:
        print("### \U0001f4cb 提交前清单\n")
        for item in result["checklist"]:
            mark = "✅" if item["done"] else "☐"
            print(f"- [{mark}] **[{item['priority']}]** {item['hint']}")
        print()

    ctx = result.get("repo_context", {})
    if ctx:
        parts = []
        if "star_count" in ctx:
            parts.append(f"{ctx['star_count']:,}⭐")
        if "repo_size" in ctx:
            parts.append(ctx["repo_size"])
        if "merge_rate" in ctx:
            parts.append(f"merge率 {ctx['merge_rate']:.0%}")
        if parts:
            print(f"*仓库: {' | '.join(parts)}*\n")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="PR Genius — 提交前改进顾问")
    subparsers = parser.add_subparsers(dest="command", help="命令")

    # analyze
    ap = subparsers.add_parser("analyze", help="分析 PR 并生成改进建议")
    ap.add_argument("title")
    ap.add_argument("--description", "-d", default="")
    ap.add_argument("--body", "-b", default="")
    ap.add_argument("--repo", "-r", required=True)
    ap.add_argument("--labels", "-l", nargs="*", default=[])
    ap.add_argument("--author", "-a", default="")
    ap.add_argument("--star-count", type=int, default=0)
    ap.add_argument("--repo-merge-rate", type=float, default=0.0)
    ap.add_argument("--author-association", default="NONE")
    ap.add_argument("--mergeable", default="MERGEABLE")
    ap.add_argument("--format", "-f", choices=["text", "json"], default="text")

    # eval (compat)
    ep = subparsers.add_parser("eval", help="评估 PR (降级为三档)")
    ep.add_argument("title")
    ep.add_argument("--description", "-d", default="")
    ep.add_argument("--body", "-b", default="")
    ep.add_argument("--repo", "-r", required=True)
    ep.add_argument("--labels", "-l", nargs="*", default=[])
    ep.add_argument("--author", "-a", default="")
    ep.add_argument("--star-count", type=int, default=0)
    ep.add_argument("--repo-merge-rate", type=float, default=0.0)
    ep.add_argument("--author-association", default="NONE")

    # coach (Agent PR Dojo)
    ch = subparsers.add_parser("coach", help="Agent PR Dojo — exit 0=pass, exit 1=fail")
    ch.add_argument("title")
    ch.add_argument("--description", "-d", default="")
    ch.add_argument("--body", "-b", default="")
    ch.add_argument("--repo", "-r", required=True)
    ch.add_argument("--labels", "-l", nargs="*", default=[])
    ch.add_argument("--author", "-a", default="")
    ch.add_argument("--star-count", type=int, default=0)
    ch.add_argument("--repo-merge-rate", type=float, default=0.0)
    ch.add_argument("--author-association", default="NONE")
    ch.add_argument("--mergeable", default="MERGEABLE")
    ch.add_argument("--format", "-f", choices=["text", "json"], default="text")

    # describe (unique to skill file)
    dp = subparsers.add_parser("describe", help="生成 PR 描述模板")
    dp.add_argument("title")
    dp.add_argument("--description", "-d", default="")
    dp.add_argument("--repo", "-r", required=True)
    dp.add_argument("--issue", "-i")

    args = parser.parse_args()

    if args.command == "analyze":
        result = analyze_pr(
            args.title, args.description or "", args.repo, _REPO_ROOT,
            body=args.body or "", labels=args.labels or [], author=args.author or "",
            star_count=args.star_count or 0, repo_merge_rate=args.repo_merge_rate or 0.0,
            author_association=args.author_association or "NONE",
            mergeable=args.mergeable or "MERGEABLE",
        )
        if args.format == "json":
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            _print_analysis(result)

    elif args.command == "eval":
        result = eval_pr(
            args.title, args.description or "", args.repo, _REPO_ROOT,
            body=args.body or "", labels=args.labels or [], author=args.author or "",
            star_count=args.star_count or 0, repo_merge_rate=args.repo_merge_rate or 0.0,
            author_association=args.author_association or "NONE",
        )
        # Backward compat: add tier_raw if missing (standalone version had it)
        if "tier_raw" not in result:
            result["tier_raw"] = result.get("tier", "")
        tier = result["tier"]
        icon = TIER_ICONS.get(result.get("tier_raw", ""), "⚪")
        print(f"**{icon} 风险等级: {tier}**\n")
        analysis = result["analysis"]
        if analysis["signals"]["negative"]:
            print("### ⚠️ 风险点")
            for s in analysis["signals"]["negative"]:
                print(f"- {s['description']}")
            print()
        if analysis["checklist"]:
            print("### \U0001f4cb 建议")
            for item in analysis["checklist"]:
                if not item["done"]:
                    print(f"- **[{item['priority']}]** {item['hint']}")

    elif args.command == "coach":
        result = analyze_pr(
            args.title, args.description or "", args.repo, _REPO_ROOT,
            body=args.body or "", labels=args.labels or [], author=args.author or "",
            star_count=args.star_count or 0, repo_merge_rate=args.repo_merge_rate or 0.0,
            author_association=args.author_association or "NONE",
            mergeable=args.mergeable or "MERGEABLE",
        )
        tier = result["tier"]
        icon = TIER_ICONS.get(tier, "⚪")
        label = TIER_LABELS.get(tier, tier)
        passed = tier != "high_risk"

        if args.format == "json":
            result["pass"] = passed
            result["exit_code"] = 0 if passed else 1
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{icon} {status} — {label}\n")
            if result["signals"]["negative"]:
                for s in result["signals"]["negative"]:
                    sev = s.get("severity", "")
                    sev_icon = {"critical": "\U0001f6a8", "high": "⚠️", "medium": "\U0001f4cb"}.get(sev, "•")
                    print(f"  {sev_icon} {s['description']}")
                    if s.get("fix_action"):
                        print(f"     → {s['fix_action']}")
                print()
            undone = [c for c in result["checklist"] if not c["done"]]
            if undone:
                print("\U0001f4cb 待修复:")
                for item in undone:
                    print(f"  [{item['priority']}] {item['hint']}")
                print()
            if passed:
                print("可以提交，但建议先完成上述 checklist。")
            else:
                print("请先修复上述问题再提交。")
        sys.exit(0 if passed else 1)

    elif args.command == "describe":
        print(f"## PR 描述\n### 标题\n{args.title}\n### 描述\n{args.description}\n")
        if args.issue:
            print(f"### 关联 Issue\nCloses {args.issue}\n")
        print("### 验收标准\n- [ ] 代码实现\n- [ ] 测试覆盖\n- [ ] DCO sign-off\n- [ ] CI 通过")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
