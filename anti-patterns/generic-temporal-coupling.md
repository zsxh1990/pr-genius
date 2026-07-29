---
type: Anti-Pattern
key: generic-temporal-coupling
description: "PR with temporal coupling"
symptom: "Maintainer comments: 'Temporal coupling'"
trigger_keywords:
  - "temporal coupling"
  - "order dependency"
fix_action: "1) Remove order dependency; 2) Use factory"
severity: medium
---

# Temporal Coupling

## Pattern

PRs with temporal coupling get rejected.

## How to Avoid

1. Remove order dependency
2. Use factory
