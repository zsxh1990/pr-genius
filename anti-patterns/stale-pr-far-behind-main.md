---
type: Anti-Pattern
key: stale-pr-far-behind-main
description: "PR 距离 main 太远，冲突无法解决"
symptom: "maintainer 评论: N commits behind main, conflicts in X surface"
trigger_keywords:
  - "commits behind"
  - "conflicts in"
  - "far behind"
fix_action: "1) 定期 rebase on main; 2) 如果冲突太多，关闭 PR 重新提交; 3) 保持 PR 小而聚焦"
source_pr: "openclaw/openclaw#74185"
severity: high
evidence:
  - "openclaw #74185: 7,115 commits behind main，冲突无法解决"
learned_at: 2026-07-15
---

## 反模式说明

PR 长时间未更新，距离 main 分支太远，导致冲突无法解决。

### 触发条件
- PR 打开后长时间未 rebase
- 目标仓库更新频繁
- PR 改动范围太大

### 如何避免
1. 定期 rebase on latest main（至少每周一次）
2. 保持 PR 小而聚焦，减少冲突面
3. 如果冲突太多，关闭 PR 重新提交
4. 使用 `gh pr sync` 保持 fork 更新
