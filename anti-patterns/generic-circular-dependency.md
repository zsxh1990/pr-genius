---
type: Anti-Pattern
key: generic-circular-dependency
description: "PR with circular dependency"
symptom: "Maintainer comments: 'Circular dependency'"
trigger_keywords:
  - "circular dependency"
  - "circular import"
fix_action: "1) Break cycle; 2) Restructure"
severity: high
---

# Circular Dependency

## Pattern

PRs with circular dependency get rejected.

## How to Avoid

1. Break cycle
2. Restructure
