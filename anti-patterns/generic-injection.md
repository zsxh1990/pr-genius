---
type: Anti-Pattern
key: generic-injection
description: "PR introducing injection vulnerability"
symptom: "Maintainer comments: 'Injection vulnerability'"
trigger_keywords:
  - "injection"
  - "sql injection"
  - "xss"
fix_action: "1) Sanitize input; 2) Use parameterized queries"
severity: critical
---

# Injection

## Pattern

PRs introducing injection vulnerability get rejected.

## How to Avoid

1. Sanitize input
2. Use parameterized queries
