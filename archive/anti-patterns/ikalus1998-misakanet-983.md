---
type: Anti-Pattern
key: feat-add-3-more-original-failure-recovery-lessons
description: "feat: add 3 more original failure-recovery lessons (git worktree recovery, escro"
symptom: "已合并 by @Ikalus1988"
trigger_keywords:
  - "feat"
fix_action: "TODO: 从 maintainer 评论中提取具体修复步骤"
source_pr: "Ikalus1988/MisakaNet#983"
severity: medium
evidence:
  - "Ikalus1988/MisakaNet#983: 已合并 by @Ikalus1988"
learned_at: 2026-08-13
---

## 反模式说明

**PR**: [Ikalus1988/MisakaNet#983](https://github.com/Ikalus1988/MisakaNet/pull/983)
**作者**: @elevasyncsolutions-jpg
**标签**: area:docs, area:lessons, needs-human-review, shape-safe, lessons-only
**关闭原因**: 已合并 by @Ikalus1988

### PR 描述

Third round of original failure-recovery lessons, JSON frontmatter with `evidence_level: E2`, allowed domains.

- `git-worktree-dangling-commit-recovery.md` — commit "disappearing" after pushing from the wrong worktree; recover via `fsck --lost-found`/`reflog`
- `escrow-fee-rounding-per-provider.md` — floating-point fee math vs integer-unit currency math, per-provider rounding
- `squash-rebase-force-push-lease.md` — squash-rebase rewrites the base; use explicit `--force-with-lease`

Same quality

### Maintainer 关键评论

> @Ikalus1988: PR Genius 分析结果：

- ✅ DCO 签名

### 如何避免

TODO: 从上述评论中总结具体避免步骤

### 历史案例

- Ikalus1988/MisakaNet#983: 已合并 by @Ikalus1988
