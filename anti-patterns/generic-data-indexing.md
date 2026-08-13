---
type: Anti-Pattern
key: generic-data-indexing
tags: [cron, scheduling, reliability]
description: "PR忽视数据索引"
symptom: "Maintainer comments: 'Data indexing issue'"
trigger_keywords:
  - "data indexing"
  - "database index"
fix_action: "1) Add index; 2) Optimize queries"
created: 2026-07-29
severity: medium
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-data-indexing.md
updated: 2026-08-01
confidence: medium

---

# Data Indexing

## Pattern

PRs忽视数据索引 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add index
2. Optimize queries
