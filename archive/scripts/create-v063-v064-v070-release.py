#!/usr/bin/env python3
"""Create v0.6.3, v0.6.4, v0.7.0 release notes + tags (chronology fill-up)."""
import json
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.github.com"
REPO = "zsxh1990/pr-genius"

COMMITS = [
    {
        "tag": "v0.6.3",
        "sha": "f20cb833d4104d152eea4e27ceff3889c9fb8c06",
        "name": "v0.6.3 — agentic-community-mcp-gateway-registry profile + 2 case studies",
        "body": """\
## v0.6.3 — New profile + 2 case studies (2026-07-04)

### New profile

- `agentic-community-mcp-gateway-registry/` (12th profile)
  - 765★ / 201 fork / Python / 57MB / 94 open issues
  - Maintainer vibe: responsive (single-day merges of 9+ PRs in 7/3-7/4)
  - Friendly pattern: docs/mermaid-fix (matches PR #1373, #1375, this batch)
  - **Red zones**: deployment, oauth/identity middleware, observability

### New case studies (rounds v0.5.0 schema, close_decision=pending)

- `pr-1382-auth-md-mermaid-token.md` (1 file, 1 line, +1/-1)
- `pr-1383-egress-vault-mermaid-placeholders.md` (1 file, 2 lines, +2/-2)

### Index updates

- `index.md`: +3 rows (agentic-community, mongodb-js, NousResearch now visible)
- `docs/INDEX.md`: mongodb-js star count fix (1073 → 1.1k); NousResearch
  updated to 208k hub

## Stats

- 12 profiles / 12 case studies / 11 lessons / 4 anti-patterns
- validate.py --strict: 0 errors
""",
    },
    {
        "tag": "v0.6.4",
        "sha": "d40c003ace0a2c7ed633b546cefabf3bae33b39f",
        "name": "v0.6.4 — lesson-11 (mcp typo pool) + heartbeat snapshot + dashboard tool",
        "body": """\
## v0.6.4 — lesson + tooling (2026-07-04)

### Added

- `misakanet-50/lesson-11-mcp-typo-pool-x3-merged.md` — real-empirical
  lesson covering 2 PRs (#1382, #1383) + 1 marker-pattern (#1373 + #1375);
  distills the pattern: 1-file-per-PR, copy maintainer tone, mcp docs-only
  diffs (domains: pr-strategy, tooling; confidence: 0.91)
- `scripts/heartbeat.py` — daily validator snapshot; last run:
  2026-07-04T14:08:46 GMT+8 with 60 files / 0 errors / 0 warnings
- `scripts/dashboard.py` — lists every PR Case Study open / in-flight /
  pending (sorts by days_idle desc; flags stale at ≥14d / ≥30d)

### Updated

- `KNOWN_ISSUES.md` tracker — bumped snapshot count and TRACKED_REPOS
  (added `agentic-community/mcp-gateway-registry`)

## Stats

- 12 profiles / 12 case studies / 11 lessons / 5 anti-patterns
- validate.py --strict: 0 errors
""",
    },
    {
        "tag": "v0.7.0",
        "sha": "ba3032b6c1fcf3877099ed25a458a066d51483b9",
        "name": "v0.7.0 — schema evidence layer + stdlib prgenius package + stdio MCP shell",
        "body": """\
## v0.7.0 — Foundation (2026-07-04)

This is the foundation release that everything since builds on.
**If you are upgrading, read this first**, then look at v0.7.1 for
the `prgenius` → `prgenius-kb` rename and v0.7.3 for evidence coverage.

### T1 — `prgenius` Python package (new, `src/prgenius/`)

- `pyproject.toml` (stdlib-only, no deps)
- `parser.py` — pure-stdlib YAML-subset frontmatter parser (zero PyYAML)
- `cli.py` — subcommands: `profile`, `case`, `schema`, `dump`, `mcp`
- `mcp.py` — stdio MCP shell exposing 4 tools:
  - `get_repo_profile(repo)`
  - `list_open_prs()`
  - `get_case_study(repo, pr_number)`
  - `schema_info()`
- NDJSON dump output (benchmark-ready)
- Smoke-tested only (no formal test suite — tracked as TODO G2+)

### T2 — schema v0.7.0 (BC over v0.5.0)

- `ROUNDS_SCHEMA.md` adds three optional fields, available at both levels:
  - Round-level: `delta.verified_at`, `delta.evidence_urls`, `delta.confidence`
  - Case-level: `verified_at`, `evidence_urls`, `confidence`
- 100% BC: when absent they're ignored; presence is forward-compatible
- `validate.py` rewritten to surface v0.7.0 fields and emit
  `--enforce-evidence` warnings when case-level evidence is missing

### T3 — stdio MCP shell (`scripts/dashboard.py`)

- Reads `data/snapshot.json` when present, falls back to in-script
  computation
- `--snapshot` mode emits JSON snapshot of n-counts
- Stats line consumes snapshot numbers (avoids hand-written drift)

### T4 — README narrative cleanup

- External-facing README + index.md use neutral terms
- Internal history (CHANGELOG / KNOWN_ISSUES) uses maintainer / initiator
- "Pragmatic" CHANGELOG lines preserved (data, not narrative)
- Dropped "MisakaNet 一侧" section (planned-only, not actionable)

### T5 — legacy BC scaffold

- `validate.py --enforce-evidence` surfaces cases needing v0.7.0 fields
- The 100%-coverage goal from evaluation is now checkable, not aspirational

## Stats

- 12 profiles / 12 case studies / 11 lessons / 5 anti-patterns
- snapshot.json: 60 files / 12 profiles / 11 case studies / 0 errors / 0 warnings
- data/ in .gitignore (don't ship generated snapshots)

## Important upgrade note

In **v0.7.1** the distribution was renamed `prgenius` → `prgenius-kb` to
avoid a PyPI name collision with an unrelated 2024 GPT-3 PR-description
tool. If you are installing for the first time, use `prgenius-kb`.
""",
    },
]


