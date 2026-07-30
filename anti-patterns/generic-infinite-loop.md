---
type: Anti-Pattern
key: generic-infinite-loop
tags: [cron, scheduling, reliability]
description: "PR introducing infinite loop"
symptom: "Maintainer comments: 'Infinite loop'"
trigger_keywords:
  - "infinite loop"
  - "endless loop"
fix_action: "1) Add termination condition; 2) Add timeout"
created: 2026-07-29
severity: high
---

# Infinite Loop

## Pattern

PRs introducing infinite loop get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add termination condition
2. Add timeout
