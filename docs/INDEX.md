---
type: Index
title: pr-genius Index Map
description: Agent-readable map of every file in this repo and what it does.
version: 0.7.5
created: 2026-07-04
updated: 2026-07-05
conforms_to: OKF v0.1
---

# pr-genius Index (agent-readable)

This file is an **agent-first map**. Every other document in this repo
should be reachable from here by path. If you are an LLM agent reading
this, you can use it to plan your next retrieval step.

> For humans: this complements `README.md` (narrative) by listing paths
> and what each file is for.

## Repo root

| Path | Purpose | Reading order |
|---|---|---|
| `README.md` | What this is, Quick Start, stats, badges | 1 |
| `index.md` | Root OKF index (Sudhakaran88/okf-conformance) | 2 |
| `KNOWN_ISSUES.md` | Known data gaps + verification plan | 3 |
| `CHANGELOG.md` | Version history (Keep a Changelog, 9 releases) | - |
| `CONTRIBUTING.md` | How to contribute (profile/lesson/PR/AI-assisted) | - |
| `CODE_OF_CONDUCT.md` | Conduct rules | - |
| `LICENSE` | MIT | - |
| `SECURITY.md` | Coordinated disclosure | - |
| `DISCUSSIONS.md` | Discussions categories (until enabled) | - |
| `README.zh.md` | Chinese README mirror | - |
| `validate.py` | Validator (frontmatter / links / consistency / rounds) | - |

## Schemas & governance

| Path | Purpose |
|---|---|
| `AGENT_GUIDELINES_SCHEMA.md` | 17-key agent_guidelines field (8 repo profiles × shape) |
| `ROUNDS_SCHEMA.md` | rounds v0.7.0 schema (action / delta / close_decision / evidence) |
| `BLACKLIST.md` | Repos we don't track (with reason) |
| `federation.yaml` | `federates_with` declarations (MisakaNet query-only) |

## `prgenius/` Python package

The local stdlib-only Python library + CLI + stdio MCP shell. Shipped
as the `prgenius-kb` distribution on PyPI (renamed from `prgenius` to
avoid a 2024 name collision).

| Path | Purpose |
|---|---|
| `prgenius/README.md` | Package-level README — install + Cursor/Claude/Cline MCP snippets |
| `prgenius/pyproject.toml` | stdlib-only build config (`prgenius-kb` distribution) |
| `prgenius/src/prgenius/__init__.py` | Package metadata (`__version__ = "0.7.3"`) |
| `prgenius/src/prgenius/parser.py` | Pure-stdlib frontmatter parser + iterators |
| `prgenius/src/prgenius/cli.py` | CLI entry (`python3 -m prgenius ...`) |
| `prgenius/src/prgenius/mcp.py` | stdio MCP shell (4 tools) |
| `prgenius/src/prgenius/__main__.py` | `python3 -m prgenius` entry |

## Repo profiles (`<org>-<repo>/`)

12 profiles total. Each is a directory. Naming: `owner-repo` with `-`,
never `_`.

| Profile | Star | Lang | Case studies + status (post-v0.7.4 status drift fix) |
|---|---|---|---|
| `ag2ai-ag2/` | 21k★ | Python | (image-only profile; no PR case yet) |
| `astral-sh-uv/` | 35k★ | Rust | pr-19685 (closed-not-merged) |
| `e2b-dev-e2b/` | — | Python | pr-1413 (closed-not-merged) |
| `future-agi-future-agi/` | — | Python | pr-778 (open, round-3 third-party check-in) |
| `harbor-framework-harbor/` | — | Python | pr-2121 (open) |
| `mongodb-js-mongodb-mcp-server/` | 1.1k★ | TypeScript | pr-1309 (open) |
| `NousResearch-hermes-agent/` | 208k★ (hub) | Python | (image-only profile) |
| `plastic-labs-honcho/` | — | Python | pr-801 (open, round 4 awaiting bump-or-close at 7/9) |
| `punkpeye-fastmcp/` | — | Python | pr-282 (open) |
| `qdrant-mcp-server-qdrant/` | — | Python | pr-143 (open, 28d stale, close-decision pending at 7/9) |
| `sourcebot-dev-sourcebot/` | — | TypeScript | pr-1383 (open) |
| `agentic-community-mcp-gateway-registry/` | 765★ | Python | pr-1382 + pr-1383 (both closed-merged 7/4) |

Each profile directory contains either:
- `index.md` (Repo Profile) — single-PR-safe default
- `RISK.md` (skip-for-now decision record) — no profile, decision only
- `pr-<num>-<slug>.md` (PR Case Study) — 0..n

## Anti-patterns

