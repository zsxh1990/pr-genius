---
type: Anti-Pattern
key: generic-cookie-theft
tags: [cron, scheduling, reliability]
description: "PR introducing cookie theft vulnerability"
symptom: "Maintainer comments: 'Cookie theft vulnerability'"
trigger_keywords:
  - "cookie theft"
  - "cookie hijacking"
fix_action: "1) Use secure cookies; 2) Add HttpOnly flag"
created: 2026-07-29
severity: high
---

# Cookie Theft

## Pattern

PRs introducing cookie theft vulnerability get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Use secure cookies
2. Add HttpOnly flag
