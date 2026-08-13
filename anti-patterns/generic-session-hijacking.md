---
type: Anti-Pattern
key: generic-session-hijacking
tags: [cron, scheduling, reliability]
description: "PR introducing session hijacking vulnerability"
symptom: "Maintainer comments: 'Session hijacking vulnerability'"
trigger_keywords:
  - "session hijacking"
fix_action: "1) Use secure cookies; 2) Add HttpOnly flag"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-session-hijacking.md
updated: 2026-08-01
confidence: medium

---

# Session Hijacking

## Pattern

PRs introducing session hijacking vulnerability get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Use secure cookies
2. Add HttpOnly flag
