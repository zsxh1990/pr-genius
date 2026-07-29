---
type: Anti-Pattern
key: generic-dos
description: "PR introducing DoS vulnerability"
symptom: "Maintainer comments: 'DoS vulnerability'"
trigger_keywords:
  - "dos"
  - "denial of service"
fix_action: "1) Add rate limiting; 2) Add timeout"
severity: high
---

# DoS

## Pattern

PRs introducing DoS vulnerability get rejected.

## How to Avoid

1. Add rate limiting
2. Add timeout
