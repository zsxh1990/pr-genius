"""stdio MCP shell for prgenius — v1.1.1

MCP surface:
- analyze_pr(title, repo, body, ...) → 结构化信号 + 建议 + 三档风险
- coach_pr(title, repo, body, ...) → pass/fail + checklist
- get_repo_profile(repo) → 仓库画像
- list_open_prs() → open PR 列表
- get_case_study(repo, pr_number) → PR 案例
- schema_info() → schema 版本
"""
from __future__ import annotations
import sys
from pathlib import Path

REPO_ROOT_DEFAULT = Path(__file__).resolve().parents[3]


def _load_tools(repo_root: Path | None = None):
    from mcp.server.fastmcp import FastMCP
    from .parser import iter_case_studies, profile_get, schema_info as _schema_info
    from .evaluator import analyze_pr as _analyze_pr, eval_pr as _eval_pr

    mcp = FastMCP(name="prgenius", instructions=(
        "PR Genius — 提交前改进顾问。"
        "analyze_pr 分析 PR 并给出改进建议，coach_pr 用于 Agent PR Dojo (pass/fail)。"
    ))

    rr = repo_root or REPO_ROOT_DEFAULT

    @mcp.tool()
    def analyze_pr(
        title: str,
        repo: str,
        body: str = "",
        description: str = "",
        author: str = "",
        author_association: str = "NONE",
        labels: list[str] | None = None,
        star_count: int = 0,
        repo_merge_rate: float = 0.0,
    ) -> dict:
        """分析 PR 并生成结构化改进建议。

        返回 tier (low_risk/medium_risk/high_risk)、signals (positive/negative/neutral)、checklist。
        """
        return _analyze_pr(
            title, description, repo, rr,
            body=body, labels=labels or [], author=author,
            star_count=star_count, repo_merge_rate=repo_merge_rate,
            author_association=author_association,
        )

    @mcp.tool()
    def coach_pr(
        title: str,
        repo: str,
        body: str = "",
        description: str = "",
        author: str = "",
        author_association: str = "NONE",
        labels: list[str] | None = None,
        star_count: int = 0,
        repo_merge_rate: float = 0.0,
    ) -> dict:
        """Agent PR Dojo: 返回 pass/fail + checklist。

        pass=true 表示可以提交，pass=false 表示有阻塞问题需先修复。
        """
        result = _analyze_pr(
            title, description, repo, rr,
            body=body, labels=labels or [], author=author,
            star_count=star_count, repo_merge_rate=repo_merge_rate,
            author_association=author_association,
        )
        result["pass"] = result["tier"] != "high_risk"
        return result

    @mcp.tool()
    def get_repo_profile(repo: str) -> dict:
        """返回仓库画像 (org/name)。"""
        p = profile_get(rr, repo)
        if p is None:
            return {"error": f"profile not found: {repo}"}
        return p["frontmatter"]

    @mcp.tool()
    def list_open_prs() -> list:
        """列出所有 final_status=open 的 PR Case Study。"""
        out = []
        for c in iter_case_studies(rr):
            fm = c["frontmatter"]
            if fm.get("final_status") == "open":
                out.append({
                    "repo": fm.get("repo"),
                    "pr_number": fm.get("pr_number"),
                    "pr_url": fm.get("pr_url"),
                    "folder": c["folder"],
                })
        return out

    @mcp.tool()
    def get_case_study(repo: str, pr_number: int) -> dict:
        """返回单个 PR Case Study。"""
        for c in iter_case_studies(rr):
            fm = c["frontmatter"]
            if (
                fm.get("repo", "").strip("/").lower() == repo.strip("/").lower()
                and str(fm.get("pr_number")) == str(pr_number)
            ):
                return {"frontmatter": fm, "body": c["body"], "path": c["path"]}
        return {"error": f"case study not found: {repo}#{pr_number}"}

    @mcp.tool()
    def schema_info() -> dict:
        """返回支持的 schema 版本和枚举值。"""
        return _schema_info()

    return mcp


def serve(repo_root: Path | None = None) -> int:
    """Run stdio MCP server. Blocks until the host disconnects."""
    mcp = _load_tools(repo_root=repo_root)
    mcp.run(transport="stdio")
    return 0


if __name__ == "__main__":
    sys.exit(serve())
