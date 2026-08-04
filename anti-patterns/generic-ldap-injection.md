---
type: Anti-Pattern
key: generic-ldap-injection
tags: [cron, scheduling, reliability]
description: "PR introducing LDAP injection vulnerability"
symptom: "Maintainer comments: 'LDAP injection vulnerability'"
trigger_keywords:
  - "ldap injection"
fix_action: "1) Validate input; 2) Use parameterized queries"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-ldap-injection.md
updated: 2026-08-01
confidence: medium
---

# LDAP Injection

## Pattern

PRs introducing LDAP injection vulnerability get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Validate input
2. Use parameterized queries
