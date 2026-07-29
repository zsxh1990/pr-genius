---
type: Anti-Pattern
key: generic-data-migration
description: "PR忽视数据迁移"
symptom: "Maintainer comments: 'Data migration issue'"
trigger_keywords:
  - "data migration"
  - "schema migration"
fix_action: "1) Plan migration; 2) Add rollback"
severity: high
---

# Data Migration

## Pattern

PRs忽视数据迁移 get rejected.

## How to Avoid

1. Plan migration
2. Add rollback
