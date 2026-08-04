---
type: Anti-Pattern
key: generic-null-pointer
tags: [cron, scheduling, reliability]
description: "PR introducing null pointer exception"
symptom: "Maintainer comments: 'Null pointer exception'"
trigger_keywords:
  - "null pointer"
  - "npe"
fix_action: "1) Add null checks; 2) Use optional"
created: 2026-07-29
severity: medium
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-null-pointer.md
updated: 2026-08-01
confidence: medium
---

# Null Pointer Exception

## Pattern

PRs introducing null pointer exception get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add null checks
2. Use optional
