"""CLI entry point for `prgenius`.

Usage examples (run from repo root):
    python3 -m prgenius analyze "feat: add feature" --repo org/repo --body "..."
    python3 -m prgenius analyze "feat: add feature" --repo org/repo --format json
    python3 -m prgenius eval "feat: add feature" --repo org/repo
    python3 -m prgenius profile get astral-sh/uv
    python3 -m prgenius case list --status=open
    python3 -m prgenius mcp serve
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .triage import triage_pr
from .parser import (
    iter_profiles,
    iter_case_studies,
    profile_get,
    schema_info,
)
from .evaluator import analyze_pr, eval_pr
from .status import check_status, format_table


REPO_ROOT_DEFAULT = Path(__file__).resolve().parents[3]


def _get_repo_root(args) -> Path:
    if args.repo_root:
        return Path(args.repo_root).resolve()
    return REPO_ROOT_DEFAULT


# ============================================================
# analyze — 主命令
# ============================================================

TIER_ICONS = {"low_risk": "🟢", "medium_risk": "🟡", "high_risk": "🔴"}
TIER_LABELS = {"low_risk": "低风险", "medium_risk": "中风险", "high_risk": "高风险"}


def cmd_analyze(args) -> int:
    """分析 PR 并输出改进建议"""
    repo_root = _get_repo_root(args)
    labels = args.labels if args.labels else []

    result = analyze_pr(
        args.title, args.description or "", args.repo, repo_root,
        body=args.body or "", labels=labels, author=args.author or "",
        star_count=args.star_count or 0, repo_merge_rate=args.repo_merge_rate or 0.0,
        author_association=args.author_association or "NONE",
        mergeable=args.mergeable or "MERGEABLE",
    )

    if args.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    # 人类可读输出
    tier = result["tier"]
    icon = TIER_ICONS.get(tier, "⚪")
    label = TIER_LABELS.get(tier, tier)
    signals = result["signals"]

    print(f"## PR 分析: {result['repo']}\n")
    print(f"**{icon} 综合评估: {label}** ({len(signals['positive'])} 正面 / {len(signals['negative'])} 负面)\n")

    # 负面信号
    if signals["negative"]:
        print("### ⚠️ 需要改进\n")
        for i, s in enumerate(signals["negative"], 1):
            sev = s.get("severity", "")
            sev_icon = {"critical": "🚨", "high": "⚠️", "medium": "📋"}.get(sev, "•")
            print(f"{i}. {sev_icon} **{s['description']}**")
            if s.get("fix_action"):
                print(f"   → {s['fix_action']}")
            if s.get("source_pr"):
                print(f"   (历史案例: {s['source_pr']})")
        print()

    # 正面信号
    if signals["positive"]:
        print("### ✅ 已具备\n")
        for s in signals["positive"]:
            print(f"- {s['description']}")
        print()

    # 中性信号
    if signals["neutral"]:
        print("### ℹ️ 参考信息\n")
        for s in signals["neutral"]:
            print(f"- {s['description']}")
        print()

    # 提交前清单
    if result["checklist"]:
        print("### 📋 提交前清单\n")
        for item in result["checklist"]:
            mark = "✅" if item["done"] else "☐"
            pri = item["priority"]
            print(f"- [{mark}] **[{pri}]** {item['hint']}")
        print()

    # 仓库上下文
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

    return 0


# ============================================================
# coach — Agent PR Dojo (exit code = pass/fail)
# ============================================================

def cmd_coach(args) -> int:
    """Agent PR Dojo: analyze + exit code 表示 pass/fail

    exit 0 = 通过 (低风险/中风险)
    exit 1 = 不通过 (高风险)，Agent 应先修复再提交
    """
    repo_root = _get_repo_root(args)
    labels = args.labels if args.labels else []

    result = analyze_pr(
        args.title, args.description or "", args.repo, repo_root,
        body=args.body or "", labels=labels, author=args.author or "",
        star_count=args.star_count or 0, repo_merge_rate=args.repo_merge_rate or 0.0,
        author_association=args.author_association or "NONE",
        mergeable=args.mergeable or "MERGEABLE",
    )

    # Phase 5.1: Add impact/review assessment if diff_stat provided
    diff_stat = getattr(args, 'diff_stat', '') or ""
    if diff_stat:
        from .pr_metadata import assess_impact, assess_review_complexity
        from dataclasses import asdict
        impact = assess_impact(args.title, args.body or "", diff_stat)
        review = assess_review_complexity(impact, args.title, args.body or "")
        result["impact"] = asdict(impact)
        result["review"] = asdict(review)

    tier = result["tier"]
    icon = TIER_ICONS.get(tier, "⚪")
    label = TIER_LABELS.get(tier, tier)

    if args.format == "json":
        # JSON 输出: 加 pass/fail 字段
        result["pass"] = tier != "high_risk"
        result["exit_code"] = 0 if tier != "high_risk" else 1
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        # 人类可读
        passed = tier != "high_risk"
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{icon} {status} — {label}\n")

        if result["signals"]["negative"]:
            for s in result["signals"]["negative"]:
                sev = s.get("severity", "")
                sev_icon = {"critical": "🚨", "high": "⚠️", "medium": "📋"}.get(sev, "•")
                print(f"  {sev_icon} {s['description']}")
                if s.get("fix_action"):
                    print(f"     → {s['fix_action']}")
            print()

        if result["checklist"]:
            undone = [c for c in result["checklist"] if not c["done"]]
            if undone:
                print("📋 待修复:")
                for item in undone:
                    print(f"  [{item['priority']}] {item['hint']}")
                print()

        if passed:
            print("可以提交，但建议先完成上述 checklist。")
        else:
            print("请先修复上述问题再提交。")

    return 0 if tier != "high_risk" else 1


# ============================================================
# eval — 兼容旧命令，降级为三档
# ============================================================

def cmd_eval(args) -> int:
    """评估 PR（降级为三档）"""
    repo_root = _get_repo_root(args)
    labels = args.labels if args.labels else []
    result = eval_pr(
        args.title, args.description or "", args.repo, repo_root,
        body=args.body or "", labels=labels, author=args.author or "",
        star_count=args.star_count or 0, repo_merge_rate=args.repo_merge_rate or 0.0,
        author_association=args.author_association or "NONE",
    )

    tier = result["tier"]
    icon = TIER_ICONS.get(result.get("tier_raw", ""), "⚪")

    print(f"## PR 评估: {result['repo']}\n")
    print(f"**{icon} 风险等级: {tier}**\n")

    # 复用 analyze 输出
    analysis = result["analysis"]
    signals = analysis["signals"]

    if signals["negative"]:
        print("### ⚠️ 风险点\n")
        for s in signals["negative"]:
            print(f"- {s['description']}")
        print()

    if signals["positive"]:
        print("### ✅ 正面信号\n")
        for s in signals["positive"]:
            print(f"- {s['description']}")
        print()

    if analysis["checklist"]:
        print("### 📋 建议\n")
        for item in analysis["checklist"]:
            if not item["done"]:
                print(f"- **[{item['priority']}]** {item['hint']}")
        print()

    return 0


# ============================================================
# 其他命令
# ============================================================

def cmd_profile_get(args) -> int:
    p = profile_get(_get_repo_root(args), args.repo)
    if p is None:
        print(f"profile not found: {args.repo}", file=sys.stderr)
        return 2
    out = {
        "path": p["path"],
        "folder": p["folder"],
        "frontmatter": p["frontmatter"],
        "first_lines": p["body"].splitlines()[:30],
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


def cmd_case_list(args) -> int:
    rows = []
    for c in iter_case_studies(_get_repo_root(args)):
        fm = c["frontmatter"]
        fs = fm.get("final_status", "?")
        if args.status and fs != args.status:
            continue
        rows.append({
            "folder": c["folder"],
            "pr_number": fm.get("pr_number"),
            "pr_url": fm.get("pr_url"),
            "final_status": fs,
            "schema_version": fm.get("schema_version", "legacy v0.1"),
            "verified_at": fm.get("verified_at"),
        })
    print(json.dumps(rows, indent=2, ensure_ascii=False))
    return 0


def cmd_schema_info(_args) -> int:
    print(json.dumps(schema_info(), indent=2, ensure_ascii=False))
    return 0


def cmd_dump(args) -> int:
    root = _get_repo_root(args)
    for c in iter_case_studies(root):
        fm = c["frontmatter"]
        record = {
            "folder": c["folder"],
            "pr_file": c["pr_file"],
            "pr_number": fm.get("pr_number"),
            "pr_url": fm.get("pr_url"),
            "repo": fm.get("repo"),
            "final_status": fm.get("final_status"),
            "opened_at": fm.get("opened_at"),
            "merged_at": fm.get("merged_at"),
            "closed_at": fm.get("closed_at"),
            "schema_version": fm.get("schema_version", "legacy v0.1"),
            "verified_at": fm.get("verified_at"),
            "evidence_urls": fm.get("evidence_urls", []),
            "confidence": fm.get("confidence"),
            "rounds": fm.get("rounds", []),
            "close_decision": fm.get("close_decision"),
        }
        print(json.dumps(record, ensure_ascii=False))
    return 0


def cmd_suggest(args) -> int:
    """兼容旧命令 — 转发到 analyze"""
    return cmd_analyze(args)


def cmd_harvest(args) -> int:
    """从被拒 PR 提取反模式/lesson draft"""
    import subprocess
    repo_root = _get_repo_root(args)
    harvest_script = repo_root / "scripts" / "harvest.py"
    if not harvest_script.exists():
        print(f"harvest script not found: {harvest_script}", file=sys.stderr)
        return 1

    cmd = [sys.executable, str(harvest_script), args.repo_or_url]
    if args.number:
        cmd.append(str(args.number))
    if args.type:
        cmd.extend(["--type", args.type])
    if args.output:
        cmd.extend(["--output", args.output])

    return subprocess.call(cmd)


def cmd_mcp_serve(args) -> int:
    from .mcp import serve
    repo_root = _get_repo_root(args)
    return serve(repo_root=repo_root)


def cmd_triage(args) -> int:
    """Triage PR against maintainer policy."""
    repo_root = _get_repo_root(args)
    body = args.body or ""
    diff_stat = args.diff_stat or ""

    # Read body from file if specified
    if args.body_file:
        try:
            body = Path(args.body_file).read_text(encoding="utf-8")
        except (OSError, FileNotFoundError) as e:
            print(f"Error reading body file: {e}", file=sys.stderr)
            return 1

    result = triage_pr(
        title=args.title,
        repo=args.repo,
        body=body,
        diff_stat=diff_stat,
        repo_root=repo_root,
    )

    if args.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        # Human-readable output
        print(f"## PR Triage: {result['repo']}\n")
        print(f"**{result['message']}**\n")

        if result.get("policy_loaded"):
            print(f"Policy: `{result['policy_file']}`")
            print(f"Rules checked: {result['rules_checked']}\n")

        if result["violations"]:
            print("### Violations\n")
            for v in result["violations"]:
                icon = "🔴" if v["rule_type"] == "hard" else "🟡"
                anchors = ", ".join(f"#{a}" for a in v.get("anchors", []))
                print(f"{icon} **Rule {v['rule_number']}**: {v['rule_title']}")
                print(f"   Evidence: {v['evidence']}")
                if anchors:
                    print(f"   Anchors: {anchors}")
                print()
        else:
            print("No policy violations detected.\n")

    # Exit code: 1 = reject, 0 = pass/warn
    return 1 if result["verdict"] == "reject" else 0


def cmd_status(args) -> int:
    """Check health of in-flight PRs."""
    if not args.author and not args.repo:
        print("Error: specify --author or --repo", file=sys.stderr)
        return 1

    repo_root = _get_repo_root(args)
    cli_stale_days = args.stale_days if args.stale_days is not None else None
    snapshot_dir = Path(args.snapshot_dir) if args.snapshot_dir else None

    try:
        result = check_status(
            author=args.author,
            repo=args.repo,
            stale_days=cli_stale_days,
            repo_root=repo_root,
            save_snapshot=args.save_snapshot,
            snapshot_dir=snapshot_dir,
        )
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # Alert-only mode: filter to only changed/alerted PRs
    if args.alert_only:
        transitions = result.get("transitions", [])
        alert_keys = {f"{t['repo']}#{t['number']}" for t in transitions if t.get("changed")}
        if alert_keys:
            result["prs"] = [p for p in result["prs"] if f"{p['repo']}#{p['number']}" in alert_keys]
        else:
            result["prs"] = []
        # Also surface NEW and CLOSED_OR_MERGED transitions in transitions[];
        # --alert-only filters classified PRs but never hides transition events.

    # Writeback suggestions
    if args.writeback_mode != "off":
        from .status import suggest_profile_writeback, format_writeback_suggestions
        suggestions = suggest_profile_writeback(result, repo_root=repo_root, mode=args.writeback_mode)
        result["writeback_suggestions"] = suggestions
        if args.format == "table" and suggestions:
            print(format_writeback_suggestions(suggestions))
            print()

    if args.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(format_table(result))

    # Write GitHub Step Summary
    if args.step_summary:
        import os
        summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary_path:
            from .status import format_step_summary
            with open(summary_path, "a", encoding="utf-8") as f:
                f.write(format_step_summary(result))
                f.write("\n")
        else:
            print("Warning: GITHUB_STEP_SUMMARY not set, skipping step summary", file=sys.stderr)

    # Webhook notification
    if args.webhook:
        from .status import notify_webhook
        webhook_result = notify_webhook(result, args.webhook, dry_run=args.webhook_dry_run)
        if args.webhook_dry_run:
            print(json.dumps(webhook_result, indent=2, ensure_ascii=False), file=sys.stderr)
        elif not webhook_result["ok"]:
            print(f"Webhook failed: {webhook_result.get('error', webhook_result.get('status_code'))}", file=sys.stderr)

    return 0


def cmd_profile_writeback(args) -> int:
    """Show profile writeback suggestions."""
    from .status import check_status, suggest_profile_writeback, format_writeback_suggestions

    repo_root = _get_repo_root(args)
    try:
        result = check_status(author=args.author, repo_root=repo_root, save_snapshot=False)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    suggestions = suggest_profile_writeback(result, repo_root=repo_root, mode=args.mode)

    if args.format == "json":
        print(json.dumps(suggestions, indent=2, ensure_ascii=False))
    else:
        print(format_writeback_suggestions(suggestions))


def cmd_update_issue(args) -> int:
    """Update a pinned GitHub issue with heartbeat status."""
    import subprocess
    from .status import check_status, format_issue_body

    repo_root = _get_repo_root(args)

    try:
        result = check_status(
            author=args.author,
            repo=args.repo,
            stale_days=args.stale_days,
            repo_root=repo_root,
            save_snapshot=args.save_snapshot,
            snapshot_dir=Path(args.snapshot_dir) if args.snapshot_dir else None,
        )
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    body = format_issue_body(result)

    if args.dry_run:
        print(body)
        return 0

    # Update issue via gh CLI
    try:
        subprocess.run(
            ["gh", "issue", "edit", str(args.issue_number),
             "--repo", args.issue_repo,
             "--body", body],
            check=True,
            capture_output=True,
            text=True,
        )
        print(f"Updated {args.issue_repo}#{args.issue_number}")
    except subprocess.CalledProcessError as e:
        print(f"Error updating issue: {e.stderr}", file=sys.stderr)
        return 1

    return 0


def cmd_auto_ping(args) -> int:
    """Suggest ping actions for stale PRs (dry-run by default)."""
    from .status import check_status, PRStatus

    repo_root = _get_repo_root(args)
    try:
        result = check_status(author=args.author, repo_root=repo_root, save_snapshot=False)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    pingable = [p for p in result["prs"] if p.get("ping_suggested")]
    abandonable = [p for p in result["prs"] if p.get("abandon_candidate")]

    if not pingable and not abandonable:
        print("No PRs need pinging or abandoning.")
        return 0

    if args.format == "json":
        output = {
            "ping": [{"repo": p["repo"], "number": p["number"], "title": p["title"],
                       "status": p["status"], "days_since_update": p["days_since_update"]}
                      for p in pingable],
            "abandon": [{"repo": p["repo"], "number": p["number"], "title": p["title"],
                         "status": p["status"], "days_since_update": p["days_since_update"]}
                        for p in abandonable],
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return 0

    if pingable:
        print(f"📢 Suggested pings ({len(pingable)} PRs):")
        for p in pingable:
            print(f"  {p['repo']}#{p['number']} — {p['status']} ({p['days_since_update']}d)")
            print(f"    → {p['suggested_action']}")
        print()

    if abandonable:
        print(f"🗑️  Abandon candidates ({len(abandonable)} PRs):")
        for p in abandonable:
            print(f"  {p['repo']}#{p['number']} — {p['status']} ({p['days_since_update']}d)")
            print(f"    → {p['suggested_action']}")
        print()

    if not args.confirm:
        print("Dry-run mode. Use --confirm to execute pings.")
        return 0

    # Execute pings (only for ping_suggested, not abandon)
    import subprocess
    for p in pingable:
        try:
            # Add a comment to ping the maintainer
            comment = f"👋 Friendly ping — this PR has been waiting for review for {p['days_since_update']} days. Is there anything I can do to help move this forward?"
            subprocess.run(
                ["gh", "pr", "comment", str(p["number"]),
                 "--repo", p["repo"],
                 "--body", comment],
                check=True, capture_output=True, text=True,
            )
            print(f"  ✅ Pinged {p['repo']}#{p['number']}")
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Failed to ping {p['repo']}#{p['number']}: {e.stderr.strip()}", file=sys.stderr)

    return 0


def cmd_auto_rebase(args) -> int:
    """Suggest rebase actions for PRs that need it (dry-run by default)."""
    from .status import check_status, PRStatus

    repo_root = _get_repo_root(args)
    try:
        result = check_status(author=args.author, repo_root=repo_root, save_snapshot=False)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    rebaseable = [p for p in result["prs"] if p.get("rebase_suggested")]

    if not rebaseable:
        print("No PRs need rebasing.")
        return 0

    if args.format == "json":
        output = [{"repo": p["repo"], "number": p["number"], "title": p["title"],
                    "mergeable": p["mergeable"], "merge_state": p["merge_state"]}
                   for p in rebaseable]
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return 0

    print(f"🔄 PRs needing rebase ({len(rebaseable)}):")
    for p in rebaseable:
        print(f"  {p['repo']}#{p['number']} — {p['mergeable']}/{p['merge_state']}")
        print(f"    → {p['suggested_action']}")
    print()

    if not args.confirm:
        print("Dry-run mode. Use --confirm to attempt rebases.")
        return 0

    # Execute rebases via GitHub API (update branch)
    import subprocess
    for p in rebaseable:
        try:
            # Use gh to update the branch (equivalent to clicking "Update branch" in UI)
            result = subprocess.run(
                ["gh", "api", f"repos/{p['repo']}/pulls/{p['number']}/update-branch",
                 "-X", "PUT"],
                capture_output=True, text=True,
            )
            if result.returncode == 0:
                print(f"  ✅ Rebased {p['repo']}#{p['number']}")
            else:
                print(f"  ❌ Failed {p['repo']}#{p['number']}: {result.stderr.strip()}")
        except Exception as e:
            print(f"  ❌ Error {p['repo']}#{p['number']}: {e}", file=sys.stderr)

    return 0


# ============================================================
# maintainer — Maintainer view (v1.5.0)
# ============================================================

def cmd_maintainer_view(args) -> int:
    """Maintainer-facing action decision for a single PR.

    Output answers: "What should I do with this PR right now?"
    Actions: READY_FOR_REVIEW | WAIT_FOR_AUTHOR | CLOSE_DUPLICATE |
             CLOSE_STALE_OR_RISKY | HOLD_MAINTAINER_DECISION
    """
    from .maintainer_view import maintainer_view

    repo_root = _get_repo_root(args)
    body = args.body or ""
    if args.body_file:
        try:
            body = Path(args.body_file).read_text(encoding="utf-8")
        except (OSError, FileNotFoundError) as e:
            print(f"Error reading body file: {e}", file=sys.stderr)
            return 1

    result = maintainer_view(
        title=args.title,
        description=args.description or "",
        repo=args.repo,
        body=body,
        labels=args.labels or [],
        author=args.author or "",
        author_association=args.author_association or "NONE",
        star_count=args.star_count or 0,
        repo_merge_rate=args.repo_merge_rate or 0.0,
        repo_root=repo_root,
    )

    if args.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        from .maintainer_view import MaintainerAction
        action = result["action"]
        icon_map = {
            "READY_FOR_REVIEW": "✅",
            "WAIT_FOR_AUTHOR": "⏸️",
            "CLOSE_DUPLICATE": "🗑️",
            "CLOSE_STALE_OR_RISKY": "🛑",
            "HOLD_MAINTAINER_DECISION": "🤔",
        }
        icon = icon_map.get(action, "•")
        print(f"{icon} Maintainer Action: {action}")
        print(f"   Repo: {result['repo']}")
        print(f"   Title: {result['title']}")
        print(f"   Reason: {result['reason']}")
        print(f"   Blocking: {', '.join(result['blocking_signals']) or 'none'}")
        print(f"   Next step: {result['next_step']}")
        print(f"   Review ready: {result['review_ready']}")
        print(f"   Tier: {result['context'].get('tier', '?')}")
    return 0


def cmd_review_queue(args) -> int:
    """Build maintainer review queue from a list of PR dicts.

    Input: --prs-file (JSON list of {repo, number, title, body, author, labels})
           OR stdin (JSON list)
    Output: --format json|markdown, default markdown
    """
    from .maintainer_view import build_review_queue, write_review_queue_md

    repo_root = _get_repo_root(args)

    # Load PRs from file or stdin
    if args.prs_file:
        try:
            prs = json.loads(Path(args.prs_file).read_text(encoding="utf-8"))
        except (OSError, FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error reading PRs file: {e}", file=sys.stderr)
            return 1
    elif not sys.stdin.isatty():
        try:
            prs = json.loads(sys.stdin.read())
        except json.JSONDecodeError as e:
            print(f"Error parsing stdin JSON: {e}", file=sys.stderr)
            return 1
    else:
        print("Error: specify --prs-file or pipe JSON to stdin", file=sys.stderr)
        return 1

    if not isinstance(prs, list):
        print("Error: PRs must be a JSON list", file=sys.stderr)
        return 1

    queue = build_review_queue(prs, repo_root=repo_root)

    # Output
    if args.format == "json":
        print(json.dumps(queue, indent=2, ensure_ascii=False))
    else:
        # markdown
        if args.write_digest:
            output_path = Path(args.write_digest)
            if not output_path.is_absolute():
                output_path = repo_root / output_path
            write_review_queue_md(queue, output_path)
            print(f"✅ Digest written to: {output_path}", file=sys.stderr)
        # also print to stdout
        print(queue["digest_markdown"])

    return 0


# ============================================================
# main
# ============================================================

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="prgenius",
        description="PR Genius — 提交前改进顾问",
    )
    parser.add_argument("--repo-root", help="Path to pr-genius repo (default: auto-detect)")
    parser.add_argument("--version", action="version", version=f"prgenius {__version__}")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # ---- analyze (主命令) ----
    an = sub.add_parser("analyze", help="分析 PR 并生成改进建议")
    an.add_argument("title", help="PR 标题")
    an.add_argument("--description", "-d", default="", help="PR 描述")
    an.add_argument("--body", "-b", default="", help="PR body (完整内容)")
    an.add_argument("--repo", "-r", required=True, help="目标仓库 (org/repo)")
    an.add_argument("--labels", "-l", nargs="*", default=[], help="PR 标签")
    an.add_argument("--author", "-a", default="", help="PR 作者")
    an.add_argument("--star-count", type=int, default=0, help="仓库 star 数")
    an.add_argument("--repo-merge-rate", type=float, default=0.0, help="仓库 merge 率 (0-1)")
    an.add_argument("--author-association", default="NONE",
                    help="作者身份 (NONE/CONTRIBUTOR/COLLABORATOR/MEMBER/OWNER)")
    an.add_argument("--mergeable", default="MERGEABLE",
                    help="合并状态 (MERGEABLE/CONFLICTING/UNKNOWN)")
    an.add_argument("--format", "-f", choices=["text", "json"], default="text", help="输出格式")
    an.set_defaults(func=cmd_analyze)

    # ---- eval (兼容旧命令) ----
    ev = sub.add_parser("eval", help="评估 PR (降级为三档)")
    ev.add_argument("title", help="PR 标题")
    ev.add_argument("--description", "-d", default="", help="PR 描述")
    ev.add_argument("--body", "-b", default="", help="PR body")
    ev.add_argument("--repo", "-r", required=True, help="目标仓库 (org/repo)")
    ev.add_argument("--labels", "-l", nargs="*", default=[], help="PR 标签")
    ev.add_argument("--author", "-a", default="", help="PR 作者")
    ev.add_argument("--star-count", type=int, default=0, help="仓库 star 数")
    ev.add_argument("--repo-merge-rate", type=float, default=0.0, help="仓库 merge 率")
    ev.add_argument("--author-association", default="NONE", help="作者身份")
    ev.set_defaults(func=cmd_eval)

    # ---- coach (Agent PR Dojo) ----
    ch = sub.add_parser("coach", help="Agent PR Dojo — exit 0=pass, exit 1=fail")
    ch.add_argument("title", help="PR 标题")
    ch.add_argument("--description", "-d", default="", help="PR 描述")
    ch.add_argument("--body", "-b", default="", help="PR body")
    ch.add_argument("--repo", "-r", required=True, help="目标仓库 (org/repo)")
    ch.add_argument("--labels", "-l", nargs="*", default=[], help="PR 标签")
    ch.add_argument("--author", "-a", default="", help="PR 作者")
    ch.add_argument("--star-count", type=int, default=0, help="仓库 star 数")
    ch.add_argument("--repo-merge-rate", type=float, default=0.0, help="仓库 merge 率")
    ch.add_argument("--author-association", default="NONE", help="作者身份")
    ch.add_argument("--mergeable", default="MERGEABLE", help="合并状态 (MERGEABLE/CONFLICTING/UNKNOWN)")
    ch.add_argument("--diff-stat", default="", help="git diff --stat 输出 (用于 impact 评估)")
    ch.add_argument("--format", "-f", choices=["text", "json"], default="text", help="输出格式")
    ch.set_defaults(func=cmd_coach)

    # ---- triage ----
    tr = sub.add_parser("triage", help="Policy-aware PR triage")
    tr.add_argument("title", help="PR 标题")
    tr.add_argument("--repo", "-r", required=True, help="目标仓库 (org/repo)")
    tr.add_argument("--body", "-b", default="", help="PR body")
    tr.add_argument("--body-file", default="", help="从文件读取 PR body")
    tr.add_argument("--diff-stat", default="", help="git diff --stat 输出")
    tr.add_argument("--format", "-f", choices=["text", "json"], default="text", help="输出格式")
    tr.set_defaults(func=cmd_triage)

    # ---- suggest (兼容) ----
    sg = sub.add_parser("suggest", help="获取改进建议 (同 analyze)")
    sg.add_argument("title", help="PR 标题")
    sg.add_argument("--description", "-d", default="", help="PR 描述")
    sg.add_argument("--body", "-b", default="", help="PR body")
    sg.add_argument("--repo", "-r", required=True, help="目标仓库 (org/repo)")
    sg.add_argument("--labels", "-l", nargs="*", default=[], help="PR 标签")
    sg.add_argument("--author", "-a", default="", help="PR 作者")
    sg.add_argument("--star-count", type=int, default=0, help="仓库 star 数")
    sg.add_argument("--repo-merge-rate", type=float, default=0.0, help="仓库 merge 率")
    sg.add_argument("--author-association", default="NONE", help="作者身份")
    sg.add_argument("--format", "-f", choices=["text", "json"], default="text", help="输出格式")
    sg.set_defaults(func=cmd_suggest)

    # ---- harvest ----
    hv = sub.add_parser("harvest", help="从被拒 PR 提取 anti-pattern/lesson draft")
    hv.add_argument("repo_or_url", help="org/repo 或 PR URL")
    hv.add_argument("number", nargs="?", type=int, help="PR number")
    hv.add_argument("--type", "-t", choices=["anti-pattern", "lesson"], default="anti-pattern", help="输出类型")
    hv.add_argument("--output", "-o", help="输出文件路径")
    hv.add_argument("--repo-root", help="Path to pr-genius repo root")
    hv.set_defaults(func=cmd_harvest)

    # ---- profile ----
    p_get = sub.add_parser("profile", help="Profile operations")
    p_get_sub = p_get.add_subparsers(dest="profile_cmd", required=True)
    pp = p_get_sub.add_parser("get", help="Get one profile")
    pp.add_argument("repo", help="org/name")
    pp.add_argument("--repo-root", help="Path to pr-genius repo root")
    pp.set_defaults(func=cmd_profile_get)
    pw = p_get_sub.add_parser("writeback", help="Show profile writeback suggestions (dry-run)")
    pw.add_argument("--author", required=True, help="GitHub username")
    pw.add_argument("--mode", choices=["suggest", "auto"], default="suggest", help="Writeback mode")
    pw.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    pw.add_argument("--repo-root", help="Path to pr-genius repo root")
    pw.set_defaults(func=cmd_profile_writeback)

    # ---- case ----
    c_list = sub.add_parser("case", help="Case study operations")
    c_list_sub = c_list.add_subparsers(dest="case_cmd", required=True)
    cl = c_list_sub.add_parser("list", help="List case studies")
    cl.add_argument("--status", help="Filter by final_status")
    cl.set_defaults(func=cmd_case_list)

    # ---- schema ----
    s_info = sub.add_parser("schema", help="Schema info")
    s_info_sub = s_info.add_subparsers(dest="schema_cmd", required=True)
    si = s_info_sub.add_parser("info", help="Show supported schema versions")
    si.set_defaults(func=cmd_schema_info)

    # ---- status ----
    st = sub.add_parser(
        "status",
        help="Check health of in-flight PRs",
        description=(
            "Scan open PRs for an author or repo and classify each by health "
            "status (9 categories: NEEDS_REBASE / CI_FAILING / STALE_REVIEW / "
            "CHANGES_REQUESTED / STALE_NO_REVIEW / BLOCKED / CLEAN / UNKNOWN / "
            "WAITING). Optional --save-snapshot records results and detects "
            "transitions (e.g. WAITING -> NEEDS_REBASE) against the previous run."
        ),
        epilog=(
            "Examples:\n"
            "  prgenius status --author zsxh1990\n"
            "  prgenius status --repo Ikalus1988/MisakaNet --stale-days 7\n"
            "  prgenius status --author zsxh1990 --save-snapshot --alert-only\n"
            "  prgenius status --author zsxh1990 --writeback-mode suggest\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    st.add_argument("--author", help="GitHub username to check PRs for")
    st.add_argument("--repo", help="Repository to check PRs in (org/repo)")
    st.add_argument("--stale-days", type=int, default=None,
                    help="Days without update to consider stale (priority: CLI > profile > default 14)")
    st.add_argument("--format", choices=["table", "json"], default="table",
                    help="Output format (default: table)")
    st.add_argument("--save-snapshot", action="store_true",
                    help="Persist result to data/status-snapshots/ and diff against previous snapshot")
    st.add_argument("--snapshot-dir",
                    help="Directory for snapshots (default: data/status-snapshots)")
    st.add_argument("--writeback-mode", choices=["off", "suggest", "auto"], default="off",
                    help=(
                        "Profile writeback mode. 'suggest' lists all proposals; "
                        "'auto' keeps only confidence>=0.8 (currently always empty "
                        "because all rule confidences are <0.8 by design — see docs)."
                    ))
    st.add_argument("--alert-only", action="store_true",
                    help="Only output PRs whose status changed since the previous snapshot")
    st.add_argument("--step-summary", action="store_true", help="Write GitHub Step Summary to $GITHUB_STEP_SUMMARY")
    st.add_argument("--webhook", help="Webhook URL for notifications (飞书/Slack/generic)")
    st.add_argument("--webhook-dry-run", action="store_true", help="Show webhook payload without sending")
    st.add_argument("--repo-root", help="Path to pr-genius repo root")
    st.set_defaults(func=cmd_status)

    # ---- update-issue ----
    ui = sub.add_parser("update-issue", help="Update a pinned GitHub issue with heartbeat status")
    ui.add_argument("--author", help="GitHub username to check PRs for")
    ui.add_argument("--repo", help="Repository to check PRs in (org/repo)")
    ui.add_argument("--stale-days", type=int, default=None, help="Stale days threshold")
    ui.add_argument("--save-snapshot", action="store_true", help="Save snapshot")
    ui.add_argument("--snapshot-dir", help="Directory for snapshots")
    ui.add_argument("--issue-repo", required=True, help="Repo containing the issue (org/repo)")
    ui.add_argument("--issue-number", required=True, type=int, help="Issue number to update")
    ui.add_argument("--dry-run", action="store_true", help="Print issue body without updating")
    ui.add_argument("--repo-root", help="Path to pr-genius repo root")
    ui.set_defaults(func=cmd_update_issue)

    # ---- auto-ping ----
    ap = sub.add_parser("auto-ping", help="Suggest ping actions for stale PRs (dry-run by default)")
    ap.add_argument("--author", required=True, help="GitHub username")
    ap.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    ap.add_argument("--confirm", action="store_true", help="Actually post ping comments (default: dry-run)")
    ap.add_argument("--repo-root", help="Path to pr-genius repo root")
    ap.set_defaults(func=cmd_auto_ping)

    # ---- auto-rebase ----
    ar = sub.add_parser("auto-rebase", help="Suggest rebase actions for PRs that need it (dry-run by default)")
    ar.add_argument("--author", required=True, help="GitHub username")
    ar.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    ar.add_argument("--confirm", action="store_true", help="Actually attempt rebases via GitHub API (default: dry-run)")
    ar.add_argument("--repo-root", help="Path to pr-genius repo root")
    ar.set_defaults(func=cmd_auto_rebase)

    # ---- dump ----
    dmp = sub.add_parser("dump", help="NDJSON dump of all cases")
    dmp.set_defaults(func=cmd_dump)

    # ---- mcp ----
    m_serve = sub.add_parser("mcp", help="MCP server (stdio)")
    m_serve_sub = m_serve.add_subparsers(dest="mcp_cmd", required=True)
    ms = m_serve_sub.add_parser("serve", help="Run stdio MCP shell")
    ms.set_defaults(func=cmd_mcp_serve)

    # ---- maintainer (v1.5.0) ----
    mv = sub.add_parser(
        "maintainer",
        help="Maintainer view — action decision for a single PR (5 actions: READY_FOR_REVIEW / WAIT_FOR_AUTHOR / CLOSE_DUPLICATE / CLOSE_STALE_OR_RISKY / HOLD_MAINTAINER_DECISION)",
        description=(
            "Maintainer-facing decision: 'What should I do with this PR right now?'\n"
            "Reuses analyze_pr signals, maps to 5 maintainer actions.\n"
            "read-only / advisory-only — never auto-closes, labels, or comments."
        ),
        epilog=(
            "Examples:\n"
            "  prgenius maintainer 'fix: typo' --repo Ikalus1988/MisakaNet\n"
            "  prgenius maintainer 'fix: DCO' --repo org/repo --body 'fixes bug' --author test --format json\n"
        ),
    )
    mv.add_argument("title", help="PR title")
    mv.add_argument("--repo", "-r", required=True, help="Target repo (org/name)")
    mv.add_argument("--body", "-b", default="", help="PR body")
    mv.add_argument("--body-file", default="", help="Read PR body from file")
    mv.add_argument("--description", "-d", default="", help="PR description")
    mv.add_argument("--labels", "-l", nargs="*", default=[], help="PR labels")
    mv.add_argument("--author", "-a", default="", help="PR author")
    mv.add_argument("--author-association", default="NONE", help="Author association")
    mv.add_argument("--star-count", type=int, default=0, help="Repo star count")
    mv.add_argument("--repo-merge-rate", type=float, default=0.0, help="Repo merge rate 0-1")
    mv.add_argument("--format", "-f", choices=["text", "json"], default="text", help="Output format")
    mv.set_defaults(func=cmd_maintainer_view)

    # ---- review-queue (v1.5.0) ----
    rq = sub.add_parser(
        "review-queue",
        help="Build maintainer review queue digest from a list of PRs",
        description=(
            "Aggregate multiple PRs into a maintainer-facing digest grouped by action.\n"
            "Input: --prs-file (JSON list) or stdin (JSON list).\n"
            "Output: --format json|markdown (default markdown).\n"
            "Optional: --write-digest <path> to write git-trackable markdown digest.\n"
            "read-only by default; --write-digest is opt-in."
        ),
        epilog=(
            "Examples:\n"
            "  prgenius review-queue --prs-file open-prs.json --format markdown\n"
            "  cat open-prs.json | prgenius review-queue --write-digest docs/maintainer/pr-review-queue.md\n"
        ),
    )
    rq.add_argument("--prs-file", help="JSON file with PR list [{repo, number, title, body, author, labels}, ...]")
    rq.add_argument("--format", "-f", choices=["json", "markdown"], default="markdown", help="Output format")
    rq.add_argument("--write-digest", help="Write digest to this path (git-trackable, opt-in)")
    rq.set_defaults(func=cmd_review_queue)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
