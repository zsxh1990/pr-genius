---type: Anti-Pattern
key: openclaw-merge-risk-caching
tags: [cron, scheduling, reliability]
description: "OpenClaw PR 涉及缓存风险"
symptom: "标签包含 merge-risk: risk-caching"
trigger_keywords:
  - "merge risk caching"
fix_action: "测试缓存一致性"
source_pr: "NousResearch/hermes-agent#53213"
severity: medium
created: 2026-07-15
learned_at: 2026-07-15
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/openclaw-merge-risk-caching.md
updated: 2026-08-01
confidence: medium
---

## 反模式说明

OpenClaw PR 涉及缓存风险。

### 触发条件
- 标签包含 merge-risk: risk-caching

### 如何避免
1. 测试缓存一致性

## Applicability

All repository sizes.
