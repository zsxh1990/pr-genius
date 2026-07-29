---
type: Anti-Pattern
key: generic-deadlock
description: "PR introducing deadlock"
symptom: "Maintainer comments: 'Deadlock'"
trigger_keywords:
  - "deadlock"
  - "lock issue"
fix_action: "1) Fix deadlock; 2) Use timeout"
severity: high
---

# Deadlock

## Pattern

PRs introducing deadlock get rejected.

## How to Avoid

1. Fix deadlock
2. Use timeout
