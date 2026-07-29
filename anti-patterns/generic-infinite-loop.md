---
type: Anti-Pattern
key: generic-infinite-loop
description: "PR introducing infinite loop"
symptom: "Maintainer comments: 'Infinite loop'"
trigger_keywords:
  - "infinite loop"
  - "endless loop"
fix_action: "1) Add termination condition; 2) Add timeout"
severity: high
---

# Infinite Loop

## Pattern

PRs introducing infinite loop get rejected.

## How to Avoid

1. Add termination condition
2. Add timeout
