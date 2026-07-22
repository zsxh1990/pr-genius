"""stdio MCP shell for prgenius — v1.3.0

MCP surface (7 tools, all read-only / non-destructive / idempotent):
- analyze_pr(title, repo, body, ...) → 结构化信号 + 建议 + 三档风险
- coach_pr(title, repo, body, ...) → pass/fail + checklist
- triage_pr(title, repo, body, diff_stat, labels) → verdict + violations + recommended_action
- get_repo_profile(repo) → 仓库画像
- list_open_prs() → open PR 列表
- get_case_study(repo, pr_number) → PR 案例
- search_patterns(query, type, limit) → 按关键词搜 anti-patterns + success-patterns
- schema_info() → schema 版本

All tools follow MCP tool annotations (readOnlyHint=True, destructiveHint=False,
idempotentHint=True) — pr-genius 是只读 advisor, 不写任何状态.
"""
from __future__ import annotations
import sys
from pathlib import Path

REPO_ROOT_DEFAULT = Path(__file__).resolve().parents[3]


def _load_tools(repo_root: Path | None = None):
    from mcp.server.fastmcp import FastMCP
    from .parser import iter_case_studies, profile_get, schema_info as _schema_info
    from .evaluator import analyze_pr as _analyze_pr, eval_pr as _eval_pr
    from .triage import triage_pr as _triage_pr

    mcp = FastMCP(name="prgenius", instructions=(
        "PR Genius — Evidence-backed PR contribution advisor. "
        "analyze_pr 分析 PR 并给出改进建议, coach_pr 用于 Agent PR Dojo (pass/fail), "
        "triage_pr 做 policy-aware screening. 所有 tools 只读 — pr-genius 不写任何状态."
    ))

    rr = repo_root or REPO_ROOT_DEFAULT

    # Tool annotations: 全是只读 advisor (M1 克莱恩 2026-07-19)
    READ_ONLY = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}

    @mcp.tool(annotations=READ_ONLY)
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

    @mcp.tool(annotations=READ_ONLY)
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

    @mcp.tool(annotations=READ_ONLY)
    def triage_pr(
        title: str,
        repo: str,
        body: str = "",
        diff_stat: str = "",
        labels: list[str] | None = None,
    ) -> dict:
        """Policy-aware PR triage — M1 克莱恩 2026-07-19 新增.

        Reads docs/policies/<org>-<repo>.md and checks the PR against hard/soft rules.

        返回:
            verdict: pass / needs_preflight / warn / reject
            policy_loaded: bool
            violations: list of {rule, severity, evidence}
            generic_checks: list (only when needs_preflight)
            recommended_action: str (always)

        Example:
            triage_pr("docs: typo", "Ikalus1988/MisakaNet", "fix typo", "docs/faq.md | 3 ++-")
            → {verdict: "pass", policy_loaded: true, ...}

            triage_pr("docs: add installation", "pallets/flask", ...)
            → {verdict: "needs_preflight", generic_checks: [...6 items...], ...}
        """
        # 35 期评测反哺 (lesson-21): 底层 _triage_pr (triage.py:318) 不收 labels kwarg.
        # 之前 wrapper 传 labels=labels or [] 会 TypeError. 现在传空 list (policy 检查
        # 暂未用 labels, 后续若底层支持再补).
        result = _triage_pr(
            title=title,
            repo=repo,
            body=body,
            diff_stat=diff_stat,
            repo_root=rr,
        )
        # 补 recommended_action 字段 (M1 评估要求)
        verdict = result.get("verdict", "unknown")
        if verdict == "pass":
            result["recommended_action"] = "safe_to_review"
        elif verdict == "warn":
            # 35 期评测反哺 (lesson-21): triage.py 返回的是 int count,不是 list
            n_soft = int(result.get("soft_violations", 0))
            result["recommended_action"] = f"needs_human_review ({n_soft} soft rule(s))"
        elif verdict == "reject":
            # 35 期评测反哺 (lesson-21): 同上,读 int count
            n_hard = int(result.get("hard_violations", 0))
            result["recommended_action"] = f"blocked_by_policy ({n_hard} hard rule(s))"
        elif verdict == "needs_preflight":
            result["recommended_action"] = (
                "no_policy_for_repo — run generic preflight checks before opening PR"
            )
        else:
            result["recommended_action"] = f"unknown_verdict ({verdict})"
        return result

    @mcp.tool(annotations=READ_ONLY)
    def get_repo_profile(repo: str) -> dict:
        """返回仓库画像 (org/name)。"""
        p = profile_get(rr, repo)
        if p is None:
            return {"error": f"profile not found: {repo}"}
        return p["frontmatter"]

    @mcp.tool(annotations=READ_ONLY)
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

    @mcp.tool(annotations=READ_ONLY)
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

    @mcp.tool(annotations=READ_ONLY)
    def search_patterns(
        query: str,
        pattern_type: str = "all",
        limit: int = 10,
    ) -> list:
        """按关键词搜 anti-patterns + success-patterns (M1 克莱恩 2026-07-19 新增).

        Args:
            query: 搜的关键词 (e.g. "duplicate PR", "missing tests", "out of scope")
            pattern_type: "all" / "anti-pattern" / "success-pattern"
            limit: 最多返回几条 (默认 10)

        Returns: list of {key, title, symptom, fix_action, source_pr, type}
        """
        # 35 期评测反哺 (lesson-21): _parse_frontmatter_dict 是死导入
        # (ether2 SMOKE_RESULTS.md §1.4: cannot import name '_parse_frontmatter_dict')
        # 改用现存的 parse_frontmatter (parser.py:96) — 它返回完整 dict
        from .parser import parse_frontmatter
        results = []

        patterns_dirs = []
        if pattern_type in ("all", "anti-pattern"):
            patterns_dirs.append((rr / "anti-patterns", "anti-pattern"))
        if pattern_type in ("all", "success-pattern"):
            patterns_dirs.append((rr / "success-patterns", "success-pattern"))

        query_lower = query.lower()
        for pdir, ptype in patterns_dirs:
            if not pdir.exists():
                continue
            for f in pdir.glob("*.md"):
                if f.name == "README.md":
                    continue
                content = f.read_text(encoding="utf-8")
                if query_lower not in content.lower():
                    continue
                # Parse frontmatter — 用 parser.py 现存函数 (lesson-21)
                fm = parse_frontmatter(content)
                if not fm:
                    continue
                fm["type"] = ptype
                fm["file"] = str(f.relative_to(rr))
                results.append(fm)

        return results[:limit]

    @mcp.tool(annotations=READ_ONLY)
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
