---
type: Anti-Pattern
key: generic-data-recovery
tags: [cron, scheduling, reliability]
description: "PR忽视数据恢复"
symptom: "Maintainer comments: 'Data recovery issue'"
trigger_keywords:
  - "data recovery"
  - "restore"
fix_action: "1) Add recovery; 2) Test recovery"
created: 2026-07-29
severity: high
---

# Data Recovery

## Pattern

PRs忽视数据恢复 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add recovery
2. Test recovery
