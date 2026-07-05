import urllib.request, json

line = open('/home/eric_jia/.git-credentials').read().splitlines()[0]
user, _, rest = line[len('https://'):].rpartition('@')
u, _, t = user.partition(':')

# PATCH existing v0.7.5 release: rename + retarget to include push-via-api v2
NEW_NAME = "v0.7.5 — Amend-round evidence + docs/INDEX sync + badge automation + push-via-api v2"
NEW_TARGET = "c9366a463f5c4850a0a34cb117c57e067b64dc89"
release_id = 349120080

body_new = """\
## v0.7.5 — round evidence + dynamic badges + INDEX sync + push-via-api v2

### Round-level evidence now at 21/21 (100%)

Schema v0.7.0 added optional per-round `verified_at` /
`evidence_urls` / `confidence`. v0.7.4 filled **round 1 (open)**.
v0.7.5 fills the rest:

- 11/11 round 1 (`action: open`) — `verified_at` from PR `created_at`
  via `refresh-evidence.py`, plus 3 `evidence_urls` (PR files /
  PR human URL / commits API)
- 4/4 amend rounds (e2b / future-agi / honcho / fastmcp) — anchored
  on round-level `timestamp:` or `commit:` SHA; cross-refs GH commit
  URL where present
- 6/6 check_in / bump / human_review rounds — `verified_at` from the
  round's existing comment timestamp + comments API URL

`archive/scripts/inject-round-evidence.py` is re-runnable for new
round-level evidence updates.

### Dynamic shields.io badges (9 endpoints)

`archive/scripts/refresh-badges.py` emits endpoint JSONs under
`docs/badges/` so README badges track real repo state:

| Badge | Source JSON |
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

README now wires 10 badge slots to these (1 to GitHub release API,
1 static, 8 dynamic).

### `docs/INDEX.md` synchronised

- Was stale on the agentic #1382/#1383 "two PRs" claim; actually
  11 case-study files (the two agentic PRs sit in the same profile
  folder but are independent case studies).
- Added `Round-level evidence` row to the Auto-generated metadata table.
- Bumped INDEX frontmatter `version` 0.7.4 → 0.7.5.

### Tooling

- `archive/scripts/inject-round-evidence.py` — round 1 + amend +
  check_in/bump injectors, idempotent on re-run
- `archive/scripts/refresh-badges.py` — endpoint JSON emitter
- `archive/scripts/git-push-via-api.py --push-all-unpushed` — multi-commit
  GH-DB-API push with per-commit parent chaining

### CHANGELOG realignment

`CHANGELOG.md` previously jumped v0.7.1 → [Unreleased]. v0.7.5 entry
backfills `## [0.7.3]` through `## [0.7.5]` sections and adds
`Compare:` lines for the GH Release template.

### Network-route caveat (carried over from v0.7.4)

Three of this release's commits were pushed via the GH DB API (not
`git push`) because WSL→github.com:443 was blocked from
~11:30 GMT+8 today. The `--base-on-remote` workaround plus the new
`--push-all-unpushed` loop made that multi-commit push feasible. See
KNOWN_ISSUES and `archive/scripts/git-push-via-api.py` docstring.

## Stats

- 12 profiles / 12 case studies / 11 lessons / 5 anti-patterns
- validate.py --strict: 0 errors ✅
- validate.py --enforce-evidence: 0 warnings ✅
- Round-level evidence: 21/21 ✅
- Releases published on GH: **10** (this v0.7.5)
"""

req = urllib.request.Request(
    'https://api.github.com/repos/zsxh1990/pr-genius/releases/349120080',
    method='PATCH',
    headers={
        'Authorization': f'Bearer {t}',
        'Accept': 'application/vnd.github+json',
        'Content-Type': 'application/json',
    },
    data=json.dumps({
        'name': NEW_NAME,
        'body': body_new,
        'target_commitish': NEW_TARGET,
    }).encode('utf-8'),
)
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
        print(f'OK status={resp.status}')
        print(f'  new name: {data.get("name")}')
        print(f'  url: {data.get("html_url")}')
except urllib.error.HTTPError as e:
    print(f'FAIL: {e.code} {e.read().decode("utf-8")[:200]}')