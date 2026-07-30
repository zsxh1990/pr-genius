---
type: Anti-Pattern
key: generic-token-leak
description: "PR introducing token leak vulnerability"
symptom: "Maintainer comments: 'Token leak vulnerability'"
trigger_keywords:
  - "token leak"
  - "api token leak"
fix_action: "1) Rotate tokens; 2) Use secure storage"
created: 2026-07-29
severity: critical
---

# Token Leak

## Pattern

PRs introducing token leak vulnerability get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Rotate tokens
2. Use secure storage
