#!/usr/bin/env python3
"""create-v077-release.py — Create GitHub tag + release for v0.7.7.

v0.7.6 release was created earlier (tag sha=e7d9b91) at an earlier
snapshot. Subsequent main commits (10 total, including the post-push
rebase to 238bf715 = "fix(p0-p2): version drift to 0.7.5 + profile
evidence 11/11 + round evidence口径一致") are NOT included in v0.7.6.

克莱恩 2026-07-06 12:02 GMT+8 拍板 A: 创建 v0.7.7 release with the
current main HEAD. This is a NEW tag (low risk, no force-move of v0.7.6).

Token: read from ~/.git-credentials (same as git-push-via-api.py pattern).
"""
import urllib.request, json
import urllib.error

line = open('/home/eric_jia/.git-credentials').read().splitlines()[0]
user, _, rest = line[len('https://'):].rpartition('@')
u, _, t = user.partition(':')

# v0.7.7 release target: current main HEAD on remote (post-push rebase)
HEAD_SHA = "238bf7155321e4c869a4defcde7d9592d544f539"
TAG = "v0.7.7"
REPO = "zsxh1990/pr-genius"

body_v077 = """\
## What v0.7.7 ships

v0.7.7 captures the 10 commits since v0.7.6 tag (e7d9b91), of which the
**anchor is the P0-P2 backlog fix on 2026-07-06**:
`fix(p0-p2): version drift to v0.7.5 + profile evidence 11/11 + round evidence口径一致`.

### What changed since v0.7.6 (10 commits)

| Commit | Area |
|---|---|
| `1a52ee1` | feat: 100% round-level evidence + dynamic badges + INDEX.md sync |
| `e74c2ac` | docs: README badges updated to use all 9 dynamic endpoints |
| `a8cce68` | fix(badges): round-evidence filter excludes check_in/bump (actionable-only) |
| `df79c68` | feat(push-via-api): fetch remote commit when --base-on-remote not in local objects |
| `0f10125` | fix(push-via-api): use local parent for diff even with --base-on-remote |
| `fcc9c9c` | feat(push-via-api): add --push-all-unpushed loop mode |
| `8e93908` | chore(archive+docs): v0.7.5 final — release scripts + KNOWN_ISSUES |
| `74d9eb0` | feat(1+2+3): #4 profile verified_at 92% + #7 blog + #1 helper script |
| `85ec679` | chore(archive+docs): v0.7.6 release scripts + KNOWN_ISSUES |
| `238bf71` | **fix(p0-p2): v0.7.5 drift fix + 11/11 profile evidence** |

### P0 fixes (v0.7.7)

- **P0-1**: `latest_release.json` badge v0.7.4 → **v0.7.5** + `prgenius_version.json` 0.7.3 → **0.7.5** + `pyproject.toml` + `__init__.py` version synced to 0.7.5
- **P0-2**: README Stats table — 11 profiles + 1 stub `ag2ai-ag2`, 11 case studies, 5 anti-patterns (was 4), 11 lessons (was 10), round evidence (16/16 across 11 cases)
- **P0-3**: KNOWN_ISSUES `待验证项` — all 4 `[- [ ]]` folded to `[- [x]]` per 克莱恩 2026-07-02 23:29 GMT+8 拍板

### P1 fixes (v0.7.7)

- **P1-1**: 4 profile `index.md` now carry `evidence_urls` + `verified_at: 2026-07-06`:
  - `NousResearch-hermes-agent/index.md`
  - `mongodb-js-mongodb-mcp-server/index.md`
  - `plastic-labs-honcho/index.md`
  - `qdrant-mcp-server-qdrant/index.md`
  - Result: profile-level `evidence_urls` 7/11 → **11/11 (100%)**
- **P1-2**: `docs/INDEX.md` ROUNDS_SCHEMA line corrected — rounds schema is **v0.7.0** (schema evidence layer加固), rounds-v0.5.0 is 2-case migration status (not the schema version itself)
- **P1-3**: `round_evidence.json` badge message "16/16" → "11 round-1 + 4 amend + 1 check-in" (口径一致)
- **P1-4**: `docs/INDEX.md` notes PyPI publish is pending (`pip install prgenius-kb` not yet possible; use `PYTHONPATH=src python -m prgenius` for now)

### Validator state

- `python3 validate.py --strict` ✅
- `python3 validate.py --enforce-evidence` ✅
- `prgenius dump` NDJSON output for 11 cases OK

### Stats (anchored snapshot at 238bf715)

- 11 profiles (live, with `evidence_urls` and `verified_at`) + 1 stub `ag2ai-ag2`
- 11 case studies (2 migrated to v0.5.0 schema: honcho + qdrant; 9 in legacy v0.1)
- 5 anti-patterns
- 11 lessons (`misakanet-50/lesson-01..11`)
- 16/16 round-level evidence (100%) across 11 cases
"""

# 1. Create tag at HEAD
req = urllib.request.Request(
    f'https://api.github.com/repos/{REPO}/git/refs',
    method='POST',
    headers={
        'Authorization': f'Bearer {t}',
        'Accept': 'application/vnd.github+json',
        'Content-Type': 'application/json',
    },
    data=json.dumps({'ref': f'refs/tags/{TAG}', 'sha': HEAD_SHA}).encode('utf-8'),
)
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        print(f'tag {TAG} created at {HEAD_SHA[:12]}')
except urllib.error.HTTPError as e:
    print(f'tag: {e.code} {e.read().decode("utf-8")[:300]}')

# 2. Create release
req = urllib.request.Request(
    f'https://api.github.com/repos/{REPO}/releases',
    method='POST',
    headers={
        'Authorization': f'Bearer {t}',
        'Accept': 'application/vnd.github+json',
        'Content-Type': 'application/json',
    },
    data=json.dumps({
        'tag_name': TAG,
        'name': 'v0.7.7 — P0-P2 drift fix: profiles 11/11 + version 0.7.5 align + KNOWN_ISSUES fold',
        'body': body_v077,
        'target_commitish': 'main',
        'draft': False,
        'prerelease': False,
    }).encode('utf-8'),
)
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
        print(f'release {TAG} created id={data.get("id")}')
        print(f'  → {data.get("html_url")}')
except urllib.error.HTTPError as e:
    print(f'release: {e.code} {e.read().decode("utf-8")[:500]}')
