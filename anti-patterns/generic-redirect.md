---
type: Anti-Pattern
key: generic-redirect
description: "PR introducing open redirect vulnerability"
symptom: "Maintainer comments: 'Open redirect vulnerability'"
trigger_keywords:
  - "open redirect"
  - "redirect vulnerability"
fix_action: "1) Validate URLs; 2) Whitelist domains"
severity: high
---

# Open Redirect

## Pattern

PRs introducing open redirect vulnerability get rejected.

## How to Avoid

1. Validate URLs
2. Whitelist domains
