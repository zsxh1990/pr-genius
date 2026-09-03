---
type: Anti-Pattern
key: generic-data-inconsistency
tags: [cron, scheduling, reliability]
description: "PR导致数据不一致"
symptom: "Maintainer comments: 'Data inconsistency'"
trigger_keywords:
  - "data inconsistency"
  - "stale data"
fix_action: "1) Add consistency checks; 2) Add validation"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-data-inconsistency.md
updated: 2026-08-01
confidence: medium

---

# Data Inconsistency

## Pattern

PRs导致数据不一致 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add consistency checks
2. Add validation
