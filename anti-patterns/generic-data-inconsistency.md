---
type: Anti-Pattern
key: generic-data-inconsistency
description: "PR导致数据不一致"
symptom: "Maintainer comments: 'Data inconsistency'"
trigger_keywords:
  - "data inconsistency"
  - "stale data"
fix_action: "1) Add consistency checks; 2) Add validation"
created: 2026-07-29
severity: high
---

# Data Inconsistency

## Pattern

PRs导致数据不一致 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add consistency checks
2. Add validation
