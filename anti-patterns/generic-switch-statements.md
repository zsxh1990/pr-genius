---
type: Anti-Pattern
key: generic-switch-statements
tags: [cron, scheduling, reliability]
description: "PR with switch statements"
symptom: "Maintainer comments: 'Switch statements'"
trigger_keywords:
  - "switch statements"
  - "large switch"
fix_action: "1) Use polymorphism; 2) Use strategy pattern"
created: 2026-07-29
severity: low
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-switch-statements.md
updated: 2026-08-01
confidence: medium

---

# Switch Statements

## Pattern

PRs with switch statements get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Use polymorphism
2. Use strategy pattern
