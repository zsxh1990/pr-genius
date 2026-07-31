---
key: punkpeye-fastmcp-282-too-large
type: Anti-Pattern
repo: punkpeye/fastmcp
created: 2026-07-29
anchors: [282]
tags: [pr-size, first-contribution, maintainer-bandwidth]

trigger_keywords:
  - no-keywords---

# fastmcp: PR Too Large for First Contribution

## Pattern

First-time contributor PR with +271/-16 changes gets closed without review. Maintainer (punkpeye) has limited bandwidth and prefers smaller, focused PRs.

## Evidence

**PR #282** — "feat: add testWithOllama() for local LLM testing"
- Created: 2026-06-28
- Closed: 2026-07-24 (no merge)
- Size: +271/-16, 1 file
- Review: 0 maintainer reviews
- Result: Closed without review

## Root Cause

1. **PR size**: 271 additions is large for a first contribution to a personal project
2. **Maintainer bandwidth**: punkpeye maintains multiple large repos (awesome-mcp-servers 91k stars, fastmcp 3k stars)
3. **No issue first**: PR was not preceded by an issue discussion

## How to Avoid

1. **Split large PRs**: Break into 2-3 smaller PRs (< 100 lines each)
2. **Open issue first**: Discuss the feature before implementing
3. **Start with docs/tests**: First PR should be low-risk (docs fix, test addition)
4. **Check maintainer response time**: If >1 week, consider smaller PRs
