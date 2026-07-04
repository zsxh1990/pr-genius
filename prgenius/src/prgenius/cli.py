"""CLI entry point for `prgenius`.

Usage examples (run from repo root):
    python3 -m prgenius profile get astral-sh/uv
    python3 -m prgenius case list --status=open
    python3 -m prgenius schema info
    python3 -m prgenius dump --format=ndjson  > cases.ndjson
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


def cmd_dump(_args) -> int:
    """Dump everything in NDJSON (one PR per line) for benchmark use."""
    root = REPO_ROOT_DEFAULT if not _args.repo_root else Path(_args.repo_root)
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


def cmd_mcp_serve(_args) -> int:
    """stdio MCP shell. See prgenius/mcp.py for the small facade."""
    from .mcp import serve
    serve()


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

    m_serve = sub.add_parser("mcp", help="MCP server (stdio)")
    m_serve_sub = m_serve.add_subparsers(dest="mcp_cmd", required=True)
    ms = m_serve_sub.add_parser("serve", help="Run stdio MCP shell")
    ms.set_defaults(func=cmd_mcp_serve)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
