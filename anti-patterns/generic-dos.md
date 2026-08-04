---
type: Anti-Pattern
key: generic-dos
tags: [cron, scheduling, reliability]
description: "PR introducing DoS vulnerability"
symptom: "Maintainer comments: 'DoS vulnerability'"
trigger_keywords:
  - "dos"
  - "denial of service"
fix_action: "1) Add rate limiting; 2) Add timeout"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-dos.md
updated: 2026-08-01
confidence: medium
---

# DoS

## Pattern

PRs introducing DoS vulnerability get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add rate limiting
2. Add timeout
