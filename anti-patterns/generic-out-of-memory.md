---
type: Anti-Pattern
key: generic-out-of-memory
description: "PR introducing out of memory"
symptom: "Maintainer comments: 'Out of memory'"
trigger_keywords:
  - "out of memory"
  - "oom"
fix_action: "1) Optimize memory; 2) Add limits"
created: 2026-07-29
severity: high
---

# Out of Memory

## Pattern

PRs introducing out of memory get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Optimize memory
2. Add limits
