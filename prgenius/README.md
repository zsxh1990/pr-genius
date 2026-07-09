---
type: Schema Reference
title: prgenius
description: PR Genius — 提交前改进顾问，stdlib-first CLI + stdio MCP shell
version: 1.1.1
created: 2026-07-04
updated: 2026-07-09
author: zsxh1990
---

# prgenius

**PR Genius — 提交前改进顾问。Local-only. Stdlib-first.**

A pure-Python (zero hard deps) library + CLI for PR contribution quality analysis.

## Install

```bash
pip install prgenius-core
```

Or run from a checkout:

```bash
cd prgenius
PYTHONPATH=src python3 -m prgenius --version
```

## Important: PyPI package is the *interface*, not the data

The PyPI wheel ships only the Python code (`prgenius/` package).
**The knowledge base (profile markdown, case studies, OKF schemas) lives
in the GitHub repo** at <https://github.com/zsxh1990/pr-genius> and is
**not** bundled into the wheel. To use `prgenius-core` after `pip install`,
point it at a checkout of the knowledge base:

```bash
git clone https://github.com/zsxh1990/pr-genius
prgenius-core --repo-root ./pr-genius profile get astral-sh/uv
```

If you cloned a specific tag/commit, the package's `__version__` should
match (e.g. v0.7.7 ↔ `prgenius-core==0.7.7`).

### Optional: MCP server

The MCP entry point (`prgenius-core mcp serve`) requires the `mcp` package:

```bash
pip install "prgenius-core[mcp]"
```

## Quick Start

```bash
# 1) Schema reference
PYTHONPATH=src python3 -m prgenius schema info

# 2) Look up one repo
PYTHONPATH=src python3 -m prgenius profile get astral-sh/uv

# 3) List currently-open case studies
PYTHONPATH=src python3 -m prgenius case list --status=open

# 4) NDJSON dump of every case study (for benchmarks / agent context)
PYTHONPATH=src python3 -m prgenius dump > cases.ndjson

# 5) Run as stdio MCP server (for Cursor/Cline/Claude Code)
PYTHONPATH=src python3 -m prgenius mcp serve
```

## Programmatic use

```python
from prgenius.parser import profile_get, iter_case_studies, schema_info

prof = profile_get("path/to/repo_root", "astral-sh/uv")
print(prof["frontmatter"]["title"])

for case in iter_case_studies("path/to/repo_root"):
    fm = case["frontmatter"]
    if fm.get("final_status") == "open":
        print(fm.get("pr_number"), fm.get("repo"))
```

## What's exposed

| Command | Description |
|---|---|
| `prgenius analyze "title" --repo org/repo` | 提交前改进建议 (三档风险) |
| `prgenius coach "title" --repo org/repo` | Agent PR Dojo (exit 0=pass, 1=fail) |
| `prgenius harvest org/repo 123` | 被拒 PR → anti-pattern/lesson draft |
| `prgenius profile get <org/name>` | 仓库画像 |
| `prgenius case list [--status=...]` | PR Case Study 列表 |
| `prgenius schema info` | Schema 版本 |
| `prgenius dump` | NDJSON dump |
| `prgenius mcp serve` | Stdio MCP server |

## MCP surface (when `mcp` is installed)

6 tools for local agents:

- `analyze_pr(title, repo, body, ...)` — 结构化信号 + 建议 + 三档风险
- `coach_pr(title, repo, body, ...)` — pass/fail + checklist
- `get_repo_profile(repo)` — 仓库画像
- `list_open_prs()` — open PR 列表
- `get_case_study(repo, pr_number)` — PR 案例
- `schema_info()` — schema 版本

No network, no auth. Stdio only.

### `--repo-root` flag

The MCP server defaults to a path computed from its install location
(`<package>/../..` × 3 to reach the knowledge base). When that path is
wrong (editable install, venv, worktree, fork), pass `--repo-root`:

```bash
python3 -m prgenius --repo-root /path/to/big-repo-pr-knowledge mcp serve
```

### Wiring into Cursor / Claude Code / Cline

These editors all read MCP server config from JSON. Point `command` at
`python3 -m prgenius` and `args` at `mcp serve` (add `--repo-root` if the
auto-detected path doesn't match your checkout). No `env` keys, no auth.

**Claude Code** (`~/.claude/mcp.json` or project-local `.mcp.json`):

```json
{
  "mcpServers": {
    "pr-genius": {
      "command": "python3",
      "args": ["-m", "prgenius", "--repo-root", "/abs/path/to/big-repo-pr-knowledge", "mcp", "serve"]
    }
  }
}
```

**Cursor** (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "pr-genius": {
      "command": "python3 -m prgenius",
      "args": ["--repo-root", "/abs/path/to/big-repo-pr-knowledge", "mcp", "serve"]
    }
  }
}
```

**Cline** (VS Code `cline_mcp_settings.json`):

```json
{
  "mcpServers": {
    "pr-genius": {
      "command": "python3",
      "args": ["-m", "prgenius", "--repo-root", "/abs/path/to/big-repo-pr-knowledge", "mcp", "serve"],
      "disabled": false
    }
  }
}
```

Replace `/abs/path/to/big-repo-pr-knowledge` with the actual checkout.
Omit `--repo-root` only if you installed prgenius from this exact
checkout (then the default path resolves correctly).

## Schema we honor

- **rounds v0.5.0** — `action` enum + `delta` object + case-level `close_decision`
- **rounds v0.7.0** — adds optional `verified_at`, `evidence_urls`, `confidence`
  to round + case level (BC over v0.5.0)

See [../ROUNDS_SCHEMA.md](../ROUNDS_SCHEMA.md) for the canonical schema.

## Why this exists

The repo is meant to be human-readable (`<org>-<repo>/index.md`) AND
machine-readable via this package. People get the narrative; agents get
structured tool calls. Both views share one source of truth.

## License

MIT (same as parent repo).
