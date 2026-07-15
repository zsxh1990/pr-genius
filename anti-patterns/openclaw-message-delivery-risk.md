---
type: Anti-Pattern
key: openclaw-message-delivery-risk
description: "OpenClaw PR 涉及消息投递，风险较高"
symptom: "标签包含 merge-risk: message-delivery"
trigger_keywords:
  - "message-delivery"
  - "merge-risk: message-delivery"
fix_action: "1) 测试消息投递可靠性; 2) 提供回滚方案; 3) 测试边界情况"
source_pr: "NousResearch/hermes-agent#52958, NousResearch/hermes-agent#53148"
severity: high
evidence:
  - "NousResearch #52958: 涉及消息投递，标记 risk-message-delivery"
  - "NousResearch #53148: 涉及消息投递，标记 risk-message-delivery"
learned_at: 2026-07-15
---

## 反模式说明

涉及消息投递的 PR 风险较高，可能导致消息丢失或重复。

### 触发条件
- 修改消息发送逻辑
- 修改消息队列逻辑
- 修改消息重试逻辑

### 如何避免
1. 测试消息投递可靠性
2. 提供回滚方案
3. 测试边界情况（网络中断、服务重启等）
