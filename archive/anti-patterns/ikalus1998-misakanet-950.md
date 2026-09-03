---
type: Anti-Pattern
key: feat-add-3-original-failure-recovery-lessons-webho
description: "feat: add 3 original failure-recovery lessons (webhook dedupe scope, Go toolchai"
symptom: "已合并 by @Ikalus1988"
trigger_keywords:
  - "feat"
fix_action: "TODO: 从 maintainer 评论中提取具体修复步骤"
source_pr: "Ikalus1988/MisakaNet#950"
severity: medium
evidence:
  - "Ikalus1988/MisakaNet#950: 已合并 by @Ikalus1988"
learned_at: 2026-08-13
---

## 反模式说明

**PR**: [Ikalus1988/MisakaNet#950](https://github.com/Ikalus1988/MisakaNet/pull/950)
**作者**: @elevasyncsolutions-jpg
**标签**: area:docs, area:lessons, needs-dco, needs-human-review, shape-safe, lessons-only
**关闭原因**: 已合并 by @Ikalus1988

### PR 描述

## What changed

Adds 3 original, verified failure-recovery lessons to the knowledge base:

1. **`lessons/contrib/webhook-duplicate-delivery-dedupe-scope.md`** — over-broad webhook dedupe keys silently dropping legitimate events; fix = namespace the dedupe marker per producer.
2. **`lessons/contrib/go-toolchain-vuln-bump-wrong-arch.md`** — `bad CPU type` from an architecture-mismatched Go toolchain blocking a security dependency bump; fix = pin tarball to host arch.
3. **`lessons/contrib/acciden

### Maintainer 关键评论

> @Ikalus1988: ## Lesson Quality Gate Failed

The lesson quality gate failed because all 5 lesson files are missing the required `evidence_level` field in the frontmatter.

### 如何避免

TODO: 从上述评论中总结具体避免步骤

### 历史案例

- Ikalus1988/MisakaNet#950: 已合并 by @Ikalus1988
