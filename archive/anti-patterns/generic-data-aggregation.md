---
type: Anti-Pattern
key: generic-data-aggregation
tags: [cron, scheduling, reliability]
description: "PR忽视数据聚合"
symptom: "Maintainer comments: 'Data aggregation issue'"
trigger_keywords:
  - "data aggregation"
  - "group by"
fix_action: "1) Validate aggregation; 2) Add tests"
created: 2026-07-29
severity: medium
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-data-aggregation.md
updated: 2026-08-01
confidence: medium

---

# Data Aggregation

## Pattern

PRs忽视数据聚合 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Validate aggregation
2. Add tests
