---
type: Anti-Pattern
key: openclaw-stale-with-proof
tags: [cron, scheduling, reliability]
description: "OpenClaw PR 有 proof 但被标记 stale"
symptom: "标签包含 stale 和 proof: supplied"
trigger_keywords:
  - "stale with proof"
fix_action: "定期更新 PR"
source_pr: "openclaw/openclaw#87304"
severity: medium
created: 2026-07-15
learned_at: 2026-07-15
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/openclaw-stale-with-proof.md
updated: 2026-08-01
confidence: medium
---

## 反模式说明

OpenClaw PR 有 proof 但被标记 stale。

### 触发条件
- 标签包含 stale 和 proof: supplied

### 如何避免
1. 定期更新 PR

## Applicability

All repository sizes.
