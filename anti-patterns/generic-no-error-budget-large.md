---
type: Anti-Pattern
key: generic-no-error-budget-large
tags: [cron, scheduling, reliability]
description: "Large repos require error budget"
symptom: "Maintainer comments: 'Please add error budget'"
trigger_keywords:
  - "no error budget"
  - "missing error budget"
fix_action: "1) Add error budget; 2) Push fix"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-no-error-budget-large.md
updated: 2026-08-01
confidence: medium
---

# No Error Budget (Large Repos)

## Pattern

Large repos require error budget for all changes.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add error budget
2. Push fix
