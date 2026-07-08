---
type: Community Resource
description: Changelog following Keep a Changelog format + GitHub compare links
---

# Changelog

All notable changes to pr-genius are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this repo uses
GitHub tag/release compare links per Keep a Changelog guidance.

## [Unreleased]

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
