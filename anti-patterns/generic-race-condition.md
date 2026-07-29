---
type: Anti-Pattern
key: generic-race-condition
description: "PR introducing race condition"
symptom: "Maintainer comments: 'Race condition'"
trigger_keywords:
  - "race condition"
  - "concurrency issue"
fix_action: "1) Add synchronization; 2) Fix race"
severity: high
---

# Race Condition

## Pattern

PRs introducing race condition get rejected.

## How to Avoid

1. Add synchronization
2. Fix race
