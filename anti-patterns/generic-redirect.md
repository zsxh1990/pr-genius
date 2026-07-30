---
type: Anti-Pattern
key: generic-redirect
description: "PR introducing open redirect vulnerability"
symptom: "Maintainer comments: 'Open redirect vulnerability'"
trigger_keywords:
  - "open redirect"
  - "redirect vulnerability"
fix_action: "1) Validate URLs; 2) Whitelist domains"
created: 2026-07-29
severity: high
---

# Open Redirect

## Pattern

PRs introducing open redirect vulnerability get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Validate URLs
2. Whitelist domains
