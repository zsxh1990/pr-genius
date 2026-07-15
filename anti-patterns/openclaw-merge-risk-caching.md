---
type: Anti-Pattern
key: openclaw-merge-risk-caching
description: "OpenClaw PR 涉及缓存风险"
symptom: "标签包含 merge-risk: risk-caching"
trigger_keywords:
  - ""
fix_action: "测试缓存一致性"
source_pr: "NousResearch/hermes-agent#53213"
severity: medium
learned_at: 2026-07-15
---

## 反模式说明

OpenClaw PR 涉及缓存风险。

### 触发条件
- 标签包含 merge-risk: risk-caching

### 如何避免
1. 测试缓存一致性
