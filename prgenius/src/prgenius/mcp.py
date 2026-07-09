"""stdio MCP shell for prgenius — a thin façade.

This module is optional: only loaded if `mcp` is installed (the only runtime
dependency we ever take). Calling `python3 -m prgenius mcp serve` starts a
stdio MCP server that exposes the prgenius lookup surface to local agents
(Cursor/Cline/Claude Code). No network, no auth, no rate-limiting.

Promoted tools (intentionally small — ACD rule "first to simplify wins"):
- get_repo_profile(repo) → returns one Repo Profile dict
- list_open_prs() → list of PRs with final_status=open
- get_case_study(repo, pr_number) → one PR Case Study
- schema_info() → enumerated schema versions

This file is ~70 lines (one per tool + boilerplate). Anyone reading it should
be able to verify the surface and the path-resolution logic in under 5 min.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

# mcp SDK: only imported at serve() time so the rest of the package stays stdlib.
REPO_ROOT_DEFAULT = Path(__file__).resolve().parents[3]  # up to big-repo-pr-knowledge


def _load_tools(repo_root: Path | None = None):
    from mcp.server.fastmcp import FastMCP
    from .parser import (
        iter_case_studies,
        profile_get,
        schema_info,
    )
    from .evaluator import eval_pr, suggest_pr

    mcp = FastMCP(name="prgenius", instructions=(
        "Evidence-backed lookup for big-repo PR contributions. "
        "Local stdio; no network calls."
    ))

    rr = repo_root or REPO_ROOT_DEFAULT

    @mcp.tool()
    def get_repo_profile(repo: str) -> dict:
        """Return one Repo Profile by `org/name` (e.g. astral-sh/uv)."""
        p = profile_get(rr, repo)
        if p is None:
            return {"error": f"profile not found: {repo}"}
        return p["frontmatter"]

    @mcp.tool()
    def list_open_prs() -> list:
        """List every PR Case Study with final_status=open."""
        out = []
        for c in iter_case_studies(rr):
            fm = c["frontmatter"]
            if fm.get("final_status") == "open":
                out.append({
                    "repo": fm.get("repo"),
                    "pr_number": fm.get("pr_number"),
                    "pr_url": fm.get("pr_url"),
                    "folder": c["folder"],
                    "schema_version": fm.get("schema_version", "legacy v0.1"),
                    "verified_at": fm.get("verified_at"),
                })
        return out

    @mcp.tool()
    def get_case_study(repo: str, pr_number: int) -> dict:
        """Return one PR Case Study by `org/name` + `pr_number`."""
        for c in iter_case_studies(rr):
            fm = c["frontmatter"]
            if (
                fm.get("repo", "").strip("/").lower() == repo.strip("/").lower()
                and str(fm.get("pr_number")) == str(pr_number)
            ):
                return {
                    "frontmatter": fm,
                    "body": c["body"],
                    "path": c["path"],
                }
        return {"error": f"case study not found: {repo}#{pr_number}"}

    @mcp.tool()
    def schema_info() -> dict:
        """Return supported schema versions + enum values."""
        return schema_info()

    @mcp.tool()
    def eval_pr(title: str, description: str, repo: str) -> dict:
        """评估 PR 成功率，检查反模式和成功模式"""
        return eval_pr(title, description, repo, rr)

    @mcp.tool()
    def suggest_pr(title: str, description: str, repo: str) -> dict:
        """生成改进建议"""
        return suggest_pr(title, description, repo, rr)

    return mcp


def serve(repo_root: Path | None = None) -> int:
    """Run stdio MCP server. Blocks until the host disconnects.

    Args:
        repo_root: Override the knowledge base location. If None, uses
            the auto-detected default (parents[3] of this file).
    """
    mcp = _load_tools(repo_root=repo_root)
    mcp.run(transport="stdio")
    return 0


if __name__ == "__main__":
    sys.exit(serve())
