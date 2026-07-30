---
type: Anti-Pattern
key: generic-data-types
tags: [cron, scheduling, reliability]
description: "PR忽视数据类型"
symptom: "Maintainer comments: 'Data types issue'"
trigger_keywords:
  - "data types"
  - "type mismatch"
fix_action: "1) Fix types; 2) Add validation"
created: 2026-07-29
severity: medium
---

# Data Types

## Pattern

PRs忽视数据类型 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Fix types
2. Add validation
