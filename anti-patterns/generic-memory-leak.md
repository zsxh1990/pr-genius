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
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-memory-leak.md
updated: 2026-08-01
confidence: medium
---

# Memory Leak

## Pattern

PRs introducing memory leak get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Profile
2. Fix leak
