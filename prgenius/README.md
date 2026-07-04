# prgenius

**Evidence-backed lookup for big-repo PR contributions. Local-only. Stdlib-first.**

A pure-Python (zero hard deps) library + CLI that reads the markdown knowledge
base in this repo and exposes it through structured tool calls.

## Install

```bash
pip install prgenius
```

Or run from a checkout:

```bash
cd prgenius
PYTHONPATH=src python3 -m prgenius --version
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

| Tool | Description |
|---|---|
| `prgenius profile get <org/name>` | One Repo Profile (frontmatter + first lines) |
| `prgenius case list [--status=...]` | All PR Case Study rows |
| `prgenius schema info` | Supported schema versions + enums |
| `prgenius dump` | NDJSON dump (one case per line) |
| `prgenius mcp serve` | Stdio MCP server (4 tools) |

## MCP surface (when `mcp` is installed)

The MCP shell exposes 4 tools to local agents:

- `get_repo_profile(repo)` — one Profile dict
- `list_open_prs()` — currently-open PRs
- `get_case_study(repo, pr_number)` — one Case Study
- `schema_info()` — schema versions + enums

No network, no auth, no rate-limiting. Agent calls go through stdio only.

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
