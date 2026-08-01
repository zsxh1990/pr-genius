---type: Anti-Pattern
key: generic-data-constraints
tags: [cron, scheduling, reliability]
description: "PR忽视数据约束"
symptom: "Maintainer comments: 'Data constraints issue'"
trigger_keywords:
  - "data constraints"
  - "check constraints"
fix_action: "1) Add constraints; 2) Add validation"
created: 2026-07-29
severity: medium
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-data-constraints.md
updated: 2026-08-01
confidence: medium
---

# Data Constraints

## Pattern

PRs忽视数据约束 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add constraints
2. Add validation
