---
type: Anti-Pattern
key: generic-auth-bypass
tags: [cron, scheduling, reliability]
description: "PR introducing auth bypass"
symptom: "Maintainer comments: 'Auth bypass'"
trigger_keywords:
  - "auth bypass"
  - "authentication bypass"
fix_action: "1) Fix auth; 2) Add checks"
created: 2026-07-29
severity: critical
---

# Auth Bypass

## Pattern

PRs introducing auth bypass get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Fix auth
2. Add checks
