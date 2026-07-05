#!/usr/bin/env python3
"""create-v071-release.py — create GitHub release via API (no git protocol needed).

Bypasses the github.com:443 route that is currently dead on this WSL setup;
goes through api.github.com:443 (which works).
"""
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.github.com"
COMMIT_SHA = "184075c634981615c9388e587da5cb0684fe9b5a"
TAG = "v0.7.1"
REPO = "zsxh1990/pr-genius"


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
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


def main():
    token = get_pat()

    # First check if tag already exists (it doesn't — there are no v0.7.1 tags)
    status, tags = gh("GET",
                      f"/repos/{REPO}/git/refs/tags/{TAG}", token)
    print(f"GET tag refs → {status}", flush=True)
    if status == 200:
        print(f"Tag {TAG} already exists — skipping tag creation", flush=True)
    else:
        # Create tag ref pointing at commit
        status, ref = gh("POST", f"/repos/{REPO}/git/refs", token,
                         body={"ref": f"refs/tags/{TAG}", "sha": COMMIT_SHA})
        print(f"POST ref → {status}: {ref}", flush=True)

    # Create release
    notes = """\
## What's in v0.7.1

**Distribution rename** — `prgenius` → **`prgenius-kb`** (PyPI name was already
taken by an unrelated 2024 GPT-3 PR-description tool; uploader, purpose,
maintainer all differ). Import path unchanged (`prgenius.cli`). README install
command updated.

**MCP `--repo-root` flag now actually flows** — `cli.py cmd_dump` and
`cli.py cmd_mcp_serve` were parsing `--repo-root` but ignoring it; `mcp.py`
hardcoded `REPO_ROOT` as a module-level constant. Both fixed. All 4 tool
implementations now read the resolved repo_root from `_load_tools(repo_root)`.

**Cursor / Claude Code / Cline config snippets** in `prgenius/README.md` —
JSON ready to paste into `~/.claude/mcp.json`, `~/.cursor/mcp.json`, or
VS Code `cline_mcp_settings.json`.

**`validate.py --enforce-evidence` convergence** — 22 → 12 warnings. 5 PR
Case Studies now carry case-level `verified_at` / `evidence_urls` /
`confidence` (honcho#801, qdrant#143, uv#19685, mongodb#1309,
agentic#1382). `--strict` remains 0 errors.

**CHANGELOG doc-drift fix** — entries previously parked under `[Unreleased]`
are realigned to the release they landed in (`[0.6.1]` ← SECURITY /
DISCUSSIONS / Topics / .github / docs/INDEX / README.zh), and missing
segments `[0.6.2]` through `[0.7.0]` are filled in.

## Stats

- 12 profiles / 12 case studies / 11 lessons / 5 anti-patterns
- validate.py --strict: 0 errors
- validate.py --enforce-evidence: 12 warnings

## Known issues (carried from upstream)

- G. `astral-sh-uv/pr-19685-sarif-audit.md`: case frontmatter says
  `status: merged` but GH API returns `state=closed, merged=False`.
- H. `agentic-community-mcp-gateway-registry/pr-1382-auth-md-mermaid-token.md`:
  case frontmatter says `status: open` but GH API returns `merged=True`.

Both pending next real upstream interaction.

## Install

```bash
pip install prgenius-kb
```

Full quickstart: see [`prgenius/README.md`](./prgenius/README.md).
"""
    status, rel = gh("POST", f"/repos/{REPO}/releases", token,
                     body={
                         "tag_name": TAG,
                         "name": "v0.7.1 — MCP --repo-root wiring + PyPI rename + 5-case evidence",
                         "body": notes,
                         "target_commitish": COMMIT_SHA,
                         "draft": False,
                         "prerelease": False,
                     })
    print(f"POST release → {status}", flush=True)
    print(f"  html_url: {rel.get('html_url')}", flush=True)


if __name__ == "__main__":
    main()
