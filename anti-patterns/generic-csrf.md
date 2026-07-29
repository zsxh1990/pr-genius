---
type: Anti-Pattern
key: generic-csrf
description: "PR introducing CSRF vulnerability"
symptom: "Maintainer comments: 'CSRF vulnerability'"
trigger_keywords:
  - "csrf"
  - "cross-site request forgery"
fix_action: "1) Add CSRF token; 2) Validate origin"
severity: high
---

# CSRF

## Pattern

PRs introducing CSRF vulnerability get rejected.

## How to Avoid

1. Add CSRF token
2. Validate origin
