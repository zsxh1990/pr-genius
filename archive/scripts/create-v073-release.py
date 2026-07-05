#!/usr/bin/env python3
"""Bumps v0.7.1 → v0.7.3 in-place (keep existing tag as committed, just edit
the existing release to point at the new HEAD + republish). Or more cleanly:
make a new release v0.7.3 at the current main HEAD."""
import json
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.github.com"
HEAD_SHA = "4c94126bc9615bb39ed38133d782b3c0e29b4322"
OLD_RELEASE_ID = None  # we'll fetch and edit the existing one
TAG = "v0.7.3"
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
            raw = resp.read()
            return resp.status, (json.loads(raw.decode("utf-8")) if raw else {})
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        return e.code, json.loads(raw) if raw.startswith(("{", "[")) else {"raw": raw}


def main():
    token = get_pat()

    # 1. Create tag ref pointing to HEAD (idempotent: 422 if exists)
    status, ref = gh("POST", f"/repos/{REPO}/git/refs", token,
                     body={"ref": f"refs/tags/{TAG}", "sha": HEAD_SHA})
    if status == 422:
        print(f"Tag {TAG} already exists, won't recreate", flush=True)
    elif status == 201:
        print(f"Tag {TAG} created", flush=True)
    else:
        print(f"Tag create: {status} {ref}", flush=True)

    # 2. Find existing v0.7.1 release to delete OR find v0.7.3 release
    status, existing = gh("GET",
                          f"/repos/{REPO}/releases/tags/v0.7.3", token)
    if status == 200:
        rel_id = existing["id"]
        print(f"v0.7.3 release already exists at id={rel_id} — updating",
              flush=True)
    else:
        # Create fresh
        status, rel = gh("POST", f"/repos/{REPO}/releases", token,
                         body={
                             "tag_name": TAG,
                             "name": "v0.7.3 — 100% case-level evidence + status drift fix",
                             "body": """\
## What's new in v0.7.3

**`--enforce-evidence` converges to 0 warnings.** Every PR Case Study now
carries case-level `verified_at` / 6 `evidence_urls` (one human + 5 GH API
endpoints: pulls / pulls/files / issues/comments / pulls/reviews /
pulls/commits) / `confidence`. validate.py --strict stays 0 errors;
--enforce-evidence drops 22 → 0.

**Status drift fixes (release-blocker sweep).** Case frontmatter and
GH-reported state now match for every case:

- `astral-sh/uv#19685` — `status: merged` → `closed-not-merged` (was
  closed-without-merge at 2026-06-05T14:43:54Z)
- `e2b-dev/E2B#1413` — `status: merged` → `closed-not-merged`
- `agentic-community/mcp-gateway-registry#1382` — `status: open` →
  `closed-merged` (merged 2026-07-04T16:30:18Z by aarora79)
- `agentic-community/mcp-gateway-registry#1383` — `status: open` →
  `closed-merged` (merged 2026-07-04T16:28:52Z)

## What's in v0.7.2 (carried forward)

- `archive/scripts/git-push-via-api.py` — fallback for pushing one commit
  through Git DB API when `github.com:443` is unreachable but
  `api.github.com:443` works; supports `--base-on-remote` to handle the
  date-format SHA divergence (local git uses `+0800`, GH API uses `+08:00`)
- `archive/scripts/create-v071-release.py` — release + tag creation via API

## What's in v0.7.1 (carried forward)

- **Distribution rename** — `prgenius` → **`prgenius-kb`** (PyPI collision
  with an unrelated 2024 GPT-3 PR-description tool)
- **MCP `--repo-root` flag actually flows** — `cli.py` was parsing it but
  ignoring it; `mcp.py` hardcoded `REPO_ROOT` as a module-level constant.
  Both fixed.
- **Cursor / Claude Code / Cline config snippets** in `prgenius/README.md`
- **CHANGELOG doc-drift fix** — `[Unreleased]` realigned to the release
  each entry landed in; missing `[0.6.2]`-`[0.7.0]` segments backfilled

## Stats

- 12 profiles / 12 case studies / 11 lessons / 5 anti-patterns
- validate.py --strict: 0 errors
- validate.py --enforce-evidence: 0 warnings ✅ (100% coverage)

## Install

```bash
pip install prgenius-kb
```

Full quickstart: [`prgenius/README.md`](./prgenius/README.md).
""",
                             "target_commitish": "main",
                             "draft": False,
                             "prerelease": False,
                         })
        if status != 201:
            sys.exit(f"Release create failed: {status} {rel}")
        rel_id = rel["id"]
        print(f"v0.7.3 release created id={rel_id}", flush=True)

    print(f"DONE. https://github.com/{REPO}/releases/tag/{TAG}", flush=True)


if __name__ == "__main__":
    main()
