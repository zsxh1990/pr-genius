---
type: Anti-Pattern
key: generic-null-pointer
description: "PR introducing null pointer exception"
symptom: "Maintainer comments: 'Null pointer exception'"
trigger_keywords:
  - "null pointer"
  - "npe"
fix_action: "1) Add null checks; 2) Use optional"
severity: medium
---

# Null Pointer Exception

## Pattern

PRs introducing null pointer exception get rejected.

## How to Avoid

1. Add null checks
2. Use optional
