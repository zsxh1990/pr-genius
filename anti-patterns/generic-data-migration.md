---
type: Anti-Pattern
key: generic-data-migration
tags: [cron, scheduling, reliability]
description: "PR忽视数据迁移"
symptom: "Maintainer comments: 'Data migration issue'"
trigger_keywords:
  - "data migration"
  - "schema migration"
fix_action: "1) Plan migration; 2) Add rollback"
created: 2026-07-29
severity: high
---

# Data Migration

## Pattern

PRs忽视数据迁移 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Plan migration
2. Add rollback
