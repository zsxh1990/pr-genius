---
type: Anti-Pattern
key: generic-nosql-injection
description: "PR introducing NoSQL injection vulnerability"
symptom: "Maintainer comments: 'NoSQL injection vulnerability'"
trigger_keywords:
  - "nosql injection"
  - "mongodb injection"
fix_action: "1) Validate input; 2) Use parameterized queries"
created: 2026-07-29
severity: high
---

# NoSQL Injection

## Pattern

PRs introducing NoSQL injection vulnerability get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Validate input
2. Use parameterized queries
