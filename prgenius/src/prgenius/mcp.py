"""stdio MCP shell for prgenius — v1.4.1

MCP surface (13 tools, all read-only / non-destructive / idempotent):
- analyze_pr(title, repo, body, ..., diff_stat) → 结构化信号 + 建议 + 三档风险
- coach_pr(title, repo, body, ..., diff_stat) → pass/fail + checklist
- triage_pr(title, repo, body, diff_stat, labels) → verdict + violations + fallback_signals
- get_repo_profile(repo) → 仓库画像
- list_open_prs(repo, author) → 本地 case-study 记录 (不是 GitHub 实时 PR; 实时的用 status_prs)
- get_case_study(repo, pr_number) → PR 案例
- search_patterns(query, type, limit) → 按关键词搜 anti-patterns + success-patterns
- schema_info() → schema 版本
- status_prs(author, repo, stale_days, save_snapshot) → outbound PR health check
- profile_writeback_suggestions(author, mode) → profile update proposals
- prgenius_doctor() → 安装/数据/MCP 自检 (issue #70)

All tools follow MCP tool annotations (readOnlyHint=True, destructiveHint=False,
idempotentHint=True) — pr-genius 是只读 advisor, 不写任何状态.
"""
from __future__ import annotations
import sys
from pathlib import Path

from .utils import get_repo_root

REPO_ROOT_DEFAULT = get_repo_root()

# issue #72: CLI and MCP enforce the same value domains — impossible values
# must fail loudly before analysis, not produce meaningless output.
_AUTHOR_ASSOCIATIONS = {"NONE", "CONTRIBUTOR", "COLLABORATOR", "MEMBER", "OWNER"}
_MERGEABLE_STATES = {"MERGEABLE", "CONFLICTING", "UNKNOWN"}


def _validate_pr_args(
    star_count: int,
    repo_merge_rate: float,
    author_association: str,
    mergeable: str,
) -> None:
    """Raise ValueError on impossible argument values (issue #72)."""
    if not isinstance(star_count, int) or isinstance(star_count, bool) or star_count < 0:
        raise ValueError(f"star_count must be an integer >= 0, got {star_count!r}")
    if not isinstance(repo_merge_rate, (int, float)) or isinstance(repo_merge_rate, bool) \
            or not 0.0 <= float(repo_merge_rate) <= 1.0:
        raise ValueError(f"repo_merge_rate must be a number in [0.0, 1.0], got {repo_merge_rate!r}")
    if author_association not in _AUTHOR_ASSOCIATIONS:
        raise ValueError(
            f"author_association must be one of {sorted(_AUTHOR_ASSOCIATIONS)}, "
            f"got {author_association!r}"
        )
    if mergeable not in _MERGEABLE_STATES:
        raise ValueError(
            f"mergeable must be one of {sorted(_MERGEABLE_STATES)}, got {mergeable!r}"
        )


def _profile_merge_rate(gl: dict) -> float:
    """从 profile 的 agent_guidelines 取数值合并率 (issue #68)。

    profiles 里 `external_merge_rate` 是数字, `external_merge_rate_30` 常是
    URL 字符串 — 只认真正的数值, 数字键优先, 避免把 URL 当合并率传下去。
    """
    from .evaluator import coerce_merge_rate
    for key in ("external_merge_rate", "external_merge_rate_30", "merge_rate"):
        rate = coerce_merge_rate(gl.get(key, 0.0))
        if rate > 0:
            return rate
    return 0.0


