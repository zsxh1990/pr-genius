---
type: Anti-Pattern
key: generic-primitive-obsession
description: "PR with primitive obsession"
symptom: "Maintainer comments: 'Primitive obsession'"
trigger_keywords:
  - "primitive obsession"
  - "using primitives"
fix_action: "1) Use value objects; 2) Extract class"
created: 2026-07-29
severity: low
---

# Primitive Obsession

## Pattern

PRs with primitive obsession get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Use value objects
2. Extract class
