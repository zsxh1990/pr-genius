---
type: Anti-Pattern
key: generic-switch-statements
description: "PR with switch statements"
symptom: "Maintainer comments: 'Switch statements'"
trigger_keywords:
  - "switch statements"
  - "large switch"
fix_action: "1) Use polymorphism; 2) Use strategy pattern"
created: 2026-07-29
severity: low
---

# Switch Statements

## Pattern

PRs with switch statements get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Use polymorphism
2. Use strategy pattern
