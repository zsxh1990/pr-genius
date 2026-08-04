---
type: Anti-Pattern
key: generic-data-pagination
tags: [cron, scheduling, reliability]
description: "PR忽视数据分页"
symptom: "Maintainer comments: 'Data pagination issue'"
trigger_keywords:
  - "data pagination"
  - "cursor pagination"
fix_action: "1) Add pagination; 2) Add tests"
created: 2026-07-29
severity: medium
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-data-pagination.md
updated: 2026-08-01
confidence: medium
---

# Data Pagination

## Pattern

PRs忽视数据分页 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add pagination
2. Add tests
