---
type: Anti-Pattern
key: generic-data-quality
description: "PR忽视数据质量"
symptom: "Maintainer comments: 'Data quality issue'"
trigger_keywords:
  - "data quality"
  - "dirty data"
fix_action: "1) Validate data; 2) Clean data"
created: 2026-07-29
severity: high
---

# Data Quality

## Pattern

PRs忽视数据质量 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Validate data
2. Clean data
