---
type: Anti-Pattern
key: generic-data-validation
description: "PR忽视数据验证"
symptom: "Maintainer comments: 'Data validation issue'"
trigger_keywords:
  - "data validation"
  - "input validation"
fix_action: "1) Add validation; 2) Add tests"
created: 2026-07-29
severity: high
---

# Data Validation

## Pattern

PRs忽视数据验证 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add validation
2. Add tests
