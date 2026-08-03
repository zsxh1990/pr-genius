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
    # 35 期评测反哺 (lesson-21 续): eval_pr 是死导入 — mcp.py 内部未调用
    # 保留给 cli.py (line 192) 使用, 这里只 import analyze_pr
    from .evaluator import analyze_pr as _analyze_pr
    from .triage import triage_pr as _triage_pr

    mcp = FastMCP(name="pr-genius", instructions=(
        "PR Genius — Evidence-backed PR contribution advisor. "
        "analyze_pr 分析 PR 并给出改进建议, coach_pr 用于 Agent PR Dojo (pass/fail), "
        "triage_pr 做 policy-aware screening. 所有 tools 只读 — pr-genius 不写任何状态."
    ))

    rr = Path(repo_root) if repo_root else REPO_ROOT_DEFAULT

    # Tool annotations: all read-only advisor
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
        """Detailed PR analysis with signals and checklist. Use analyze_pr for deep analysis, coach_pr for quick pass/fail.

        Returns: tier (low_risk/medium_risk/high_risk), signals (positive/negative/neutral),
        checklist (P0/P1/P2 items), and recommended_action.

        Use this before submitting a PR to a large open-source repo to check if your
        contribution strategy is sound. Combines repo profile data, anti-pattern matching,
        and success pattern analysis.

        Args:
            title: PR title (e.g. "feat: add new search endpoint")
            repo: Target repo in org/name format (e.g. "encode/httpx")
            body: PR body/description text
            description: Extended description (optional)
            author: PR author username
            author_association: Author's association with repo (NONE/CONTRIBUTOR/COLLABORATOR/MEMBER/OWNER)
            labels: PR labels (e.g. ["bug", "documentation"])
            star_count: Repository star count (0 = unknown)
            repo_merge_rate: Repository's external PR merge rate 0.0-1.0 (0 = unknown)

        Returns:
            dict with keys: tier, signals, checklist, recommended_action, repo, title

        Example:
            analyze_pr("fix: timeout in connection pool", "encode/httpx", "Fixes #123")
            → {"tier": "medium_risk", "signals": {...}, "checklist": [...], "recommended_action": "..."}
        """
        # Auto-read from profile if not provided
        if star_count == 0 or repo_merge_rate == 0.0:
            from .parser import profile_get
            profile = profile_get(rr, repo)
            if profile:
                fm = profile.get("frontmatter", {})
                gl = fm.get("agent_guidelines", {})
                if star_count == 0:
                    star_count = fm.get("star", 0)
                if repo_merge_rate == 0.0:
                    repo_merge_rate = gl.get("external_merge_rate_30", gl.get("external_merge_rate", 0.0))

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
        """Agent PR Dojo: quick pass/fail gate. Use coach_pr for go/no-go decision, analyze_pr for detailed analysis.

        Use this as a final gate before opening a PR. Returns pass=true if safe
        to submit, pass=false if there are blocking issues to fix first.

        Combines repo profile analysis, anti-pattern matching, and maintainer
        policy checks into a single go/no-go decision.

        Args:
            title: PR title
            repo: Target repo (org/name)
            body: PR body/description
            description: Extended description
            author: PR author username
            author_association: Author's association (NONE/CONTRIBUTOR/etc.)
            labels: PR labels
            star_count: Repo star count
            repo_merge_rate: External PR merge rate (0.0-1.0)

        Returns:
            dict with pass (bool), tier, signals, checklist, recommended_action
        """
        # Auto-read from profile if not provided
        if star_count == 0 or repo_merge_rate == 0.0:
            from .parser import profile_get
            profile = profile_get(rr, repo)
            if profile:
                fm = profile.get("frontmatter", {})
                gl = fm.get("agent_guidelines", {})
                if star_count == 0:
                    star_count = fm.get("star", 0)
                if repo_merge_rate == 0.0:
                    repo_merge_rate = gl.get("external_merge_rate_30", gl.get("external_merge_rate", 0.0))

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
        """Policy-aware PR screening.

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
        """Get repository profile with maintainer guidelines, AI policy, and merge rate.

        Returns 17 agent_guidelines fields including ai_policy, maintainer_vibe,
        external_merge_rate, close_keywords, and more. Use this to understand a
        repo's contribution culture before submitting a PR.

        Args:
            repo: Repository in org/name format (e.g. "encode/httpx")

        Returns:
            dict with repo metadata and agent_guidelines, or error if not found
        """
        p = profile_get(rr, repo)
        if p is None:
            return {"error": f"profile not found: {repo}"}
        return p["frontmatter"]

    @mcp.tool(annotations=READ_ONLY)
    def list_open_prs() -> list:
        """List all open PR case studies in the knowledge base.

        Returns PRs with final_status=open, useful for tracking ongoing
        contributions and their current state.

        Returns:
            list of {repo, pr_number, pr_url, folder} for each open PR
        """
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
        """Get a specific PR case study with full details and rounds.

        Returns the complete case study including frontmatter, body text,
        and round-by-round interaction history. Useful for learning from
        past PR experiences.

        Args:
            repo: Repository in org/name format
            pr_number: PR number (integer)

        Returns:
            dict with frontmatter, body, path, or error if not found
        """
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
        """Search anti-patterns and success-patterns by keyword.

        Use this to find relevant patterns before submitting a PR.
        Anti-patterns show what NOT to do, success-patterns show what works.

        Args:
            query: Search keyword (e.g. "duplicate PR", "missing tests", "out of scope", "breaking change")
            pattern_type: Filter type — "all" (default), "anti-pattern", or "success-pattern"
            limit: Max results to return (default 10)

        Returns:
            list of dicts with keys: key, title, symptom, fix_action, source_pr, type, file

        Example:
            search_patterns("duplicate PR") → finds anti-patterns about duplicate submissions
            search_patterns("timeout", "anti-pattern") → finds timeout-related failure patterns
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

        import json as _json
        query_lower = query.lower()
        for pdir, ptype in patterns_dirs:
            if not pdir.exists():
                continue
            # Search .md files
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
            # Search .json files (from API/automation)
            for f in pdir.glob("*.json"):
                try:
                    content = f.read_text(encoding="utf-8")
                    if query_lower not in content.lower():
                        continue
                    data = _json.loads(content)
                    if isinstance(data, dict) and "id" in data:
                        fm = {
                            "key": data.get("id", f.stem),
                            "title": data.get("title", data.get("description", "")),
                            "type": ptype,
                            "file": str(f.relative_to(rr)),
                        }
                        results.append(fm)
                except Exception:
                    continue

        return results[:limit]

    @mcp.tool(annotations=READ_ONLY)
    def schema_info() -> dict:
        """返回支持的 schema 版本和枚举值。"""
        return _schema_info()

    @mcp.tool(annotations=READ_ONLY)
    def status_prs(
        author: str | None = None,
        repo: str | None = None,
        stale_days: int | None = None,
    ) -> dict:
        """Check health of in-flight PRs (outbound PR heartbeat).

        Classifies open PRs into 9 statuses: NEEDS_REBASE, CI_FAILING,
        STALE_REVIEW, CHANGES_REQUESTED, STALE_NO_REVIEW, BLOCKED,
        CLEAN, UNKNOWN, WAITING. Suggests actions for each.

        Args:
            author: GitHub username to check PRs for
            repo: Repository to check (org/name)
            stale_days: Days without update to consider stale (default: profile or 14)

        Returns:
            dict with prs, ignored, summary, actions, transitions
        """
        from .status import check_status
        if not author and not repo:
            return {"error": "specify author or repo"}
        try:
            return check_status(
                author=author,
                repo=repo,
                stale_days=stale_days,
                repo_root=rr,
                save_snapshot=True,
            )
        except RuntimeError as e:
            return {"error": str(e)}

    @mcp.tool(annotations=READ_ONLY)
    def profile_writeback_suggestions(
        author: str,
        mode: str = "suggest",
    ) -> list:
        """Get profile writeback suggestions based on PR status analysis.

        Analyzes PR health data and suggests profile updates (e.g.,
        stale_days_threshold, response_time). Returns suggestions with
        evidence, source, and confidence score.

        Args:
            author: GitHub username
            mode: 'suggest' (all suggestions) or 'auto' (confidence >= 0.8 only)

        Returns:
            list of {field, value, repo, evidence, source, confidence, private}
        """
        from .status import check_status, suggest_profile_writeback
        try:
            result = check_status(author=author, repo_root=rr, save_snapshot=False)
            return suggest_profile_writeback(result, repo_root=rr, mode=mode)
        except RuntimeError as e:
            return [{"error": str(e)}]

    return mcp


def serve(repo_root: Path | None = None) -> int:
    """Run stdio MCP server. Blocks until the host disconnects."""
    mcp = _load_tools(repo_root=repo_root)
    mcp.run(transport="stdio")
    return 0


if __name__ == "__main__":
    sys.exit(serve())
