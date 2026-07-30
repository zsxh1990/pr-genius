---
type: Anti-Pattern
key: generic-data-access
tags: [cron, scheduling, reliability]
description: "PR忽视数据访问"
symptom: "Maintainer comments: 'Data access issue'"
trigger_keywords:
  - "data access"
  - "data permissions"
fix_action: "1) Control access; 2) Add permissions"
created: 2026-07-29
severity: high
---

# Data Access

## Pattern

PRs忽视数据访问 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Control access
2. Add permissions
