---
type: Knowledge Bundle
title: PR Genius — Pre-submission PR Advisor
description: Evidence-backed PR contribution advisor for large open-source projects
version: 1.4.0
created: 2026-07-01
updated: 2026-07-22
author: zsxh1990
conforms_to: OKF v0.1 (Sudhakaran88/okf-conformance) + agent_guidelines extension
---
mcp-name: io.github.zsxh1990/pr-genius

# PR Genius — The advisor that knows which PRs get closed

> **1355 loaded patterns across 61 repos. 100% quality pass rate.**
> Clone → paste MCP config → ask "Should I open this PR to encode/httpx?"

[![CI](https://github.com/zsxh1990/pr-genius/actions/workflows/validate.yml/badge.svg)](https://github.com/zsxh1990/pr-genius/actions/workflows/validate.yml)
[![PyPI](https://img.shields.io/pypi/v/prgenius-core)](https://pypi.org/project/prgenius-core/)
[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/github/license/zsxh1990/pr-genius?style=flat&color=blueviolet)](https://github.com/zsxh1990/pr-genius/blob/main/LICENSE)
[![Glama score](https://glama.ai/mcp/servers/zsxh1990/pr-genius/badges/score.svg)](https://glama.ai/mcp/servers/zsxh1990/pr-genius)

---

## 🎯 What is PR Genius?

PR Genius is **not** a PR dashboard. It's an **Outbound PR CRM** for professional OSS contributors and AI agents:

> Manage PRs you've *submitted to other repos* — when to fix CI, rebase, wait, ping, or abandon.

| Capability | `gh` CLI | PR Genius |
|---|---|---|
| Cross-repo PR list | ✅ | ✅ |
| Status classification | ❌ | ✅ (9 states) |
| Stale detection | ❌ | ✅ |
| Action suggestions | ❌ | ✅ |
| Repo-specific policy | ❌ | ✅ |
| Snapshot & transitions | ❌ | ✅ |

**Status heartbeat** runs daily via cron, auto-detecting:
- 🔴 `NEEDS_REBASE` / `CI_FAILING` — fix immediately
- 🟡 `STALE_REVIEW` — ping after threshold
- 🟡 `STALE_NO_REVIEW` — consider abandoning
- 🟢 `CLEAN` / `WAITING` — continue waiting

---

## 🛡️ Why PR Genius?

**PR Genius doesn't write PRs for you. It knows which PRs get closed.**

| Capability | LLM directly | Scraper Agent | PR Genius |
|------------|-------------|---------------|-----------|
| Knowledge source | Training data | Real-time scrape | 1355 structured patterns |
| Repo understanding | Generic | Surface data (stars) | 17-field agent_guidelines |
| Failure patterns | Unknown | Unknown | 752 anti-patterns |
| Success patterns | Unknown | Unknown | 703 success patterns |
| Maintainer preference | Guess | Recent PRs | Structured policy files |
| Merge probability | Can't estimate | Can't estimate | Based on repo merge rate + signals |

**Real cases (PR Genius helped avoid these rejections):**

| PR | Repo | What happened | PR Genius would have flagged |
|----|------|---------------|------------------------------|
| #491 | MisakaNet | "Destructive README rewrite" — closed | `breaking_change_no_compat` anti-pattern |
| #47434 | huggingface/transformers | "We'll handle internally" — closed | `maintainer_internal_handling` anti-pattern |
| #10393 | awesome-mcp-servers | Missing Glama badge — auto-flagged | `awesome-mcp-servers-glama-badge-required` anti-pattern |
| #282 | punkpeye/fastmcp | +271 lines, first PR — closed without review | `fastmcp-282-too-large` anti-pattern |
| #2902 | soxoj/maigret | CI failure (tag `dev` not recognized) — fixed, merged | `maigret-tag-validation` pattern |

## 🚀 Quick Start

```bash
pip install prgenius-core

# Analyze PR
python3 -m prgenius analyze "feat: add feature" --repo org/repo --body "Fixes #123"

# Coach (pass/fail)
python3 -m prgenius coach "feat: add feature" --repo org/repo

# Triage (policy check)
python3 -m prgenius triage "docs: typo" --repo org/repo --diff-stat "docs/faq.md | 3 ++-"

# Status heartbeat (outbound PR monitoring)
python3 -m prgenius status --author zsxh1990
python3 -m prgenius status --author zsxh1990 --format json --save-snapshot

# Profile writeback suggestions (dry-run)
python3 -m prgenius profile writeback --author zsxh1990
```

## 🤖 GitHub Action

Use PR Genius as a GitHub Action in any repo:

```yaml
# .github/workflows/pr-genius.yml
name: PR Genius Check
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  pr-genius:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: zsxh1990/pr-genius/.github/actions/pr-genius-check@main
        id: pr-genius
        with:
          title: ${{ github.event.pull_request.title }}
          repo: ${{ github.repository }}
          body: ${{ github.event.pull_request.body }}
      - name: Comment on PR
        if: always()
        uses: actions/github-script@v7
        with:
          script: |
            const tier = '${{ steps.pr-genius.outputs.tier }}';
            const emoji = tier === 'high_risk' ? '🔴' : tier === 'medium_risk' ? '🟡' : '🟢';
            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: `## ${emoji} PR Genius: ${tier}`
            });
```

## 🤖 MCP Configuration

```json
{
  "mcpServers": {
    "pr-genius": {
      "command": "python",
      "args": ["-m", "prgenius", "mcp", "serve"]
    }
  }
}
```

Docker: `docker run --rm -i ghcr.io/zsxh1990/pr-genius:1.3.0`

### 8 MCP Tools

| Tool | Purpose | Required Args |
|------|---------|---------------|
| `analyze_pr` | Merge probability + optimization path + 3-tier risk | `title`, `repo` |
| `coach_pr` | Go/no-go decision (pass/fail) | `title`, `repo` |
| `triage_pr` | Maintainer policy check (9 rules) | `title`, `repo` |
| `get_repo_profile` | Repo profile (17 fields) | `repo` |
| `list_open_prs` | Open PR list | `repo` |
| `get_case_study` | PR case study details | `case_id` |
| `search_patterns` | Anti-pattern/success-pattern search | `query` |
| `schema_info` | OKF schema versions | *(none)* |

### Tool Parameter Notes

- **`title`** (required for `analyze_pr`, `coach_pr`, `triage_pr`): The PR title, e.g. `"fix: timeout in connection pool"`
- **`repo`** (required for most tools): Repository in `owner/name` format, e.g. `"encode/httpx"`
- **`pr_description`** (optional): Additional PR body text for deeper analysis
- **`query`** (required for `search_patterns`): Search keywords, e.g. `"connection timeout"`

## 📊 Data Scale

| Dimension | Count |
|-----------|-------|
| Repo profiles | 61 |
| Case studies | 50+ |
| Success patterns | 687 (431 .md + 256 .json) |
| Anti-patterns | 668 (561 .md + 107 .json) |
| Total patterns | 1355 (all loaded) |
| Quality pass rate | 100% (994/994 markdown ≥75分) |
| Covered repos | 35+ (react, kubernetes, rust, uv, pydantic, etc.) |

### 按仓库规模分布

| 规模 | Success | Anti | 总计 |
|------|---------|------|------|
| 大仓 (>10k ⭐) | 208 | 205 | 413 |
| 中仓 (1k-10k ⭐) | 169 | 88 | 257 |
| 小仓 (<1k ⭐) | 169 | 88 | 257 |
| 通用 | 203 | 414 | 617 |
| 其他 (特定仓库) | 312 | 260 | 572 |

## 🤖 Robots / Agents

1. **[docs/index.md](docs/index.md)** — file map
2. **[AGENT_GUIDELINES_SCHEMA.md](AGENT_GUIDELINES_SCHEMA.md)** — agent_guidelines schema
3. **[ROUNDS_SCHEMA.md](ROUNDS_SCHEMA.md)** — rounds schema
4. **[BLACKLIST.md](BLACKLIST.md)** — repos we don't track

## 📖 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). AI-assisted PRs welcome.

## 🤝 Community

- 📋 [Code of Conduct](CODE_OF_CONDUCT.md)
- 🔒 [Security Policy](SECURITY.md)
- 🐛 [Issue Tracker](../../issues)
- 📜 [Changelog](CHANGELOG.md)

## 中文文档

中文版 README：[README.zh-CN.md](README.zh-CN.md)

## Citation

```bibtex
@misc{pr-genius-2026,
  title  = {PR Genius — Evidence-backed PR Contribution Advisor},
  author = {zsxh1990},
  year   = {2026},
  url    = {https://github.com/zsxh1990/pr-genius}
}
```

<!-- diff stat test -->
