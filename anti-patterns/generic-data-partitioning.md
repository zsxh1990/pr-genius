---
type: Anti-Pattern
key: generic-data-partitioning
tags: [cron, scheduling, reliability]
description: "PR忽视数据分区"
symptom: "Maintainer comments: 'Data partitioning issue'"
trigger_keywords:
  - "data partitioning"
  - "sharding"
fix_action: "1) Add partitioning; 2) Optimize queries"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-data-partitioning.md
updated: 2026-08-01
confidence: medium
---

# Data Partitioning

## Pattern

PRs忽视数据分区 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add partitioning
2. Optimize queries
