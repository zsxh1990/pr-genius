---
type: Anti-Pattern
key: openclaw-session-state-risk
tags: [cron, scheduling, reliability]
description: "OpenClaw PR 涉及会话状态，风险较高"
symptom: "标签包含 merge-risk: session-state"
trigger_keywords:
  - "session-state"
  - "merge-risk: session-state"
fix_action: "1) 测试会话状态迁移; 2) 测试边界情况; 3) 提供回滚方案"
source_pr: "openclaw/openclaw#90421, NousResearch/hermes-agent#53611"
severity: high
evidence:
  - "openclaw #90421: 涉及会话状态，标记 risk-session-state"
  - "NousResearch #53611: 涉及会话拆分，标记 risk-session-state"
created: 2026-07-15
learned_at: 2026-07-15
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/openclaw-session-state-risk.md
updated: 2026-08-01
confidence: medium
---

## 反模式说明

涉及会话状态的 PR 风险较高，可能导致用户会话丢失或状态不一致。

### 触发条件
- 修改会话存储逻辑
- 修改会话迁移逻辑
- 修改会话恢复逻辑

### 如何避免
1. 测试会话状态迁移
2. 测试边界情况（并发、崩溃、恢复）
3. 提供回滚方案

## Applicability

All repository sizes.
