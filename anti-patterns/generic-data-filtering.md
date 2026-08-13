---
type: Anti-Pattern
key: generic-data-filtering
tags: [cron, scheduling, reliability]
description: "PR忽视数据过滤"
symptom: "Maintainer comments: 'Data filtering issue'"
trigger_keywords:
  - "data filtering"
  - "where clause"
fix_action: "1) Validate filtering; 2) Add tests"
created: 2026-07-29
severity: medium
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-data-filtering.md
updated: 2026-08-01
confidence: medium

---

# Data Filtering

## Pattern

PRs忽视数据过滤 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Validate filtering
2. Add tests
