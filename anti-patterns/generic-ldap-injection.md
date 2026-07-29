---
type: Anti-Pattern
key: generic-ldap-injection
description: "PR introducing LDAP injection vulnerability"
symptom: "Maintainer comments: 'LDAP injection vulnerability'"
trigger_keywords:
  - "ldap injection"
fix_action: "1) Validate input; 2) Use parameterized queries"
severity: high
---

# LDAP Injection

## Pattern

PRs introducing LDAP injection vulnerability get rejected.

## How to Avoid

1. Validate input
2. Use parameterized queries
