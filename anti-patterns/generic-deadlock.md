---
type: Anti-Pattern
key: generic-deadlock
description: "PR introducing deadlock"
symptom: "Maintainer comments: 'Deadlock'"
trigger_keywords:
  - "deadlock"
  - "lock issue"
fix_action: "1) Fix deadlock; 2) Use timeout"
created: 2026-07-29
severity: high
---

# Deadlock

## Pattern

PRs introducing deadlock get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Fix deadlock
2. Use timeout
