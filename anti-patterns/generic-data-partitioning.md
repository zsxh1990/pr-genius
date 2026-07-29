---
type: Anti-Pattern
key: generic-data-partitioning
description: "PR忽视数据分区"
symptom: "Maintainer comments: 'Data partitioning issue'"
trigger_keywords:
  - "data partitioning"
  - "sharding"
fix_action: "1) Add partitioning; 2) Optimize queries"
severity: high
---

# Data Partitioning

## Pattern

PRs忽视数据分区 get rejected.

## How to Avoid

1. Add partitioning
2. Optimize queries
