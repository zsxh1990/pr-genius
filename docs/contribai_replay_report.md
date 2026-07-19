---
type: Research Report
title: ContribAI Anti-Pattern Replay Report
description: pr-genius v1.4.0 验收 — 15 contribai closed-PR 反模式回放检测, 100% hit rate
version: 1.0.0
created: 2026-07-19
generated_by: scripts/contribai_replay.py
---

# ContribAI Anti-Pattern Replay Report

**Generated**: 2026-07-19
**Scenarios**: 15
**Hits**: 15/15 (100.0%)
**Source**: `scripts/contribai_replay.py`

## Per-pattern 结果

| Anti-Pattern | Tier | 命中 | Negative signals |
|---|---|---|---|
| `contribai-duplicate-pr` | high_risk | ✅ | duplicate-pr-same-author, nousresearch-duplicate-pr, contribai-duplicate-pr |
| `contribai-out-of-scope` | high_risk | ✅ | contribai-docs-pr-missing-quickstart, contribai-out-of-scope, first_contributor_large_repo |
| `contribai-not-a-real-bug` | high_risk | ✅ | contribai-not-a-real-bug, first_contributor_large_repo, needs_preflight |
| `contribai-missing-tests` | high_risk | ✅ | contribai-missing-tests, needs_preflight |
| `contribai-archived-repo` | high_risk | ✅ | contribai-archived-repo, first_contributor_large_repo, needs_preflight |
| `contribai-docs-pr-missing-quickstart` | high_risk | ✅ | contribai-docs-pr-missing-quickstart, first_contributor_large_repo, needs_preflight |
| `contribai-design-philosophy-mismatch` | high_risk | ✅ | contribai-design-philosophy-mismatch |
| `contribai-incomplete-readme-contributing` | high_risk | ✅ | contribai-incomplete-readme-contributing |
| `contribai-first-time-large-repo` | high_risk | ✅ | contribai-first-time-large-repo, first_contributor_large_repo, needs_preflight |
| `contribai-breaking-change-no-migration` | high_risk | ✅ | contribai-breaking-change-no-migration, openclaw-compatibility-risk, openclaw-refactor-risk |
| `contribai-performance-benchmark-missing` | high_risk | ✅ | contribai-performance-benchmark-missing, first_contributor_large_repo, needs_preflight |
| `contribai-ethical-review-failed` | high_risk | ✅ | contribai-ethical-review-failed |
| `contribai-site-tos-violation` | high_risk | ✅ | contribai-site-tos-violation |
| `contribai-auto-generated-trash` | high_risk | ✅ | contribai-auto-generated-trash |
| `contribai-needs-rfc-first` | high_risk | ✅ | contribai-needs-rfc-first, needs_preflight |

## 总结

✅ **优秀**：hit rate 100.0%，反模式检测能力强

## v1.4.0 改进方向

- ✅ 全部命中, 准备 Glama public
