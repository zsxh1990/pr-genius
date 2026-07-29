---
type: Anti-Pattern
key: generic-data-backup
description: "PR忽视数据备份"
symptom: "Maintainer comments: 'Data backup issue'"
trigger_keywords:
  - "data backup"
  - "disaster recovery"
fix_action: "1) Add backup; 2) Test recovery"
severity: high
---

# Data Backup

## Pattern

PRs忽视数据备份 get rejected.

## How to Avoid

1. Add backup
2. Test recovery
