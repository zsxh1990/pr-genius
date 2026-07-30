---
type: Anti-Pattern
key: generic-data-transformation
description: "PR忽视数据转换"
symptom: "Maintainer comments: 'Data transformation issue'"
trigger_keywords:
  - "data transformation"
  - "etl"
fix_action: "1) Validate transformation; 2) Add tests"
created: 2026-07-29
severity: medium
---

# Data Transformation

## Pattern

PRs忽视数据转换 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Validate transformation
2. Add tests
