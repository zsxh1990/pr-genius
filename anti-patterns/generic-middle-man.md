---
type: Anti-Pattern
key: generic-middle-man
tags: [cron, scheduling, reliability]
description: "PR with middle man"
symptom: "Maintainer comments: 'Middle man'"
trigger_keywords:
  - "middle man"
  - "delegation only"
fix_action: "1) Remove middle man; 2) Direct call"
created: 2026-07-29
severity: low
---

# Middle Man

## Pattern

PRs with middle man get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Remove middle man
2. Direct call
