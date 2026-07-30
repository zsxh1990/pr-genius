---
type: Anti-Pattern
key: nousresearch-risk-session-state
description: "NousResearch PR 涉及会话状态，风险较高"
symptom: "标签包含 sweeper:risk-session-state"
trigger_keywords:
  - "risk-session-state"
  - "session-state"
fix_action: "1) 提供会话状态迁移方案; 2) 测试边界情况; 3) 提供回滚方案"
source_pr: "NousResearch/hermes-agent#53171, NousResearch/hermes-agent#53611"
severity: high
evidence:
  - "NousResearch #53171: 涉及会话状态，标记 risk-session-state"
  - "NousResearch #53611: 涉及会话拆分，标记 risk-session-state"
learned_at: 2026-07-15
---

## 反模式说明

涉及会话状态的 PR 风险较高，可能导致用户会话丢失或状态不一致。

### 触发条件
- 修改会话存储逻辑
- 修改会话迁移逻辑
- 修改会话恢复逻辑

### 如何避免
1. 提供详细的会话状态迁移方案
2. 测试边界情况（并发、崩溃、恢复）
3. 提供回滚方案
