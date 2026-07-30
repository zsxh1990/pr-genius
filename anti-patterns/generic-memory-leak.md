---
type: Anti-Pattern
key: generic-memory-leak
tags: [cron, scheduling, reliability]
description: "PR introducing memory leak"
symptom: "Maintainer comments: 'Memory leak'"
trigger_keywords:
  - "memory leak"
  - "memory issue"
fix_action: "1) Profile; 2) Fix leak"
created: 2026-07-29
severity: high
---

# Memory Leak

## Pattern

PRs introducing memory leak get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Profile
2. Fix leak
