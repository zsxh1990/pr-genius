---
type: Anti-Pattern
key: generic-data-recovery
description: "PR忽视数据恢复"
symptom: "Maintainer comments: 'Data recovery issue'"
trigger_keywords:
  - "data recovery"
  - "restore"
fix_action: "1) Add recovery; 2) Test recovery"
severity: high
---

# Data Recovery

## Pattern

PRs忽视数据恢复 get rejected.

## How to Avoid

1. Add recovery
2. Test recovery
