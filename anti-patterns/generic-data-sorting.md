---type: Anti-Pattern
key: generic-data-sorting
tags: [cron, scheduling, reliability]
description: "PR忽视数据排序"
symptom: "Maintainer comments: 'Data sorting issue'"
trigger_keywords:
  - "data sorting"
  - "order by"
fix_action: "1) Validate sorting; 2) Add tests"
created: 2026-07-29
severity: low
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-data-sorting.md
updated: 2026-08-01
confidence: medium
---

# Data Sorting

## Pattern

PRs忽视数据排序 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Validate sorting
2. Add tests
