---
type: Anti-Pattern
key: generic-data-filtering
description: "PR忽视数据过滤"
symptom: "Maintainer comments: 'Data filtering issue'"
trigger_keywords:
  - "data filtering"
  - "where clause"
fix_action: "1) Validate filtering; 2) Add tests"
severity: medium
---

# Data Filtering

## Pattern

PRs忽视数据过滤 get rejected.

## How to Avoid

1. Validate filtering
2. Add tests
