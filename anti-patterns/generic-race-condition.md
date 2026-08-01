---type: Anti-Pattern
key: generic-race-condition
tags: [cron, scheduling, reliability]
description: "PR introducing race condition"
symptom: "Maintainer comments: 'Race condition'"
trigger_keywords:
  - "race condition"
  - "concurrency issue"
fix_action: "1) Add synchronization; 2) Fix race"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-race-condition.md
updated: 2026-08-01
confidence: medium
---

# Race Condition

## Pattern

PRs introducing race condition get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add synchronization
2. Fix race
