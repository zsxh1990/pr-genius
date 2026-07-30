---
type: Anti-Pattern
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
---

# Data Nullable

## Pattern

PRs忽视数据可空性 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Handle nulls
2. Add validation
