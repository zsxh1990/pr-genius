---
type: Anti-Pattern
key: generic-long-method
description: "PR with long method"
symptom: "Maintainer comments: 'Method too long'"
trigger_keywords:
  - "long method"
  - "too many lines"
fix_action: "1) Extract method; 2) Apply SRP"
created: 2026-07-29
severity: low
---

# Long Method

## Pattern

PRs with long method get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Extract method
2. Apply SRP
