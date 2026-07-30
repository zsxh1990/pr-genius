---
type: Anti-Pattern
key: generic-stack-overflow
tags: [cron, scheduling, reliability]
description: "PR introducing stack overflow"
symptom: "Maintainer comments: 'Stack overflow'"
trigger_keywords:
  - "stack overflow"
  - "infinite recursion"
fix_action: "1) Add recursion limit; 2) Use iteration"
created: 2026-07-29
severity: high
---

# Stack Overflow

## Pattern

PRs introducing stack overflow get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add recursion limit
2. Use iteration
