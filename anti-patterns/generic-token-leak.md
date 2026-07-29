---
type: Anti-Pattern
key: generic-token-leak
description: "PR introducing token leak vulnerability"
symptom: "Maintainer comments: 'Token leak vulnerability'"
trigger_keywords:
  - "token leak"
  - "api token leak"
fix_action: "1) Rotate tokens; 2) Use secure storage"
severity: critical
---

# Token Leak

## Pattern

PRs introducing token leak vulnerability get rejected.

## How to Avoid

1. Rotate tokens
2. Use secure storage
