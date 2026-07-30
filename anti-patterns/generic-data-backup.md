---
type: Anti-Pattern
key: generic-data-backup
description: "PR忽视数据备份"
symptom: "Maintainer comments: 'Data backup issue'"
trigger_keywords:
  - "data backup"
  - "disaster recovery"
fix_action: "1) Add backup; 2) Test recovery"
created: 2026-07-29
severity: high
---

# Data Backup

## Pattern

PRs忽视数据备份 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add backup
2. Test recovery
