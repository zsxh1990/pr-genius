---
type: Community Resource
description: Changelog following Keep a Changelog format + GitHub compare links
---

# Changelog

All notable changes to pr-genius are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this repo uses
GitHub tag/release compare links per Keep a Changelog guidance.

## [Unreleased]

### Compliance
- **OKF v0.1 合规审计** (克莱恩 2026-07-19 拍板): upstream
  [Sudhakaran88/okf-conformance](https://github.com/Sudhakaran88/okf-conformance)
  validator 实测 **PASS conformant · exit 0 · 0 errors · 0 warnings**.
  - 修复 4 MUST errors (M2 frontmatter + 3× M4 relative path)
  - 修复 120 SHOULD warnings (97 S4 orphan + 23 S2 sibling chain)
  - 命名规范化: docs/INDEX.md → docs/index.md (OKF M5 path identity)
  - 新增 docs/COMPLIANCE_AUDIT.md (审计历史 + 已知方言清单)
  - 新增 archive/scripts/pr-genius-landscape-search/ (5 search/fetch 脚本)
  - validate.py type 白名单加 Compliance Audit
- See docs/COMPLIANCE_AUDIT.md for full audit history.

## [1.3.0] - 2026-07-24

### Added
- **Daily content expansion** (552+ cases, 33 repos, 87% coach accuracy)
- **Electron repo profile** (122k stars, C++)
- **20 Electron PR cases** for training
- **Glama deployment** (MCP server + Dockerfile)
- **Tool call prediction table** with A/B testing

### Added (方舟 35 期评测反哺)
- **Check 7 policy_freshness** (`validate_checks/policy_freshness.py`)
  - Maintainer Policy + Repo Profile 超过 90 天 = warn
  - lesson-19 (in-sample 配 holdout) 的评分系统兏底
- **Check 8 release_audit** (`validate_checks/release_audit.py`)
  - pyproject / __init__ / glama.json / Dockerfile / CHANGELOG 版本对齐
  - 课程从 35 期 ether2 REVIEW_FINDINGS.md §1 抓的版本漂移
- **`scripts/anti_overfit.py`** (双指标 LORO + time-split)
  - 替换原 `anti_overfit_loro.py` (单 LORO)
  - 学自 husk2 scripts/anti_overfit.py (v1.5.2)
  - 跑出 4 仓真问题: mongodb LORO -84.5% / vercel/next.js time-split -50% /
    pydantic -44.7% / astral-sh/ruff -35.7%
- **MCP stdio roundtrip 测试** (`prgenius/tests/test_mcp_stdio.py`)
  - 10 个 test (8 tools 全覆盖 + B1/B2 regression)
  - 10 passed in 0.47s
- **data/anti_overfit_report.json** (600 行双指标产物)
  - 可作 lesson-17 "data snapshot README metric unification" 输入
- **lesson-19/20/21** (3 条 A 级, misakanet-50/)
  - lesson-19: Overfit Hard Gate (LORO + time-split required)
  - lesson-20: Honest Claim vs Runtime Evidence (诚实声明 + 实跑 4 形态分级)
  - lesson-21: MCP stdio Runtime Bug (static analysis misses field-path failures)

### Fixed (35 期评测抓到)
- **B1 soft_violations 路径错配** (`prgenius/src/prgenius/mcp.py`)
  - mcp.py:127 `len(result.get("soft_violations", []))` 改为
    `int(result.get("soft_violations", 0))` (triage.py 返回的是 int count)
- **B1' wrapper 漏传 labels** (`prgenius/src/prgenius/mcp.py`)
  - 底层 `triage.py:318` 不收 labels kwarg, wrapper 去掉 labels=
- **B2 _parse_frontmatter_dict 死导入** (`prgenius/src/prgenius/mcp.py`)
  - 改为现存的 `parse_frontmatter` (parser.py:96)
- **B3 .venv/site-packages 假阳** (`validate.py`)
  - SKIP_DIRS 加 .venv / venv / .tox / site-packages / dist / build
- **B5 eval_pr 死导入** (`prgenius/src/prgenius/mcp.py`)
  - 删 `from .evaluator import analyze_pr as _analyze_pr, eval_pr as _eval_pr`
    中的 eval_pr (mcp.py 内部不调用, cli.py:192 仍能用)

### Changed
- **CI gate 升级** (`.github/workflows/validate.yml`)
  - `--strict` 从 soft gate (`|| echo "::warning::"`) 改为 hard fail
  - Check 8 drift + Check 7 stale 在 errors.append 路径会硬卡 PR
- **Version 对齐**: pyproject.toml / __init__.py bump 1.2.0 → 1.3.0
  - 跟 glama.json / Dockerfile 同步
  - 35 期评测 ether2 §1 抓的 "glama/Dockerfile 1.3.0 vs init/pyproject 1.2.0" 漂移修复

## [1.2.0] - 2026-07-18

### Added
- **Daily content expansion**: `scripts/daily_content_expand.py`
  - 自动从 32 个大中仓采样 50 PR/天
  - 7 类质量配额（merged/closed/review/open）
  - 每日 20:37 cron 触发
- **Coach fit report**: `scripts/coach_cases.py`
  - 预测 vs 实际结果对比
  - 156 case, 24 repo, 85% 准确率
- **13 new repo profiles**: httpx, checkout, pydantic, markitdown, tailwindcss,
  huggingface, terraform, docker-compose, cli, openai-python, rust-lang,
  react, fastapi, chroma, qdrant, TypeScript, ruff, deno, golang, anthropics, prometheus
- **Maintainer Policy Memory**: `docs/policies/Ikalus1988-MisakaNet.md`
  - 基于 PR #491-#497 锚点的 9 条维护者政策
  - triage 指南 + hard/soft 分类
- **Shared utilities**: `prgenius/src/prgenius/utils.py`
  - run_gh, fetch_recent_prs, get_merge_rate, classify_pr, extract_signals

### Changed
- **evaluator**: 合并率 >0.8 的大仓取消"首次大仓提 PR"负面信号
  - 准确率从 79% 提升到 87%（121 case）/ 85%（156 case）
- **Signal extraction**: 新增 8 个 metadata-based 信号
  - is_small_pr, is_large_pr, is_backport, is_dependency_update,
    is_bot_pr, has_reviews, has_comments, change_ratio
- **validate.py**: 新增 "Test Report" 合法 type
- **Version**: 统一为 1.2.0（README + pyproject.toml + __init__.py）

### Fixed
- README version 1.1.1 → 1.2.0（与 pyproject.toml 一致）
- 根 index.md 同步 35 个仓库画像

## [1.1.1] - 2026-07-09

### Fixed
- **MCP surface rewrite**: `analyze_pr` / `coach_pr` 替代旧 `eval_pr` / `suggest_pr`
  - 别名导入防止函数遮蔽 (`from .evaluator import analyze_pr as _analyze_pr`)
  - 旧 `suggest_pr` 已从 MCP 移除（v1.0.0 后不再存在）

### Changed
- **DCO 仓库感知**: 从 profile 读取 `requires_dco` / `require_signed_off`
  - `true` → P1 必做项
  - `false` → 不提示
  - 未声明 → P2 提醒
- **Bot 检测升级**: 白名单 + `[bot]` 后缀通用规则
  - `my-custom[bot]` 等未知 bot 也能正确识别
  - Bot PR 跳过 issue link 检查
- **predict_success_rate** docstring 标注 deprecated，仅供 cross_validate 历史兼容

## [1.1.0] - 2026-07-09

### Added
- **coach** command (Agent PR Dojo): `python3 -m prgenius coach "title" --repo org/repo`
  - exit 0 = pass (低风险/中风险), exit 1 = fail (高风险)
  - `--format json` for bot/agent consumption
- **harvest** script: `python3 scripts/harvest.py org/repo 123`
  - 从被拒 PR 自动提取 anti-pattern/lesson draft
  - 支持 `--type lesson` (MisakaNet 风格) 和 `--type anti-pattern`
  - 自动检测 self-close (作者自己关闭) via events API
- Ikalus1988-MisakaNet repo profile
- validate.py accepts Success Pattern, Skill, Retrospective types
- index.md updated with tools section + all 21 repos

### Fixed
- skill/skill.md: added missing `type: Skill` field
- validate.py --strict now passes (0 errors)

### Changed
- Version unified to 1.1.0 across __init__.py, pyproject.toml, CHANGELOG

## [1.0.0] - 2026-07-09

### Changed (BREAKING)
- **从"合并概率预测器"转为"提交前改进顾问"**
- 新增 `analyze` 命令: 结构化信号 + 可操作建议 + 三档风险 (🟢低/🟡中/🔴高)
- `eval` 降级为三档，不再显示百分比
- 砍掉成功模式匹配从评分中移除（语义太粗，泛化差）
- 反模式检测 + 标签信号 + author 历史 → 直接输出 actionable 建议
- `predict_success_rate` 保留为内部兼容函数仅供 cross_validate 使用

## [0.8.0] - 2026-07-09

### Added — Evaluator v0.4.0 (P3/P4/P6)
- `author_association` dimension: OWNER +0.40, MEMBER +0.25, COLLABORATOR +0.20,
  CONTRIBUTOR +0.05, NONE +0.0 — fixes 8/8 FN where MEMBER/OWNER PRs were
  misclassified as rejected
- CLI `--author-association` parameter for `eval` / `suggest`
- `duplicate` label signal strengthened from -15 to -25
- Success pattern per-match bonus reduced from +0.05 to +0.03 (issue link downweight)

### Changed — Evaluator v0.4.0
- Cross-validation accuracy: 80.0% → **87.2%** (180 PR, 9 repos)
- Merged recall: 86.0% → **95.9%**
- FN (漏报): 14 → **4**
- LibreChat: 45% → **85%**, langchain: 80% → **95%**

## [0.7.9] - 2026-07-09

### Added — Evaluator v0.3.0 (P0/P1/P2)
- `scripts/cross_validate.py` — automated cross-validation script (`--repo`, `--all`, `--limit`, `--verbose`, `--json`)
- 3 new anti-patterns: `ai-generated-content`, `missing-issue-reference`, `duplicate-pr-same-author`
- 9 large repo profiles: langchain-ai/langchain, yt-dlp/yt-dlp, microsoft/markitdown,
  langchain-ai/langgraph, onyx-dot-app/onyx, danny-avila/LibreChat, goreleaser/nfpm,
  python-jsonschema/jsonschema, woodruffw/zizmor
- Label signal layer (`LABEL_SIGNALS` dict): ai-policy-violation -20, missing-issue-link -10,
  duplicate -15, new-contributor -3, bug +5, help-wanted +5, etc.
- Bot PR independent channel: dependabot[bot], pre-commit-ci[bot], renovate[bot], etc.
  with size-based baseline (small 70%, medium 50%, large 30%)
- Dynamic baseline: `repo_merge_rate * 0.7 + 0.45 * 0.3`
- CLI parameters: `--body`, `--labels`, `--author`, `--star-count`, `--repo-merge-rate`

### Fixed — Evaluator v0.3.0
- P0: `issue-linked-fix` matching now uses regex `(fixes|closes|resolves)\s+#\d+` instead
  of substring match — eliminates false positives from "this fix addresses..." patterns
- Anti-pattern check now includes PR body (was title+description only)
- Success pattern matching now includes body in full_text for non-issue factors

### Changed — Evaluator v0.3.0
- Base rate: 0.50 → **0.45** (conservative)
- Thresholds: high 0.70→0.60, medium 0.40→0.35
- Cross-validation accuracy: 67.6% → **80.0%** (180 PR, 9 repos)
- Rejected recall: 50.0% → **72.5%**

## [0.7.8] - 2026-07-07

### Changed
- `prgenius` distribution renamed `prgenius-kb` → **`prgenius-core`**
  (drop the awkward `kb` suffix; align with `misakanet-core` naming
  convention). CLI entry point `prgenius-kb` → `prgenius-core`; import
  path `prgenius.cli` unchanged. PyPI publish still pending.

## [0.7.5] - 2026-07-05

### Added
- `archive/scripts/inject-round-evidence.py` — re-runnable round-level evidence
  installer (11/11 case round 1 + 4/4 amend rounds have `verified_at` /
  `evidence_urls` / `confidence`)
- `archive/scripts/refresh-badges.py` — regenerates `docs/badges/*.json` for
  dynamic shields.io endpoints (validate / evidence / round-evidence /
  profiles / cases / lessons / releases / latest-release / prgenius version)
- `docs/INDEX.md` synced with current counts (was stale on agentic #1382/#1383
  double-counted as 12 PRs instead of 11 case studies)

## [0.7.4] - 2026-07-05

### Changed
- CI workflow now hard-fails on `validate.py --enforce-evidence` (no more
  `|| echo ::warning::` soft gate) — future PRs missing case-level evidence
  get red build
- README adds `Evidence 100%` and `Latest release` shields

### Added
- Round-level evidence fields populated for all 11 case studies' round 1
  (`open` action) and 4 amend rounds (e2b / future-agi / honcho / fastmcp)
- `prgenius` package version bumped from `0.1.0` → `0.7.3` in
  `src/prgenius/__init__.py` and `pyproject.toml`

Compare: [0.7.3...0.7.4](https://github.com/zsxh1990/pr-genius/compare/v0.7.3...0.7.4)

## [0.7.3] - 2026-07-05

### Added
- Case-level `verified_at` / `evidence_urls` / `confidence` for **all 11** PR
  Case Studies (honcho / qdrant / uv / mongodb / agentic / e2b / future-agi /
  harbor / fastmcp / sourcebot) — `validate.py --enforce-evidence` 22 → 0

### Fixed
- 4 case frontmatter status drift corrections (uv#19685 → closed-not-merged,
  agentic#1382/#1383 → closed-merged, e2b#1413 → closed-not-merged)
- Released v0.6.3 / v0.6.4 / v0.7.0 / v0.7.1 / v0.7.3 GitHub Releases (5 added
  on top of pre-existing v0.6.0 / v0.6.1 / v0.6.2)
- `archive/scripts/git-push-via-api.py` — Git DB API fallback for when
  `github.com:443` is unreachable but `api.github.com:443` works (WSL
  network-route workaround)
- `archive/scripts/create-v07[1|3]-release.py` and
  `archive/scripts/create-v063-v064-v070-release.py` — release-creation
  helpers using the GitHub API

Compare: [0.7.1...0.7.3](https://github.com/zsxh1990/pr-genius/compare/v0.7.1...0.7.3)

## [0.7.1] - 2026-07-05

### Changed
- Realigned `CHANGELOG.md` — entries previously parked under `[Unreleased]` are now
  under the release they landed in (doc-drift fix only; no code diff)

### Fixed
- `prgenius` distribution renamed `prgenius` → `prgenius-kb` (PyPI name collision
  with an unrelated 2024 GPT-3 PR-description tool — uploader/purpose/maintainer
  all differ). Import path `prgenius.cli` unchanged.
- `prgenius/README.md` missing frontmatter (validate.py --strict was red)

### Added
- 5 PR Case Studies now carry case-level `verified_at` / `evidence_urls` /
  `confidence`: honcho#801, qdrant#143, uv#19685, mongodb#1309, agentic#1382
- `archive/scripts/refresh-evidence.py` — reusable GH-API fetch (5 endpoints × N
  PRs) for evidence refresh passes
- MCP `--repo-root` flag now actually flows through `cli.py cmd_mcp_serve` →
  `mcp.serve(repo_root=...)` → `_load_tools(rr)` (was parsed but ignored — every
  tool was reading the hardcoded module-level constant)
- MCP install/config snippets for Cursor / Claude Code / Cline in
  `prgenius/README.md` (MCP wiring section)

### Known issues
- G. `astral-sh-uv/pr-19685-sarif-audit.md`: case frontmatter says
  `status: merged / merged_at: 2026-06-05`; GH API returns
  `state=closed, merged=False, closed_at=2026-06-05T14:43:54Z`.
- H. `agentic-community-mcp-gateway-registry/pr-1382-auth-md-mermaid-token.md`:
  case frontmatter says `status: open`; GH API returns
  `state=closed, merged=True, merged_at=2026-07-04T16:30:18Z, merged_by=aarora79`.

### Stats
- 12 profiles / 12 case studies / 11 lessons / 12 anti-patterns
- validate.py --strict: 0 errors
- validate.py --enforce-evidence: 12 warnings (down from 22 pre-N1; 6 cases
  not yet refreshed)

Compare: [0.7.0...0.7.1](https://github.com/zsxh1990/pr-genius/compare/v0.7.0...0.7.1)

## [0.7.0] - 2026-07-04

### Added (BREAKING for delta shape, but BC over v0.5.0)
- `prgenius/` Python package — stdlib-only CLI (`python3 -m prgenius …`) and
  stdio MCP shell (`python3 -m prgenius mcp serve`)
- `ROUNDS_SCHEMA.md` v0.7.0 — `verified_at` / `evidence_urls` / `confidence`
  added to delta + case-level (all optional, backward compatible)
- `mcp[server]>=1.0` optional runtime dependency (only loaded when
  `mcp serve` is invoked; everything else stays stdlib)

### Stats
- 12 profiles / 12 case studies / 11 lessons / 12 anti-patterns

Compare: [0.6.4...0.7.0](https://github.com/zsxh1990/pr-genius/compare/v0.6.4...v0.7.0)

## [0.6.4] - 2026-07-04

### Added
- `misakanet-50/lesson-11` — mcp typo pool (real-failure category)
- `scripts/heartbeat.py` snapshot tool + `validate.py --heartbeat` mode

Compare: [0.6.3...0.6.4](https://github.com/zsxh1990/pr-genius/compare/v0.6.3...v0.6.4)

## [0.6.3] - 2026-07-04

### Added
- `agentic-community-mcp-gateway-registry/` profile + 2 PR Case Studies
  (pr-1382, pr-1383)

Compare: [0.6.2...0.6.3](https://github.com/zsxh1990/pr-genius/compare/v0.6.2...v0.6.3)

## [0.6.2] - 2026-07-04

### Changed
- 6 legacy PR Case Studies migrated to `rounds v0.5.0` schema (action enum +
  delta object + close_decision case-level)

Compare: [0.6.1...0.6.2](https://github.com/zsxh1990/pr-genius/compare/v0.6.1...0.6.2)

## [0.6.1] - 2026-07-04

### Added
- `SECURITY.md` — coordinated disclosure policy (private advisory + email)
- `DISCUSSIONS.md` — placeholder for GitHub Discussions until enabled
- `.github/ISSUE_TEMPLATE/config.yml` — chooser config linking to
  Discussions/Security/MisakaNet
- `.github/CODEOWNERS` — singleton maintainer marker
- `.github/FUNDING.yml` — sponsors entry
- `.github/social-preview.svg` — repo social preview source (requires manual
  upload via Settings → Social preview)
- `docs/INDEX.md` — agent-readable file map (P3 stub)
- Topics (10) on GitHub repo settings + extended description + homepage link
- `README.zh.md` Chinese mirror

Compare: [0.6.0...0.6.1](https://github.com/zsxh1990/pr-genius/compare/v0.6.0...0.6.1)

## [0.6.0] - 2026-07-03

### Added
- Community surface: README badges/Quick Start, CONTRIBUTING, CODE_OF_CONDUCT, LICENSE (MIT), CHANGELOG, .github/ (5 issue templates + PR template + dependabot + CI validate workflow)
- `scripts/heartbeat.py` + `validate.py --heartbeat` for daily validator snapshots
- `scripts/fix_lesson_yaml{,_v2}.py` repair tools for `last-updated` field
- `NousResearch-hermes-agent/index.md` (16KB profile)

### Stats
- 11 profiles / 11 case studies / 10 lessons / 4 anti-patterns

Compare: [0.5.3...0.6.0](https://github.com/zsxh1990/pr-genius/compare/v0.5.3...v0.6.0)

## [0.5.3] - 2026-07-02

### Added
- `misakanet-50/SCORING.md` — source credibility scoring system (4-dimension)
- `misakanet-50/score_source.py` — scoring automation tool

### Fixed
- `chore: ignore __pycache__ in misakanet-50/` (commit 2aa4468)

Compare: [0.5.2...0.5.3](https://github.com/zsxh1990/pr-genius/compare/v0.5.2...v0.5.3)

## [0.5.2] - 2026-07-02

### Added
- 5 real-failure lessons in `misakanet-50/lesson-06` through `lesson-10`
- Archive flag on 5 news-style lessons (lessons not suitable for distillation)

Compare: [0.5.1...0.5.2](https://github.com/zsxh1990/pr-genius/compare/v0.5.1...v0.5.2)

## [0.5.1] - 2026-07-02

### Added
- 5 misakanet-style lessons (avg 91/100, all A-grade)
- `misakanet-50/lesson-01` through `lesson-05`

Compare: [0.5.0...0.5.1](https://github.com/zsxh1990/pr-genius/compare/v0.5.0...v0.5.1)

## [0.5.0] - 2026-07-02

### Changed (BREAKING)
- Rounds schema upgrade: `action` enum (9 values) + `delta` object + `close_decision` case-level field
- See [ROUNDS_SCHEMA.md](ROUNDS_SCHEMA.md) v0.2.0 for migration guide

### Added
- `mongodb-js-mongodb-mcp-server/pr-1309-azure-readme-version.md` (1 PR case study)
- Updated `README.md` and `KNOWN_ISSUES.md` for v0.5.0

Compare: [0.4.2...0.5.0](https://github.com/zsxh1990/pr-genius/compare/v0.4.2...v0.5.0)

## [0.4.2] - 2026-07-01

### Added
- Real PR loop #2 on `qdrant/mcp-server-qdrant#143` — stale + close-decision sample

Compare: [0.4.1...0.4.2](https://github.com/zsxh1990/pr-genius/compare/v0.4.1...v0.4.2)

## [0.4.1] - 2026-07-01

### Added
- Real PR decision loop on `plastic-labs/honcho#801` — validates rounds field

Compare: [0.4.0...0.4.1](https://github.com/zsxh1990/pr-genius/compare/v0.4.0...v0.4.1)

## [0.4.0] - 2026-07-01

### Changed
- Review: track 4 known data issues + verification plan

Compare: [0.3.0...0.4.0](https://github.com/zsxh1990/pr-genius/compare/v0.3.0...v0.4.0)

## [0.3.0] - 2026-07-01

### Added
- OKF v0.1 federation declaration (`federates_with` field)
- `misakanet_queries` + `misakanet_lessons` fields in 8 repo profiles

Compare: [0.2.0...0.3.0](https://github.com/zsxh1990/pr-genius/compare/v0.2.0...v0.3.0)

## [0.2.0] - 2026-07-01

### Added
- Agent-first upgrade: agent_guidelines field schema (17 keys)
- Blacklist schema + 6 initially-blacklisted repos

Compare: [0.1.0...0.2.0](https://github.com/zsxh1990/pr-genius/compare/v0.1.0...v0.2.0)

## [0.1.0] - 2026-07-01

### Added
- Initial release
- 8 repo profiles (uv / honcho / harbor / fastmcp / sourcebot / future-agi / qdrant / e2b)
- 4 anti-patterns (e2b / honcho / uv / vite)
- OKF v0.1 compliance

[0.1.0]: https://github.com/zsxh1990/pr-genius/releases/tag/v0.1.0
