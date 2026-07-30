---
type: Anti-Pattern
key: openclaw-triage-needs-pr-context
description: "OpenClaw PR 缺少上下文"
symptom: "标签包含 triage: needs-pr-context"
trigger_keywords:
  - "triage needs pr context"
fix_action: "提供 PR 背景和动机"
source_pr: "openclaw/openclaw#107829"
severity: medium
learned_at: 2026-07-15
---

## 反模式说明

OpenClaw PR 缺少上下文。

### 触发条件
- 标签包含 triage: needs-pr-context

### 如何避免
1. 提供 PR 背景和动机
