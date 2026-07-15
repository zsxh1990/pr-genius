---
type: Anti-Pattern
key: openclaw-stale-with-proof
description: "OpenClaw PR 有 proof 但被标记 stale"
symptom: "标签包含 stale 和 proof: supplied"
trigger_keywords:
  - "stale with proof"
fix_action: "定期更新 PR"
source_pr: "openclaw/openclaw#87304"
severity: medium
learned_at: 2026-07-15
---

## 反模式说明

OpenClaw PR 有 proof 但被标记 stale。

### 触发条件
- 标签包含 stale 和 proof: supplied

### 如何避免
1. 定期更新 PR
