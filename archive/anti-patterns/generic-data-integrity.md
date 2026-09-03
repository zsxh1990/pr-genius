---
type: Anti-Pattern
key: generic-data-integrity
tags: [cron, scheduling, reliability]
description: "PR忽视数据完整性"
symptom: "Maintainer comments: 'Data integrity issue'"
trigger_keywords:
  - "data integrity"
  - "referential integrity"
fix_action: "1) Add constraints; 2) Add validation"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-data-integrity.md
updated: 2026-08-01
confidence: medium

---

# Data Integrity

## Pattern

PRs忽视数据完整性 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add constraints
2. Add validation
