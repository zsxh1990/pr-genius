---type: Anti-Pattern
key: generic-no-game-day-large-repos-final
tags: [cron, scheduling, reliability]
description: "Large repos require game day"
symptom: "Maintainer comments: 'Please build game day'"
trigger_keywords:
  - "no game day"
  - "missing game day"
fix_action: "1) Build game day; 2) Push fix"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-no-game-day-large-repos-final.md
updated: 2026-08-01
confidence: medium
---

# No Game Day (Large Repos)

## Pattern

Large repos require game day for all changes.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1) Build game day
2) Push fix
