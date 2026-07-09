"""CLI entry point for `prgenius`.

Usage examples (run from repo root):
    python3 -m prgenius profile get astral-sh/uv
    python3 -m prgenius case list --status=open
    python3 -m prgenius schema info
    python3 -m prgenius dump --format=ndjson  > cases.ndjson
    python3 -m prgenius eval "fix: update deps" --repo langchain-ai/langchain --author "dependabot[bot]" --labels "dependencies"
    python3 -m prgenius mcp serve  # stdio MCP shell
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .parser import (
    iter_profiles,
    iter_case_studies,
    profile_get,
    schema_info,
)
from .evaluator import eval_pr, suggest_pr


REPO_ROOT_DEFAULT = Path(__file__).resolve().parents[3]  # up to big-repo-pr-knowledge


def _get_repo_root(args) -> Path:
    if args.repo_root:
        return Path(args.repo_root).resolve()
    return REPO_ROOT_DEFAULT


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
    """Dump everything in NDJSON (one PR per line) for benchmark use."""
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


def cmd_eval(args) -> int:
    """评估 PR"""
    repo_root = _get_repo_root(args)
    labels = args.labels if args.labels else []
    result = eval_pr(
        args.title, args.description, args.repo, repo_root,
        body=args.body or "",
        labels=labels,
        author=args.author or "",
        star_count=args.star_count or 0,
        repo_merge_rate=args.repo_merge_rate or 0.0,
        author_association=args.author_association or "NONE",
    )

    output = []
    output.append("## PR 评估结果\n")

    # Bot 标记
    if result.get("is_bot"):
        output.append("🤖 **Bot PR** — 走独立评估通道\n\n")

    output.append(f"### 成功率预测: {result['success_rate']:.0%} ({result['success_level']})\n")

    # 标签信号
    if result.get("labels"):
        from .evaluator import compute_label_score
        label_score = compute_label_score(result["labels"])
        if label_score != 0:
            signal = "正面" if label_score > 0 else "负面"
            output.append(f"### 标签信号: {signal} ({label_score:+.0f} 分)\n")
            output.append(f"标签: {', '.join(result['labels'])}\n\n")

    # 反模式命中
    if result['anti_patterns']:
        output.append("### 反模式命中\n")
        for match in result['anti_patterns']:
            output.append(f"- ⚠️ **{match['key']}**: {match.get('symptom', '未知')}\n")
            if match.get('fix_action'):
                output.append(f"  - 建议: {match['fix_action']}\n")
            if match.get('source_pr'):
                output.append(f"  - 历史案例: {match['source_pr']}\n")
        output.append("")
    else:
        output.append("### 反模式命中\n")
        output.append("- ✅ 未命中任何反模式\n\n")

    # 成功模式匹配
    if result['success_patterns']:
        output.append("### 成功模式匹配\n")
        for match in result['success_patterns']:
            output.append(f"- ✅ **{match['key']}**: {match.get('description', '')}\n")
        output.append("")
    else:
        output.append("### 成功模式匹配\n")
        output.append("- ❌ 未匹配任何成功模式\n\n")

    # 改进建议
    if result['suggestions']:
        output.append("### 改进建议\n")
        output.extend(result['suggestions'])

    print("".join(output))
    return 0


def cmd_suggest(args) -> int:
    """生成改进建议"""
    repo_root = _get_repo_root(args)
    labels = args.labels if args.labels else []
    result = suggest_pr(
        args.title, args.description, args.repo, repo_root,
        body=args.body or "",
        labels=labels,
        author=args.author or "",
    )

    output = []
    output.append("## 改进建议\n")
    output.extend(result['suggestions'])

    print("".join(output))
    return 0


def cmd_mcp_serve(args) -> int:
    """stdio MCP shell. See prgenius/mcp.py for the small facade.

    Pass --repo-root to point the MCP server at a non-default location
    (e.g. an isolated worktree or a forked copy of the knowledge base).
    """
    from .mcp import serve
    repo_root = _get_repo_root(args)
    return serve(repo_root=repo_root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="prgenius",
        description="Evidence-backed lookup for big-repo PR contributions.",
    )
    parser.add_argument("--repo-root", help="Path to big-repo-pr-knowledge (default: auto-detect)")
    parser.add_argument("--version", action="version", version=f"prgenius {__version__}")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_get = sub.add_parser("profile", help="Profile operations")
    p_get_sub = p_get.add_subparsers(dest="profile_cmd", required=True)
    pp = p_get_sub.add_parser("get", help="Get one profile")
    pp.add_argument("repo", help="org/name (e.g. astral-sh/uv)")
    pp.set_defaults(func=cmd_profile_get)

    c_list = sub.add_parser("case", help="Case study operations")
    c_list_sub = c_list.add_subparsers(dest="case_cmd", required=True)
    cl = c_list_sub.add_parser("list", help="List case studies")
    cl.add_argument("--status", help="Filter by final_status (open/merged/...)")
    cl.set_defaults(func=cmd_case_list)

    s_info = sub.add_parser("schema", help="Schema info")
    s_info_sub = s_info.add_subparsers(dest="schema_cmd", required=True)
    si = s_info_sub.add_parser("info", help="Show supported schema versions")
    si.set_defaults(func=cmd_schema_info)

    dmp = sub.add_parser("dump", help="NDJSON dump of all cases (for benchmarks)")
    dmp.set_defaults(func=cmd_dump)

    # eval 命令 — 新增 --body, --labels, --author, --star-count
    ev = sub.add_parser("eval", help="评估 PR")
    ev.add_argument("title", help="PR 标题")
    ev.add_argument("--description", "-d", default="", help="PR 描述")
    ev.add_argument("--body", "-b", default="", help="PR body (完整内容)")
    ev.add_argument("--repo", "-r", required=True, help="目标仓库 (org/repo)")
    ev.add_argument("--labels", "-l", nargs="*", default=[], help="PR 标签列表")
    ev.add_argument("--author", "-a", default="", help="PR 作者")
    ev.add_argument("--star-count", type=int, default=0, help="仓库 star 数")
    ev.add_argument("--repo-merge-rate", type=float, default=0.0, help="仓库历史 merge 率 (0-1)")
    ev.add_argument("--author-association", default="NONE", help="作者身份 (NONE/CONTRIBUTOR/COLLABORATOR/MEMBER/OWNER)")
    ev.set_defaults(func=cmd_eval)

    # suggest 命令 — 同样新增参数
    sg = sub.add_parser("suggest", help="获取改进建议")
    sg.add_argument("title", help="PR 标题")
    sg.add_argument("--description", "-d", default="", help="PR 描述")
    sg.add_argument("--body", "-b", default="", help="PR body")
    sg.add_argument("--repo", "-r", required=True, help="目标仓库 (org/repo)")
    sg.add_argument("--labels", "-l", nargs="*", default=[], help="PR 标签列表")
    sg.add_argument("--author", "-a", default="", help="PR 作者")
    sg.set_defaults(func=cmd_suggest)

    m_serve = sub.add_parser("mcp", help="MCP server (stdio)")
    m_serve_sub = m_serve.add_subparsers(dest="mcp_cmd", required=True)
    ms = m_serve_sub.add_parser("serve", help="Run stdio MCP shell")
    ms.set_defaults(func=cmd_mcp_serve)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
