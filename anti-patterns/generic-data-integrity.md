---
type: Anti-Pattern
key: generic-data-integrity
description: "PR忽视数据完整性"
symptom: "Maintainer comments: 'Data integrity issue'"
trigger_keywords:
  - "data integrity"
  - "referential integrity"
fix_action: "1) Add constraints; 2) Add validation"
created: 2026-07-29
severity: high
---

# Data Integrity

## Pattern

PRs忽视数据完整性 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add constraints
2. Add validation
