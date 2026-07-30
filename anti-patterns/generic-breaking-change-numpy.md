---
type: Anti-Pattern
key: generic-breaking-change-numpy
description: "NumPy rejects breaking changes without NEP"
symptom: "Maintainer comments: 'Please open a NEP first'"
trigger_keywords:
  - "breaking change"
  - "NEP"
fix_action: "1) Open NEP; 2) Get approval; 3) Then submit PR"
created: 2026-07-29
severity: high
---

# NumPy Breaking Change

## Pattern

NumPy requires NEP for breaking changes.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Open NEP first
2. Get approval
3. Then submit PR
