---
type: Anti-Pattern
key: generic-stack-overflow
description: "PR introducing stack overflow"
symptom: "Maintainer comments: 'Stack overflow'"
trigger_keywords:
  - "stack overflow"
  - "infinite recursion"
fix_action: "1) Add recursion limit; 2) Use iteration"
severity: high
---

# Stack Overflow

## Pattern

PRs introducing stack overflow get rejected.

## How to Avoid

1. Add recursion limit
2. Use iteration
