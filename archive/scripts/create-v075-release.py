#!/usr/bin/env python3
"""Create v0.7.5 release for amend-rounds evidence + docs/INDEX sync + badge automation."""
import json
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.github.com"
HEAD_SHA = "5d1ff52d124f5e5f982d69c25ea766a06f44fc01"
TAG = "v0.7.5"
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
        headers={"Authorization": f"Bearer {token}",
                 "Accept": "application/vnd.github+json"},
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
    status, ref = gh("POST", f"/repos/{REPO}/git/refs", token,
                     body={"ref": f"refs/tags/{TAG}", "sha": HEAD_SHA})
    if status == 201:
        print(f"Tag {TAG} created", flush=True)
    elif status == 422:
        print(f"Tag {TAG} already exists", flush=True)
    else:
        print(f"Tag {TAG}: {status} {ref}", flush=True)
        return

    status, rel = gh("POST", f"/repos/{REPO}/releases", token,
                     body={
                         "tag_name": TAG,
                         "name": "v0.7.5 — Amend-round evidence + docs/INDEX sync + badge automation",
                         "body": """\
## v0.7.5 — Three improvements picked from a backlog of "could do later"

### Amend rounds now carry round-level evidence

v0.7.0 / v0.7.1 added the schema for per-round `verified_at` /
`evidence_urls` / `confidence`. v0.7.4 filled in **round 1 (open)**
for every case study. v0.7.5 fills the same fields for **round 2
(amend)** of the 4 cases that have one:

| Case | Round 2 kind | Round 2 evidence |
|---|---|---|
| `e2b #1413` | code_change | timestamp + PR/files URLs, confidence: low |
| `future-agi #778` | no_code_change | timestamp + PR/files URLs, confidence: low |
| `honcho #801` | unknown + `commit: 7ac3afe` | commit-SHA cross-ref URLs, confidence: medium |
| `fastmcp #282` | no_code_change | timestamp + PR/files URLs, confidence: low |

`archive/scripts/inject-round-evidence.py` is now the canonical
way to refresh round-level evidence. Idempotent — running twice
won't double-inject.

### docs/INDEX.md fully rewritten

The agent-readable map was drifting. v0.7.5 rewrites it:

- Adds `prgenius/` Python package section (8 files)
- Adds `archive/scripts/` section (7 one-off / re-runnable scripts)
- Updates profile status table with post-status-drift-fix values
  (agentic #1382/#1383 closed-merged; e2b #1413 closed-not-merged;
  uv #19685 closed-not-merged)
- Adds auto-generated metadata block (versions, latest release,
  validator state) — useful as a quick-look snapshot for agents

### Evidence badge now auto-updates

`archive/scripts/update-evidence-badge.py` reads `validate.py
--enforce-evidence` output, computes coverage %, and emits
`docs/badges/evidence.json` in shields.io dynamic JSON format.

CI workflow gained a step that runs this on every push. README
badge URL is now:

```
https://img.shields.io/badge/dynamic/json
  ?url=https://raw.githubusercontent.com/zsxh1990/pr-genius/main/docs/badges/evidence.json
  &label=evidence+coverage
  &query=$.message
```

Currently shows `100% (11/11)` and auto-flips yellow / red if
`--enforce-evidence` ever reports warnings.

## Stats

- 12 profiles / 11 case studies / 11 lessons / 5 anti-patterns
- validate.py --strict: 0 errors
- validate.py --enforce-evidence: 0 warnings ✅
- 11 case-level + 15 round-level evidence records populated
""",
                         "target_commitish": "main",
                         "draft": False,
                         "prerelease": False,
                     })
    if status == 201:
        print(f"Release {TAG} created id={rel.get('id')}", flush=True)
        print(f"→ {rel.get('html_url')}", flush=True)
    else:
        print(f"Release {TAG}: {status} {rel}", flush=True)


if __name__ == "__main__":
    main()