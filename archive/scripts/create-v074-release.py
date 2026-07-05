#!/usr/bin/env python3
"""Create v0.7.4 release pointing at main HEAD.

Distinguishes from v0.7.3 (which captured the *content* state) by
tagging the *post-improvement* commit with a more accurate version
number that reflects the round-level evidence + CI enforcement +
version bump + README badges. Technically a 0.7.3 → 0.7.4
patch bump because:
- Nothing user-facing breaks
- New optional fields (`delta.verified_at` etc.) land as the
  deeper schema layer they were designed for
- CI gate becomes hard
"""
import json
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.github.com"
HEAD_SHA = "9c5cce9ba67822e1423a84ff809f976127e55eab"
TAG = "v0.7.4"
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
                         "name": "v0.7.4 — Round-level evidence + CI hard-gate + pkg version bump",
                         "body": """\
## What's in v0.7.4

### Round-level evidence fills the deeper schema layer

v0.7.0 / v0.7.1 / v0.7.3 already documented the optional
`delta.verified_at` / `delta.evidence_urls` / `delta.confidence`
fields at the round level. v0.7.4 fills them in for every PR Case
Study's round 1 (`open` action), sourced from GitHub API via the
`refresh-evidence.py` cache:

```yaml
- round: 1
  action: open
  delta:
    kind: code_change
    value: "+283 / -0 / 3 files"
    verified_at: "2026-06-12T01:44:47Z"     # ← new
    evidence_urls:                          # ← new
      - https://github.com/.../pull/801/files
      - https://github.com/.../pull/801
      - https://api.github.com/.../pulls/801/commits
    confidence: high                        # ← new
```

`archive/scripts/inject-round-evidence.py` makes this re-runnable
when new round-1 evidence needs to be added or refreshed.

### CI becomes a hard gate, not a soft warning

`.github/workflows/validate.yml` now has:

```yaml
- name: Run validator (enforce evidence — hard gate)
  run: python3 validate.py --enforce-evidence
```

With **no** `|| echo "::warning::"` fallback. Future PRs that
add a Case Study without case-level `verified_at` /
`evidence_urls` will fail the build red, not just warn.

### Distribution version bump

`prgenius` package internal version:
- `pyproject.toml`: `0.1.0` → **`0.7.3`**
- `src/prgenius/__init__.py`: `__version__ = "0.7.3"`

`python3 -m prgenius --version` now reports `prgenius 0.7.3`. This
aligns internal version with the externally observed release
trajectory since v0.6.0.

### README badges

- `Latest release` shield linking to releases page
- `Evidence 100%` shield pinned on the README (only flips if any
  case study loses case-level evidence)

### `.gitignore` tightening

- `/data` directory (output of `validate.py --snapshot`) now
  reliably excluded; trailing-newline + leading-slash form to
  ensure git's index refresh correctly ignores it.

## Stats

- 12 profiles / 12 case studies / 11 lessons / 5 anti-patterns
- validate.py --strict: 0 errors
- validate.py --enforce-evidence: 0 warnings ✅
- All 11 case studies with round-1 evidence populated
""",
                         "target_commitish": "main",
                         "draft": False,
                         "prerelease": False,
                     })
    if status == 201:
        print(f"Release {TAG} created id={rel.get('id')}", flush=True)
        print(f"→ {rel.get('html_url')}", flush=True)
    elif status == 422:
        print(f"Release {TAG} already exists", flush=True)
    else:
        print(f"Release {TAG}: {status} {rel}", flush=True)


if __name__ == "__main__":
    main()
