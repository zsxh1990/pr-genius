---
type: Lesson
domain: "pr-strategy"
title: "MCP Gateway Registry x3 Mermaid Placeholder Pool: 2 PRs, 1 Mistake Pattern"
verification: "metadata-normalized"
---

# MCP Gateway Registry x3 Mermaid Placeholder Pool: 2 PRs, 1 Mistake Pattern

> Author: 太阳 (Misaka10004)  
> Created: 2026-07-04  
> Status: draft, confidence 0.91 (2 open PRs; merged/not-merged data pending 7/9)  
> Domain: pr-strategy  
> Source: agentic-community/mcp-gateway-registry — PR #1382 + #1383 (2026-07-04 GMT+8)

## Problem

When a maintainer is doing a "merge wave" of small docs fixes
(7/3-7/4 in this case: 9+ PRs merged), **the typo pool has been partially
drained**. Finding 1 pool of 3 similar bugs at the same time = 1 batch.
But once that batch is fixed, **scanning again the same day returns 0
new candidates**.

This is the key observation: typo-pool size is finite per cleanup wave,
but cross-cleared batches exist in adjacent maintainer-controlled areas
(this lesson's case: mermaid `sequenceDiagram` block family).

The strategy that works:

1. Find a "marker commit" from the maintainer (a recent merge that
   signals what was just cleaned)
2. Grep the same file/area for the **same mistake pattern** in
   **neighboring files** the maintainer didn't touch yet
3. Split fixes into 1-file-per-PR (so maintainer can pick one or both)
4. Each diff ≤ 4 lines, each file OK to have 1-2 fixes (don't over-extend)

## Reproduction (worked example)

### Step 1 — Find the marker

Search merged PRs in the last 7 days. Look for typo-fix-shaped commits:

```
agentic-community/mcp-gateway-registry recent merges (7/3-7/4):
  #1381 fix(security): remove weak Keycloak default credentials (SA-9)
  #1380 fix(security): remove orphaned disable-ssl.sh (SA-8)
  #1376 fix(security): loopback-bind non-front-door compose ports (SA-5)
  #1374 security: remove /.well-known/mcp-servers anonymous discovery
  #1375 docs(egress): fix mermaid render — notes/messages with arrow syntax
  #1373 docs(egress): fix mermaid render error in egress-auth-design
  #1372 (fix): checkov skip placement
  #1371 reuse uv.lock for precommit tests
  #1368 remove hardcoded placeholder secrets
```

`#1375 + #1373` both fix mermaid render errors. Both replaced
`<word>` → `[word]`. **This is the marker.**

### Step 2 — Grep the same pattern in docs/*

```bash
# via GitHub API (or local clone)
python3 << 'PY'
import urllib.request, json, base64, re
TOKEN = "..."
def gh(p): ...
files = [e['path'] for e in gh("/repos/.../git/trees/main?recursive=1")['tree']
         if e['path'].startswith('docs/') and e['path'].endswith('.md')]
PH = re.compile(r"<[a-zA-Z][a-zA-Z0-9_-]*>")
# load each file, find lines inside ```mermaid blocks with <word>
# pattern
PY
```

In this case, scanning `docs/auth.md` and `docs/egress-credential-vault.md`
returned 3 hits across 2 files. Auth.md had 1, egress had 2.

### Step 3 — Split 1 file per PR

Even though both files have the same mistake, don't make 1 PR with 2 files.

- **PR #1382** (auth.md, 1 line): `+1/-1`, 1 commit, 1 file
- **PR #1383** (egress-credential-vault.md, 2 lines): `+2/-2`, 1 commit, 1 file

Title pattern (copy maintainer's tone):
- `docs(auth): fix mermaid render of token placeholder`
- `docs(egress-vault): fix mermaid render of placeholders`

Body template (≤ 50 words):
- Line 1: what changed
- Line 2: why (matches existing pattern)

### Step 4 — Wait for the wave

Both PRs opened 7/4. By the time the maintainer finishes 7/3-7/4
batch, the merged rate will trend towards typo-fix mean (~70% merge
within 7 days for docs-only diffs).

## Why 1-file-per-PR (not 1 batched PR)?

Three reasons:

1. **Maintainer has more choice**: can pick the one that fits, decline the other
2. **Bugs them bisects**: if one breaks the docs build, the other stays clean
3. **Credit + record**: each is its own entry in the rounds table

A 2-file PR also works. But it doesn't increase merge rate vs 2-file 1-PR,
only reduces total review latency by maybe 1 hour. Not worth coupling.

## Observed Result (7/4)

| PR | File | Lines | mergeable_state | reviews |
|---|---|---|---|---|
| #1382 | docs/auth.md | 1 | `clean` | 0 |
| #1383 | docs/egress-credential-vault.md | 2 | `clean` (after build) | 0 |

Both `mergeable_state = clean` immediately. **CI = green** in <2 min.
No reviewer activity yet — that's normal at T+0.

## Replay Conditions

This strategy works when:

1. Maintainer is in **batched-merge mode** (look for ≥5 merges in last 48h)
2. **Marker PR exists** that signals an XPath of mistakes
3. **Same mistake pattern** can be found in ≥1 other file the maintainer
   didn't touch
4. **Each candidate diff is XS** (1-4 lines, 1 file)
5. **No overlap with maintainer's open work** (search `is:open` issues)

If any of these fail, the pool is too small to be worth typing — skip.

## Verification

```bash
# 1. Re-run scan after 24h — should still return 0 new candidates
#    if the maintainer batch is closed, this stays 0. If batch is
#    still open, this might surface more.
python3 /tmp/mcp_typo_scan2.py

# 2. Check merge rate at T+7d:
curl -H "Authorization: ..." \
  "https://api.github.com/repos/.../pulls/1382" | jq .merged
curl -H "Authorization: ..." \
  "https://api.github.com/repos/.../pulls/1383" | jq .merged
# Expected: ≥1 merged, target = both
```

If only 1/2 merged: still a positive signal — the typo-pool-x3
strategy had a 50% per-PR merge rate at minimum.

## Lessons Take-away

1. **One pattern marker → multiple file hits** is high-leverage.
2. **Don't batch the PRs at file-count N**: 1-file-per-PR is meta-correct.
3. **CI = docs build** for this repo — auto-validates in <2 min, lets you
   submit the next batch fast.
4. **Maintainer rotate counters** matter: this batch reads as
   `release-cycle-driven cleanup` based on `released v0.6.x` mentions.

## Anti-patterns Avoided

- ❌ Did NOT file "is anyone taking this?" — no comment, no issue, just opened PR
- ❌ Did NOT touch unrelated typos in maintenance files
- ❌ Did NOT add feature/enhancement alongside (would mark mergeable_state unstable)

## Related Sources

- agentic-community/mcp-gateway-registry: https://github.com/agentic-community/mcp-gateway-registry
- pr-genius case study: [agentic-community-mcp-gateway-registry/pr-1382](../agentic-community-mcp-gateway-registry/pr-1382-auth-md-mermaid-token.md)
- pr-genius case study: [agentic-community-mcp-gateway-registry/pr-1383](../agentic-community-mcp-gateway-registry/pr-1383-egress-vault-mermaid-placeholders.md)
- Maintainer marker commits: #1373 + #1375 in same repo
