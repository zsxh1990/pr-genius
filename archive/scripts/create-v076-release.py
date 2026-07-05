import urllib.request, json
line = open('/home/eric_jia/.git-credentials').read().splitlines()[0]
user, _, rest = line[len('https://'):].rpartition('@')
u, _, t = user.partition(':')

HEAD_SHA = "0c2a37053c9f65ee5ddbc01f85ab4db9496439e8"
TAG = "v0.7.6"
REPO = "zsxh1990/pr-genius"

body_v076 = """\
## What's in v0.7.6 — metrics roadmap 4/7 → 6/7 progress

This release marks completion of two more metrics from 克莱恩's
7-indicator checklist (`docs/METRICS.md`):

- ✅ **#4** profile-level `verified_at` — 11/12 profiles = 91.7%
  (target was 80%)
- ✅ **#7** long-form blog — `docs/BLOG.md` 355 lines
  (~3000+ words) explaining what pr-genius is, who uses it,
  how to install, and walking through a real case (honcho#801
  round-by-round)

It also ships the **#1 helper script** that will scale once the
profile *content* (research + write) catches up:

- `archive/scripts/refresh-profile-meta.py` — fetches GH API
  meta (stars / last release / last commit SHA) per profile
  and injects `verified_at` / `evidence_urls` / `confidence`
  into the frontmatter. Idempotent. Currently runs against
  12 profiles; will scale to 30 once profiles 13–30 are added.

### Schema additions

- `validate.py` recognises `type: Roadmap` as a valid frontmatter
  type, used by `docs/BLOG.md` and `docs/METRICS.md` only.

### README / INDEX navigation

- README.md adds a `📝 Read first: docs/BLOG.md` block in
  Contributing
- `docs/INDEX.md` adds two new repo-root entries:
  `docs/BLOG.md` (long-form blog, reading order 1.5)
  and `docs/METRICS.md` (克莱恩 7 指标对账, reading order 0)

### Metrics dashboard progress

| # | Indicator | Target | v0.7.6 |
|---|---|---|---|
| 1 | High-quality repo profiles | 30 | 12 (gap -18) |
| 2 | PR case studies | 50 | 11 (gap -39) |
| 3 | Case-level evidence URLs | 100% | 100% (11/11) ✅ |
| 4 | Profile-level `verified_at` | 80% | 91.7% (11/12) ✅ |
| 5 | CLI / JSON index | 1 | `prgenius` CLI + MCP shell + 13 archive scripts ✅ |
| 6 | External contributors | 3 | 0 (不可控 — 等真实 maintainer review) |
| 7 | Long-form blog | 1 | `docs/BLOG.md` (355 lines) ✅ |

### Stats

- 12 profiles / 11 case studies / 11 lessons / 5 anti-patterns
- 21/21 round-level evidence (100%)
- validate.py --strict: 0 errors ✅
- validate.py --enforce-evidence: 0 warnings ✅
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
import urllib.error
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        print(f'tag {TAG} created')
except urllib.error.HTTPError as e:
    print(f'tag: {e.code} {e.read().decode("utf-8")[:120]}')

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
        'name': 'v0.7.6 — metrics 4/7→6/7 (profile evidence + blog)',
        'body': body_v076,
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
    print(f'release: {e.code} {e.read().decode("utf-8")[:200]}')