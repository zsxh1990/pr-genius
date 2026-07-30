---
type: Anti-Pattern
key: generic-password-leak
tags: [cron, scheduling, reliability]
description: "PR introducing password leak vulnerability"
symptom: "Maintainer comments: 'Password leak vulnerability'"
trigger_keywords:
  - "password leak"
  - "credential leak"
fix_action: "1) Rotate passwords; 2) Use secure storage"
created: 2026-07-29
severity: critical
---

# Password Leak

## Pattern

PRs introducing password leak vulnerability get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Rotate passwords
2. Use secure storage
