---type: Anti-Pattern
key: generic-data-nullable
tags: [cron, scheduling, reliability]
description: "PR忽视数据可空性"
symptom: "Maintainer comments: 'Data nullable issue'"
trigger_keywords:
  - "data nullable"
  - "null values"
fix_action: "1) Handle nulls; 2) Add validation"
created: 2026-07-29
severity: medium
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-data-nullable.md
updated: 2026-08-01
confidence: medium
---

# Data Nullable

## Pattern

PRs忽视数据可空性 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Handle nulls
2. Add validation
