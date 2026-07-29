---
type: Anti-Pattern
key: generic-cookie-theft
description: "PR introducing cookie theft vulnerability"
symptom: "Maintainer comments: 'Cookie theft vulnerability'"
trigger_keywords:
  - "cookie theft"
  - "cookie hijacking"
fix_action: "1) Use secure cookies; 2) Add HttpOnly flag"
severity: high
---

# Cookie Theft

## Pattern

PRs introducing cookie theft vulnerability get rejected.

## How to Avoid

1. Use secure cookies
2. Add HttpOnly flag
