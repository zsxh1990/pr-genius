---
type: Anti-Pattern
key: generic-data-quality
tags: [cron, scheduling, reliability]
description: "PR忽视数据质量"
symptom: "Maintainer comments: 'Data quality issue'"
trigger_keywords:
  - "data quality"
  - "dirty data"
fix_action: "1) Validate data; 2) Clean data"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-data-quality.md
updated: 2026-08-01
confidence: medium

---

# Data Quality

## Pattern

PRs忽视数据质量 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Validate data
2. Clean data
