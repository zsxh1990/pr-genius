---
type: Anti-Pattern
key: generic-temporal-coupling
tags: [cron, scheduling, reliability]
description: "PR with temporal coupling"
symptom: "Maintainer comments: 'Temporal coupling'"
trigger_keywords:
  - "temporal coupling"
  - "order dependency"
fix_action: "1) Remove order dependency; 2) Use factory"
created: 2026-07-29
severity: medium
---

# Temporal Coupling

## Pattern

PRs with temporal coupling get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Remove order dependency
2. Use factory