def _load_tools(repo_root: Path | None = None):
    # mcp 2.x 把 FastMCP 改名为 MCPServer (mcp.server.mcpserver)。
    # 两个版本都支持, 不逼用户立刻升级: 1.x 仍是 `mcp>=1,<2` 的默认解析结果,
    # 2.x 是新装的形态。构造器 / @tool / run(transport=) 三者签名一致, 所以
    # 只有类名与导入路径不同。`_tool_manager._tools` 两个版本都是 dict ——
    # doctor 的内省无需分叉。
    try:  # mcp 2.x
        from mcp.server import MCPServer as _McpServer
    except ImportError:  # mcp 1.x
        from mcp.server.fastmcp import FastMCP as _McpServer
    from .parser import iter_case_studies, profile_get, schema_info as _schema_info
    # 35 期评测反哺 (lesson-21 续): eval_pr 是死导入 — mcp.py 内部未调用
    # 保留给 cli.py (line 192) 使用, 这里只 import analyze_pr
    from .evaluator import analyze_pr as _analyze_pr
    from .triage import triage_pr as _triage_pr

    mcp = _McpServer(name="pr-genius", instructions=(
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
        mergeable: str = "MERGEABLE",
        diff_stat: str = "",
        diff: str = "",
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
            star_count: Repository star count (>= 0; 0 = unknown)
            repo_merge_rate: Repository's external PR merge rate 0.0-1.0 (0 = unknown)
            mergeable: Mergeable state (MERGEABLE/CONFLICTING/UNKNOWN)
            diff_stat: git diff --stat output — populates impact/review and is
                the authoritative PR-size signal (null when omitted). Summary
                counts only: PR **size** is derived from these counts (or title
                keywords when omitted).
            diff: unified diff **body** (optional). When given, a keyword pass
                runs over its added lines and reports install commands, downloads
                piped to a shell, and secret-shaped strings — see
                `result["diff_scan"]`. Omitting it is a declared absence
                (`diff_scanned: false`), not a silent empty result. This is a
                keyword pass, not a review, and it makes no network call: it
                cannot say whether a package exists on PyPI/npm.

        Returns:
            dict with keys: tier, signals, checklist, recommended_action, repo,
            title, impact, review (impact/review null without diff_stat)

        Example:
            analyze_pr("fix: timeout in connection pool", "encode/httpx", "Fixes #123")
            → {"tier": "medium_risk", "signals": {...}, "checklist": [...], "recommended_action": "..."}
        """
        _validate_pr_args(star_count, repo_merge_rate, author_association, mergeable)
        from . import telemetry as _telemetry
        _telemetry.record("mcp.analyze_pr")

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
                    repo_merge_rate = _profile_merge_rate(gl)

        result = _analyze_pr(
            title, description, repo, rr,
            body=body, labels=labels or [], author=author,
            star_count=star_count, repo_merge_rate=repo_merge_rate,
            author_association=author_association,
            mergeable=mergeable,
            diff_stat=diff_stat,
            diff=diff or None,
        )
        if result.get("diff_scan", {}).get("findings"):
            _telemetry.record(
                "mcp.analyze_pr.patterns",
                patterns=[f.get("family", "unknown") for f in result["diff_scan"]["findings"]],
            )
        return result

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
        mergeable: str = "MERGEABLE",
        diff_stat: str = "",
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
            star_count: Repo star count (>= 0)
            repo_merge_rate: External PR merge rate (0.0-1.0)
            mergeable: Mergeable state (MERGEABLE/CONFLICTING/UNKNOWN)
            diff_stat: git diff --stat output (populates impact/review; summary
                counts only — diff content/hunks are never analyzed)

        Returns:
            dict with pass (bool), tier, signals, checklist, recommended_action
        """
        _validate_pr_args(star_count, repo_merge_rate, author_association, mergeable)
        from . import telemetry as _telemetry
        _telemetry.record("mcp.coach_pr")

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
                    repo_merge_rate = _profile_merge_rate(gl)

        result = _analyze_pr(
            title, description, repo, rr,
            body=body, labels=labels or [], author=author,
            star_count=star_count, repo_merge_rate=repo_merge_rate,
            author_association=author_association,
            mergeable=mergeable,
            diff_stat=diff_stat,
        )
        if result.get("diff_scan", {}).get("findings"):
            _telemetry.record(
                "mcp.coach_pr.patterns",
                patterns=[f.get("family", "unknown") for f in result["diff_scan"]["findings"]],
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
    def list_open_prs(repo: str = "", author: str = "") -> list:
        """List open PR **case-study records** in the local knowledge base (issue #74).

        NOTE: these are local case-study folders with final_status=open —
        NOT live GitHub PRs. For live GitHub PR health use `status_prs`.

        Args:
            repo: filter by target repo (org/name, e.g. "encode/httpx"); "" = all
            author: filter by PR author username; "" = all

        Returns:
            list of {repo, pr_number, pr_url, author, folder} for each matching
            open case study
        """
        out = []
        for c in iter_case_studies(rr):
            fm = c["frontmatter"]
            if fm.get("final_status") != "open":
                continue
            if repo and (fm.get("repo") or "").strip("/") != repo.strip("/"):
                continue
            if author and (fm.get("author") or "").lower() != author.lower():
                continue
            out.append({
                "repo": fm.get("repo"),
                "pr_number": fm.get("pr_number"),
                "pr_url": fm.get("pr_url"),
                "author": fm.get("author"),
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
        save_snapshot: bool = True,
    ) -> dict:
        """Check health of in-flight PRs (outbound PR heartbeat).

        Classifies open PRs into 9 statuses: NEEDS_REBASE, CI_FAILING,
        STALE_REVIEW, CHANGES_REQUESTED, STALE_NO_REVIEW, BLOCKED,
        CLEAN, UNKNOWN, WAITING. Suggests actions for each.

        Args:
            author: GitHub username to check PRs for
            repo: Repository to check (org/name)
            stale_days: Days without update to consider stale (default: profile or 14)
            save_snapshot: Persist the result to data/status-snapshots/ and
                diff it against the previous snapshot (default True — the
                dashboard's memory is the point of this tool). Frequent polling
                is safe: a snapshot is written when state changes and at most
                once a day when it does not, so the directory cannot flood.

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
                save_snapshot=save_snapshot,
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
            result = check_status(author=author, repo_root=rr)
            return suggest_profile_writeback(result, repo_root=rr, mode=mode)
        except RuntimeError as e:
            return [{"error": str(e)}]

    @mcp.tool(annotations=READ_ONLY)
    def maintainer_view(
        title: str,
        repo: str,
        body: str = "",
        description: str = "",
        author: str = "",
        author_association: str = "NONE",
        labels: list[str] | None = None,
        star_count: int = 0,
        repo_merge_rate: float = 0.0,
        diff_stat: str = "",
    ) -> dict:
        """Maintainer-facing action decision for a single PR (v1.5.1).

        Output answers: 'What should I do with this PR right now?'
        Maps analyze_pr signals to 5 actions: READY_FOR_REVIEW,
        WAIT_FOR_AUTHOR, CLOSE_DUPLICATE, CLOSE_STALE_OR_RISKY,
        HOLD_MAINTAINER_DECISION.

        Phase 5.1: Adds impact (files/lines/breaking/security),
        review (complexity/estimated_minutes), and author_info fields.

        Args:
            title: PR title
            repo: Target repo (org/name)
            body: PR body
            description: Extended description
            author: PR author username
            author_association: Author's association (NONE/CONTRIBUTOR/etc.)
            labels: PR labels
            star_count: Repo star count
            repo_merge_rate: External PR merge rate 0.0-1.0
            diff_stat: Diff stat string (e.g. "3 files changed, 10 insertions(+), 5 deletions(-)");
                summary counts only — diff content/hunks are never analyzed

        Returns:
            dict with keys: persona, repo, title, author, action, reason,
            blocking_signals, next_step, review_ready, impact, review,
            author_info, context.
        """
        from .maintainer_view import maintainer_view as _maintainer_view
        return _maintainer_view(
            title=title,
            description=description,
            repo=repo,
            body=body,
            labels=labels or [],
            author=author,
            author_association=author_association,
            star_count=star_count,
            repo_merge_rate=repo_merge_rate,
            diff_stat=diff_stat,
            repo_root=rr,
        )

    @mcp.tool(annotations=READ_ONLY)
    def contributor_view(
        title: str,
        repo: str,
        body: str = "",
        description: str = "",
        author: str = "",
        author_association: str = "NONE",
        labels: list[str] | None = None,
        star_count: int = 0,
        repo_merge_rate: float = 0.0,
        diff_stat: str = "",
    ) -> dict:
        """Contributor-facing action decision for a single PR (v1.6.0).

        Output answers: 'Is my PR ready to submit? What should I fix?'
        Maps analyze_pr signals to 5 actions: READY_TO_SUBMIT,
        FIX_BEFORE_SUBMIT, NEEDS_DISCUSSION, IMPROVE_CHANCE, ASK_MAINTAINER.

        Args:
            title: PR title
            repo: Target repo (org/name)
            body: PR body
            description: Extended description
            author: PR author username
            author_association: Author's association (NONE/CONTRIBUTOR/etc.)
            labels: PR labels
            star_count: Repo star count
            repo_merge_rate: External PR merge rate 0.0-1.0
            diff_stat: Diff stat string (summary counts only — diff content/hunks
                are never analyzed)

        Returns:
            dict with keys: persona, repo, title, author, action, action_label,
            action_icon, reason, next_step, checklist, confidence,
            merge_probability, impact, review, author_info, context.
        """
        from .contributor_view import contributor_view as _contributor_view
        return _contributor_view(
            title=title,
            description=description,
            repo=repo,
            body=body,
            labels=labels or [],
            author=author,
            author_association=author_association,
            star_count=star_count,
            repo_merge_rate=repo_merge_rate,
            diff_stat=diff_stat,
            repo_root=rr,
        )

    @mcp.tool(annotations=READ_ONLY)
    def review_queue(
        prs: list[dict] | None = None,
        prs_file: str = "",
    ) -> dict:
        """Build maintainer review queue digest from a list of PRs (v1.5.0).

        Groups PRs by maintainer action (5 classes) and produces a digest
        suitable for Actions summary or git-trackable markdown file.

        Args:
            prs: List of {repo, number, title, body, author, labels, star_count, repo_merge_rate}
            prs_file: Alternative — path to JSON file containing the PR list

        Returns:
            dict with keys: generated_at, total, summary (action -> count),
            results (per-PR maintainer_view), digest_markdown
        """
        from .maintainer_view import build_review_queue
        from pathlib import Path
        import json as _json

        if prs is None and prs_file:
            try:
                prs = _json.loads(Path(prs_file).read_text(encoding="utf-8"))
            except (OSError, FileNotFoundError, _json.JSONDecodeError) as e:
                return {"error": f"prs_file read failed: {e}"}
        if prs is None:
            return {"error": "specify prs (list) or prs_file (path)"}
        if not isinstance(prs, list):
            return {"error": "prs must be a list"}

        return build_review_queue(prs, repo_root=rr)

    @mcp.tool(annotations=READ_ONLY)
    def prgenius_doctor() -> dict:
        """Self-test the pr-genius install (issue #70).

        Run this before trusting analyze_pr output. Reports Python/package
        versions, knowledge-base readability and coverage (anti-patterns,
        success-patterns, profiles, case studies, policies), gh CLI
        availability, MCP tool registration, a sample analyze against a known
        profile, and data-coverage warnings.

        Returns:
            dict with keys: ok, prgenius_version, python_version, platform,
            knowledge_base, gh, mcp, sample, warnings
        """
        from .doctor import run_doctor

        return run_doctor(rr)

    return mcp


def serve(repo_root: Path | None = None) -> int:
    """Run stdio MCP server. Blocks until the host disconnects."""
    mcp = _load_tools(repo_root=repo_root)
    mcp.run(transport="stdio")
    return 0


if __name__ == "__main__":
    sys.exit(serve())
