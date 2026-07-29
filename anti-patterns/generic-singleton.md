---
type: Anti-Pattern
key: generic-singleton
description: "PR with singleton pattern"
symptom: "Maintainer comments: 'Singleton pattern'"
trigger_keywords:
  - "singleton"
  - "global instance"
fix_action: "1) Use dependency injection; 2) Remove singleton"
severity: medium
---

# Singleton Pattern

## Pattern

PRs with singleton pattern get rejected.

## How to Avoid

1. Use dependency injection
2. Remove singleton
