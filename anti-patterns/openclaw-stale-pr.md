---
type: Anti-Pattern
key: openclaw-stale-pr
description: "OpenClaw PR 长时间无更新被标记 stale"
symptom: "标签包含 stale，状态变为 waiting on author"
trigger_keywords:
  - "stale"
  - "waiting on author"
fix_action: "1) 定期 rebase on main; 2) 回复 maintainer 评论; 3) 更新 proof of work"
source_pr: "openclaw/openclaw#90421, openclaw/openclaw#87304"
severity: medium
evidence:
  - "openclaw #90421: 1个月无更新，标记 stale"
  - "openclaw #87304: 2个月无更新，标记 stale"
learned_at: 2026-07-15
---

## 反模式说明

OpenClaw 更新极快（日均 100+ commits），PR 如果长时间不更新会被标记为 stale。

### 触发条件
- PR 打开后 >1 周未更新
- 未回复 maintainer 评论
- 未提供 proof of work

### 如何避免
1. 每周 rebase on latest main
2. 及时回复 maintainer 评论
3. 提供 proof of work（测试截图、日志等）
