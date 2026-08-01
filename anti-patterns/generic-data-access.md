---type: Anti-Pattern
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
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-data-access.md
updated: 2026-08-01
confidence: medium
---

# Data Access

## Pattern

PRs忽视数据访问 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Control access
2. Add permissions
