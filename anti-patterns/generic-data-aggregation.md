---
type: Anti-Pattern
key: generic-data-aggregation
description: "PR忽视数据聚合"
symptom: "Maintainer comments: 'Data aggregation issue'"
trigger_keywords:
  - "data aggregation"
  - "group by"
fix_action: "1) Validate aggregation; 2) Add tests"
severity: medium
---

# Data Aggregation

## Pattern

PRs忽视数据聚合 get rejected.

## How to Avoid

1. Validate aggregation
2. Add tests
