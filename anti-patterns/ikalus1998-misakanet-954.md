---
type: Anti-Pattern
key: feat-add-2-more-original-failure-recovery-lessons
description: "feat: add 2 more original failure-recovery lessons (rate-limit auth, cross-repo "
symptom: "已合并 by @Ikalus1988"
trigger_keywords:
  - "feat"
fix_action: "TODO: 从 maintainer 评论中提取具体修复步骤"
source_pr: "Ikalus1988/MisakaNet#954"
severity: medium
evidence:
  - "Ikalus1988/MisakaNet#954: 已合并 by @Ikalus1988"
learned_at: 2026-08-13
---

## 反模式说明

**PR**: [Ikalus1988/MisakaNet#954](https://github.com/Ikalus1988/MisakaNet/pull/954)
**作者**: @elevasyncsolutions-jpg
**标签**: area:docs, area:lessons, needs-human-review, shape-safe, lessons-only
**关闭原因**: 已合并 by @Ikalus1988

### PR 描述

## What changed

Two more original lessons (JSON frontmatter, `evidence_level` E2):

1. **`lessons/contrib/github-rate-limit-auth.md`** — unauthenticated GitHub API search loops hitting the anonymous 60/hr IP quota; fix = authorize every call + tune search frequency.
2. **`lessons/contrib/schema-coupled-cross-repo-ci.md`** — data repo CI stays red until the sibling tools-repo schema PR merges; fix = treat schema+data as one atomic paired change.

Both follow the `lessons/TEMPLATE.md` schema and 

### Maintainer 关键评论

> @Ikalus1988: ## Lesson Quality Gate Failed

The lesson quality gate failed because the lesson files are missing required frontmatter fields.

### 如何避免

TODO: 从上述评论中总结具体避免步骤

### 历史案例

- Ikalus1988/MisakaNet#954: 已合并 by @Ikalus1988
