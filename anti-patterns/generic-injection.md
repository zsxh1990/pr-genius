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
created: 2026-07-29
severity: critical
---

# Injection

## Pattern

PRs introducing injection vulnerability get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Sanitize input
2. Use parameterized queries
