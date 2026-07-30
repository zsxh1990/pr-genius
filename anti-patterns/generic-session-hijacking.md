---
type: Anti-Pattern
key: generic-session-hijacking
description: "PR introducing session hijacking vulnerability"
symptom: "Maintainer comments: 'Session hijacking vulnerability'"
trigger_keywords:
  - "session hijacking"
fix_action: "1) Use secure cookies; 2) Add HttpOnly flag"
created: 2026-07-29
severity: high
---

# Session Hijacking

## Pattern

PRs introducing session hijacking vulnerability get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Use secure cookies
2. Add HttpOnly flag
