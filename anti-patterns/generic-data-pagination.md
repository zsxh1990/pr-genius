---
type: Anti-Pattern
key: generic-data-pagination
description: "PR忽视数据分页"
symptom: "Maintainer comments: 'Data pagination issue'"
trigger_keywords:
  - "data pagination"
  - "cursor pagination"
fix_action: "1) Add pagination; 2) Add tests"
created: 2026-07-29
severity: medium
---

# Data Pagination

## Pattern

PRs忽视数据分页 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add pagination
2. Add tests
