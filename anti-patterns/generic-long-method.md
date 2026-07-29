---
type: Anti-Pattern
key: generic-long-method
description: "PR with long method"
symptom: "Maintainer comments: 'Method too long'"
trigger_keywords:
  - "long method"
  - "too many lines"
fix_action: "1) Extract method; 2) Apply SRP"
severity: low
---

# Long Method

## Pattern

PRs with long method get rejected.

## How to Avoid

1. Extract method
2. Apply SRP
