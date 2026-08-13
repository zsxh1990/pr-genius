---
type: Anti-Pattern
key: openclaw-merge-risk-blast-contained
tags: [cron, scheduling, reliability]
description: "OpenClaw PR 影响范围可控"
symptom: "标签包含 sweeper: blast-contained"
trigger_keywords:
  - "merge risk blast contained"
fix_action: "保持影响范围可控"
source_pr: "NousResearch/hermes-agent#52865"
severity: low
created: 2026-07-15
learned_at: 2026-07-15
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/openclaw-merge-risk-blast-contained.md
updated: 2026-08-01
confidence: medium

---

## 反模式说明

OpenClaw PR 影响范围可控。

### 触发条件
- 标签包含 sweeper: blast-contained

### 如何避免
1. 保持影响范围可控

## Applicability

All repository sizes.
