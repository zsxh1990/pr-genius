---
type: Anti-Pattern
key: chore-release-sync-v2-17-lesson-count-and-data-ind
description: "chore(release): sync v2.17 lesson count and data index"
symptom: "已合并 by @Ikalus1988"
trigger_keywords:
  - "chore(release)"
fix_action: "TODO: 从 maintainer 评论中提取具体修复步骤"
source_pr: "Ikalus1988/MisakaNet#996"
severity: medium
evidence:
  - "Ikalus1988/MisakaNet#996: 已合并 by @Ikalus1988"
learned_at: 2026-08-13
---

## 反模式说明

**PR**: [Ikalus1988/MisakaNet#996](https://github.com/Ikalus1988/MisakaNet/pull/996)
**作者**: @Ikalus1988
**标签**: area:tests, area:docs, area:workflow, area:config, area:lessons, area:scripts, risk:high, needs-dco, shape-safe, workflow-change
**关闭原因**: 已合并 by @Ikalus1988

### PR 描述

## Summary

- lessons.json regenerated: 287 → 289 entries (PR #983 batch4 included)
- README.zh-CN.md: 275 → 289
- STATUS.md: 287 → 289
- ROADMAP.md: 287 → 289
- docs/index.html: 235+ → 289+
- docs/data/lessons.json synced
- docs/data/feed.json refreshed
- v2.17.0-plan.md count updated

## Verification

- [x] `python scripts/sync_lesson_count.py --check` → All files consistent: lesson count = 289
- [x] `python scripts/lesson_lint.py --lessons-dir lessons --fail-on high` → 0 high
- [x] Site healt

### Maintainer 关键评论

> @Ikalus1988: <!-- misakanet-pr-shape-guard -->
### ⚠️ PR Shape Guard detected unsafe patch patterns


> @Ikalus1988: ## 🧾 Audit Report — PR #996 (d5b4a9b)

### 📊 Quality Score

### 如何避免

TODO: 从上述评论中总结具体避免步骤

### 历史案例

- Ikalus1988/MisakaNet#996: 已合并 by @Ikalus1988
