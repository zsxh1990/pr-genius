---
type: Anti-Pattern
key: generic-csrf
tags: [cron, scheduling, reliability]
description: "PR introducing CSRF vulnerability"
symptom: "Maintainer comments: 'CSRF vulnerability'"
trigger_keywords:
  - "csrf"
  - "cross-site request forgery"
fix_action: "1) Add CSRF token; 2) Validate origin"
created: 2026-07-29
severity: high
---

# CSRF

## Pattern

PRs introducing CSRF vulnerability get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add CSRF token
2. Validate origin