def get_pat():
    creds = Path.home() / ".git-credentials"
    for line in creds.read_text().splitlines():
        if not line.startswith("https://"):
            continue
        user, _, rest = line[len("https://"):].rpartition("@")
        u, _, t = user.partition(":")
        if u == "zsxh1990":
            return t
    raise RuntimeError("No PAT")


def gh(method, path, token, body=None):
    req = urllib.request.Request(
        f"{API}{path}", method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
    )
    data = json.dumps(body).encode("utf-8") if body is not None else None
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, data=data, timeout=30) as resp:
            raw = resp.read()
            return resp.status, (json.loads(raw.decode("utf-8")) if raw else {})
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        return e.code, json.loads(raw) if raw.startswith(("{", "[")) else {"raw": raw}


def main():
    token = get_pat()
    for c in COMMITS:
        # 1. Create tag ref
        status, ref = gh("POST", f"/repos/{REPO}/git/refs", token,
                         body={"ref": f"refs/tags/{c['tag']}", "sha": c["sha"]})
        if status == 201:
            print(f"  tag {c['tag']} created", flush=True)
        elif status == 422:
            print(f"  tag {c['tag']} already exists", flush=True)
        else:
            print(f"  tag {c['tag']}: {status} {ref}", flush=True)
            continue

        # 2. Create release
        status, rel = gh("POST", f"/repos/{REPO}/releases", token,
                         body={
                             "tag_name": c["tag"],
                             "name": c["name"],
                             "body": c["body"],
                             "target_commitish": c["sha"],
                             "draft": False,
                             "prerelease": False,
                         })
        if status == 201:
            print(f"  release {c['tag']} created id={rel.get('id')}",
                  flush=True)
            print(f"  → {rel.get('html_url')}", flush=True)
        elif status == 422:
            print(f"  release {c['tag']} already exists", flush=True)
        else:
            print(f"  release {c['tag']}: {status} {rel}", flush=True)


if __name__ == "__main__":
    main()
