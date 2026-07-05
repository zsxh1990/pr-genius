#!/usr/bin/env python3
"""Create v0.7.5 GitHub Release pointing at remote main HEAD.

Distinguishes from v0.7.4 (the last manually-published release) by
capturing the round-level evidence + dynamic badges + INDEX.md + CHANGELOG
v0.7.3-0.7.5 realignment + push-via-api v2 (the "1, 3, 4" work pushed
after v0.7.4 was published).
"""
import json
import urllib.request, urllib.error
from pathlib import Path

API = "https://api.github.com"
HEAD_SHA = "c9366a463f5c4850a0a34cb117c57e067b64dc89"  # remote main now
TAG = "v0.7.5"
REPO = "zsxh1990/pr-genius"


def get_pat():
    line = Path.home().joinpath(".git-credentials").read_text().splitlines()
    for raw in line:
        if not raw.startswith("https://"):
            continue
        user_part, _, rest = raw[len("https://"):].rpartition("@")
        u, _, t = user_part.partition(":")
        if u == "zsxh1990":
            return t
    raise RuntimeError("no zsxh1990 PAT")


def gh(method, path, token, body=None):
    req = urllib.request.Request(
        f"{API}{path}", method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
    )
    if body is not None:
        req.add_header("Content-Type", "application/json")
        data = json.dumps(body).encode("utf-8")
    else:
        data = None
    try:
        with urllib.request.urlopen(req, data=data, timeout=30) as resp:
            raw = resp.read()
            return resp.status, json.loads(raw.decode("utf-8")) if raw else {}
    except urllib.error.HTTPError as e:
        return e.code, {"raw": e.read().decode("utf-8", errors="replace")[:300]}


def main():
    token = get_pat()

    # 1. Tag at HEAD
    status, ref = gh("POST", f"/repos/{REPO}/git/refs", token,
                     body={"ref": f"refs/tags/{TAG}", "sha": HEAD_SHA})
    if status == 201:
        print(f"tag {TAG} created", flush=True)
    elif status == 422:
        print(f"tag {TAG} already exists — skipping", flush=True)
    else:
        print(f"tag {TAG}: {status} {ref}", flush=True)
        return

    status, rel = gh("POST", f"/repos/{REPO}/releases", token,
                     body={
                         "tag_name": TAG,
                         "name": "v0.7.5 — 100% round-level evidence + dynamic badges + INDEX sync",
                         "body": """\
## What's in v0.7.5

This release captures the work after v0.7.4: round-level evidence filling,
dynamic shields.io badges, and the `docs/INDEX.md` synchronisation that
came out of 克莱恩's "1, 3, 4"拍板.

### Round-level evidence (21/21 = 100%)

The schema v0.7.0 BC promise of per-round `verified_at` /
`evidence_urls` / `confidence` is now realised across every case study:

- 11/11 round-1 (`action: open`) — `verified_at` from PR `created_at`
  via `refresh-evidence.py`; 3 `evidence_urls` (files / pull / commits)
- 4/4 amend rounds (e2b / future-agi / honcho / fastmcp) — anchored
  on round-level `timestamp:` or `commit:` SHA; cross-refs GH commit
  URL where present
- 6/6 check_in / bump / human_review rounds — `verified_at` from the
  round's existing comment timestamp

`archive/scripts/inject-round-evidence.py` is re-runnable for new rounds.

### Dynamic shields.io badges (9 endpoints)

`archive/scripts/refresh-badges.py` emits endpoint JSONs under
`docs/badges/` so README badges stay in sync with the actual repo
state (counts, validate outcomes, latest release tag, prgenius version):

| Badge | Source |
|---|---|
| `validate` | `validate.json` |
| `evidence` | `evidence.json` |
| `round evidence` | `round_evidence.json` |
| `profiles` | `profiles.json` |
| `cases` | `cases.json` |
| `lessons` | `lessons.json` |
| `releases` | `releases.json` |
| `latest release` | `latest_release.json` |
| `prgenius` | `prgenius_version.json` |

README now wires all 10 badge slots to these endpoints (1 to GitHub's
release-tag API, 1 static "PRs welcome", 8 dynamic).

### `docs/INDEX.md` synchronised

- Was stale: "11 (12 PRs — agentic #1382 + #1383 both closed-merged)"
  miscounted PRs. The correct description is "11 (one PR per file;
  agentic contributes two case-study files in the same profile)".
- Added `Round-level evidence` row (21/21 = 100% coverage).
- Bumped INDEX frontmatter `version` 0.7.4 → 0.7.5 to track content.

### Tooling shipped

- `archive/scripts/inject-round-evidence.py` (round 1 + amend +
  check_in/bump injectors, idempotent on re-run)
- `archive/scripts/refresh-badges.py` (endpoint JSON emitter)
- `archive/scripts/git-push-via-api.py --push-all-unpushed` (multi-commit
  GH-DB-API push with per-commit parent chaining — the loop the v0.7.4
  push was missing for)

### CHANGELOG realignment

`CHANGELOG.md` previously jumped v0.7.1 → [Unreleased]; v0.7.3 / v0.7.4
release commits never landed sections. v0.7.5 entry backfills
`## [0.7.3]` through `## [0.7.5]` sections and adds `Compare:` lines
to the GH Release template.

### Network-route caveat (memory)

Three of this release's five remote commits were pushed via the GH DB
API (not `git push`) because WSL→github.com:443 was blocked from
~11:30 GMT+8 today. The `--base-on-remote` workaround plus the new
`--push-all-unpushed` loop made that multi-commit push feasible. See
KNOWN_ISSUES and `archive/scripts/git-push-via-api.py` docstring.

## Stats

- 12 profiles / 12 case studies / 11 lessons / 5 anti-patterns
- validate.py --strict: 0 errors ✅
- validate.py --enforce-evidence: 0 warnings ✅
- Round-level evidence: 21/21 ✅
- Releases published on GH: **10** (this v0.7.5 is the 10th)
""",
                         "target_commitish": "main",
                         "draft": False,
                         "prerelease": False,
                     })
    if status == 201:
        print(f"release {TAG} created id={rel.get('id')}", flush=True)
        print(f"→ {rel.get('html_url')}", flush=True)
    else:
        print(f"release {TAG}: {status}", flush=True)
        print(rel, flush=True)


if __name__ == "__main__":
    main()