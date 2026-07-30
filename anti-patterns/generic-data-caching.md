---
type: Anti-Pattern
key: generic-data-caching
description: "PR忽视数据缓存"
symptom: "Maintainer comments: 'Data caching issue'"
trigger_keywords:
  - "data caching"
  - "cache invalidation"
fix_action: "1) Add caching; 2) Add invalidation"
created: 2026-07-29
severity: medium
---

# Data Caching

## Pattern

PRs忽视数据缓存 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add caching
2. Add invalidation
