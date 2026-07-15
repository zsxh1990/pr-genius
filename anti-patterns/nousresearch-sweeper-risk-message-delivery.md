---
type: Anti-Pattern
key: nousresearch-sweeper-risk-message-delivery
description: "NousResearch PR 涉及消息投递"
symptom: "标签包含 sweeper: risk-message-delivery"
trigger_keywords:
  - "sweeper risk message delivery"
fix_action: "测试消息投递可靠性"
source_pr: "NousResearch/hermes-agent#53148"
severity: high
learned_at: 2026-07-15
---

## 反模式说明

NousResearch PR 涉及消息投递。

### 触发条件
- 标签包含 sweeper: risk-message-delivery

### 如何避免
1. 测试消息投递可靠性
