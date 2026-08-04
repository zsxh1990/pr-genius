---
type: Anti-Pattern
key: generic-no-availability-large-repos
tags: [cron, scheduling, reliability]
description: "Large repos require availability"
symptom: "Maintainer comments: 'Please build availability'"
trigger_keywords:
  - "no availability"
  - "missing availability"
fix_action: "1) Build availability; 2) Push fix"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-no-availability-large-repos.md
updated: 2026-08-01
confidence: medium
---

# No Availability (Large Repos)

## Pattern

Large repos require availability for all changes.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1) Build availability
2) Push fix
