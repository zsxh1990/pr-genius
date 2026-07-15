---
type: Anti-Pattern
key: openclaw-sweeper-not-planned
description: "OpenClaw PR 被标记为 not-planned，不会被合并"
symptom: "标签包含 sweeper:not-planned"
trigger_keywords:
  - "not-planned"
  - "sweeper:not-planned"
fix_action: "1) 检查 Issue 是否在 roadmap 上; 2) 先开 Issue 讨论再提 PR; 3) 关注 maintainer 的优先级标签"
source_pr: "NousResearch/hermes-agent#50839, NousResearch/hermes-agent#53149"
severity: high
evidence:
  - "NousResearch #50839: 新 provider 插件，标记 not-planned"
  - "NousResearch #53149: 9 个搜索 provider，标记 not-planned"
learned_at: 2026-07-15
---

## 反模式说明

贡献者提交的功能 PR 被标记为 not-planned，意味着 maintainer 不打算在当前方向上合并。

### 触发条件
- PR 功能不在 maintainer 的 roadmap 上
- 功能过于超前或偏离项目方向
- 未事先在 Issue 中讨论

### 如何避免
1. 提 PR 前先开 Issue 讨论
2. 关注项目的 roadmap 和优先级标签
3. 避免提交过于"创意"的功能