| Path | Slug |
|---|---|
| `anti-patterns/README.md` | Index |
| `anti-patterns/2026-04-12-e2b-error-handler.md` | e2b _ERROR_HANDLER pattern |
| `anti-patterns/2026-04-13-honcho-pr-template-merge-defaults.md` | honcho template |
| `anti-patterns/2026-04-16-uv-pin-and-deps-bloat.md` | uv over-pin |
| `anti-patterns/2026-04-19-vite-error-handler-rejection.md` | vite rejection |

## Lessons (`misakanet-50/`)

50 lessons distilled from MisakaNet practice. Currently **11 published**
(lesson-01 through lesson-11). The scoring tool is
`misakanet-50/score_source.py` (4-dimension source credibility).

| Path | Purpose |
|---|---|
| `misakanet-50/lesson-01.md` .. `lesson-11.md` | Published lessons |
| `misakanet-50/SCORING.md` | 4-dimension scoring rubric |
| `misakanet-50/score_source.py` | Scoring automation tool |

Each lesson follows the OKF v0.1 frontmatter (title, type, description,
version, created, conforms_to, federates_with).

## Scripts (`scripts/`)

Operational scripts (kept under `scripts/`; one-off / network-bypass
scripts under `archive/scripts/`).

| Path | Purpose |
|---|---|
| `scripts/heartbeat.py` | Daily validator snapshot (errors/warnings/files) |
| `scripts/dashboard.py` | Open PR Case Study dashboard (sorts by days_idle) |
| `scripts/fix_lesson_yaml.py` | Initial last-updated repair |
| `scripts/fix_lesson_yaml_v2.py` | Resilient last-updated repair |
| `scripts/fix_legacy_cases.py` | v0.1 → v0.5.0 schema migration for old case studies |

## `archive/scripts/` (one-off / re-runnable)

Ponytail-min: capture-and-keep, not delete. These scripts were written
to work around WSL→github.com:443 routing failures or to be
re-runnable evidence / release tools.

| Path | Purpose | When to run |
|---|---|---|
| `archive/scripts/refresh-evidence.py` | Fetch GH API for N PRs (PR/files/comments/reviews/commits) | After closing / merging PRs; before enforcing evidence |
| `archive/scripts/inject-round-evidence.py` | Inject round-level `verified_at` / `evidence_urls` / `confidence` into case rounds | After refresh-evidence; idempotent |
| `archive/scripts/git-push-via-api.py` | Push one commit via Git Database API | When `github.com:443` is unreachable but `api.github.com:443` works |
| `archive/scripts/create-v071-release.py` | Create GH Release + tag for v0.7.1 | One-shot at v0.7.1 |
| `archive/scripts/create-v073-release.py` | Create GH Release for v0.7.3 | One-shot at v0.7.3 |
| `archive/scripts/create-v063-v064-v070-release.py` | Bulk create releases for v0.6.3/v0.6.4/v0.7.0 | One-shot history fill |
| `archive/scripts/create-v074-release.py` | Create GH Release for v0.7.4 | One-shot at v0.7.4 |
| `archive/scripts/.tmp/` | gitignored cache for evidence dumps | (regenerated each refresh-evidence run) |

## `.github/`

| Path | Purpose |
|---|---|
| `.github/ISSUE_TEMPLATE/` | 5 issue templates + config.yml chooser |
| `.github/PULL_REQUEST_TEMPLATE.md` | PR template |
| `.github/CODEOWNERS` | Singleton (@zsxh1990) |
| `.github/FUNDING.yml` | GitHub sponsors entry |
| `.github/dependabot.yml` | Auto PRs for stale actions |
| `.github/workflows/validate.yml` | CI validator on every push (**includes hard `--enforce-evidence` gate**) |
| `.github/social-preview.svg` | Source for repo social preview (upload via UI) |

## What this map is NOT

- **Not** a sitemap.xml — XML sitemaps require a served URL.
- **Not** an llms.txt — see `federation.yaml` instead for cross-repo robot hints.
- **Not** generated by `tree` — contents are curated; regenerate when
  adding/removing large sections (don't regenerate on every commit).

## Auto-generated metadata

| Field | Value |
|---|---|
| `prgenius` package version | `0.7.3` (in `prgenius/src/prgenius/__init__.py`) |
| Latest GH release | `v0.7.4` (2026-07-05) |
| Total case studies | 11 (one PR per file; agentic #1382 + #1383 are separate case studies for the same profile) |
| Total profiles | 12 |
| Total lessons | 11 (`misakanet-50/lesson-01`..`lesson-11`) |
| Total anti-patterns | 5 |
| Round-level evidence | 11/11 round-1 + 4/4 amend rounds have `verified_at` / `evidence_urls` / `confidence` |
| `validate.py --strict` | 0 errors ✅ |
| `validate.py --enforce-evidence` | 0 warnings ✅ (hard-gate on PRs) |