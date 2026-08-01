---type: Anti-Pattern
key: nousresearch-sweeper-risk-message-delivery
tags: [cron, scheduling, reliability]
description: "NousResearch PR 涉及消息投递"
symptom: "标签包含 sweeper: risk-message-delivery"
trigger_keywords:
  - "sweeper risk message delivery"
fix_action: "测试消息投递可靠性"
source_pr: "NousResearch/hermes-agent#53148"
severity: high
created: 2026-07-15
learned_at: 2026-07-15
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/nousresearch-sweeper-risk-message-delivery.md
updated: 2026-08-01
confidence: medium
---

## 反模式说明

NousResearch PR 涉及消息投递。

### 触发条件
- 标签包含 sweeper: risk-message-delivery

### 如何避免
1. 测试消息投递可靠性

## Applicability

All repository sizes.
