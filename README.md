---
type: Knowledge Bundle
title: PR Genius — Pre-submission PR Advisor
description: Evidence-backed PR contribution advisor for large open-source projects
version: 1.3.0
created: 2026-07-01
updated: 2026-07-22
author: zsxh1990
conforms_to: OKF v0.1 (Sudhakaran88/okf-conformance) + agent_guidelines extension
---
mcp-name: io.github.zsxh1990/pr-genius

# PR Genius — The advisor that knows which PRs get closed

> **550+ real case studies. Find the path to maximum merge probability.**
> Clone → paste MCP config → ask "Should I open this PR to encode/httpx?"

<p align="center">
  <a href="https://glama.ai/mcp/servers"><img src="https://glama.ai/mcp/servers/zsxh1990/pr-genius/badge" alt="MCP Server on Glama"/></a>
  <a href="https://github.com/zsxh1990/pr-genius/blob/main/LICENSE"><img src="https://img.shields.io/github/license/zsxh1990/pr-genius?style=flat&color=blueviolet" alt="License"/></a>
  <a href="https://github.com/zsxh1990/pr-genius"><img src="https://img.shields.io/badge/cases-550+-blue?label=Cases" alt="Cases"/></a>
  <a href="https://github.com/zsxh1990/pr-genius"><img src="https://img.shields.io/badge/profiles-58-blue?label=Profiles" alt="Profiles"/></a>
</p>

---

## 🛡️ Why PR Genius?

**PR Genius doesn't write PRs for you. It knows which PRs get closed.**

| Capability | LLM directly | Scraper Agent | PR Genius |
|------------|-------------|---------------|-----------|
| Knowledge source | Training data | Real-time scrape | 550+ structured case studies |
| Repo understanding | Generic | Surface data (stars) | 17-field agent_guidelines |
| Failure patterns | Unknown | Unknown | 68 anti-patterns |
| Maintainer preference | Guess | Recent PRs | Structured policy files |
| Merge probability | Can't estimate | Can't estimate | Based on repo merge rate + signals |

**Real lessons (only learned by getting rejected):**
- MisakaNet doesn't accept "destructive README rewrites" (#491, #496)
- huggingface wants to "handle internally" tokenizer versions (#47434)
- encode/httpx doesn't accept external contributors (restricted interactions)
- Glama badge is required for awesome-mcp-servers (#10393)

## 🚀 Quick Start

```bash
pip install prgenius-core

# Analyze PR
python3 -m prgenius analyze "feat: add feature" --repo org/repo --body "Fixes #123"

# Coach (pass/fail)
python3 -m prgenius coach "feat: add feature" --repo org/repo

# Triage (policy check)
python3 -m prgenius triage "docs: typo" --repo org/repo --diff-stat "docs/faq.md | 3 ++-"
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
| Repo profiles | 58 |
| Case studies | 50+ |
| Anti-patterns | 68 |
| Success patterns | 40+ |
| Coach accuracy | 87% (257 cases, LORO validated) |
| Covered repos | 35+ (react, kubernetes, rust, uv, pydantic, etc.) |

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
