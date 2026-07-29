---
type: Anti-Pattern
key: generic-data-nullable
description: "PR忽视数据可空性"
symptom: "Maintainer comments: 'Data nullable issue'"
trigger_keywords:
  - "data nullable"
  - "null values"
fix_action: "1) Handle nulls; 2) Add validation"
severity: medium
---

# Data Nullable

## Pattern

PRs忽视数据可空性 get rejected.

## How to Avoid

1. Handle nulls
2. Add validation
