---
type: Anti-Pattern
key: generic-timeout
tags: [cron, scheduling, reliability]
description: "PR introducing timeout"
symptom: "Maintainer comments: 'Timeout'"
trigger_keywords:
  - "timeout"
  - "hang"
fix_action: "1) Add timeout; 2) Optimize performance"
created: 2026-07-29
severity: medium
---

# Timeout

## Pattern

PRs introducing timeout get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add timeout
2. Optimize performance
