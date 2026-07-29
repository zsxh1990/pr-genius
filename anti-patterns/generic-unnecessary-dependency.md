---
type: Anti-Pattern
key: generic-unnecessary-dependency
description: "PR adding unnecessary dependency"
symptom: "Maintainer comments: 'Unnecessary dependency'"
trigger_keywords:
  - "unnecessary dependency"
  - "too many dependencies"
fix_action: "1) Remove dependency; 2) Implement locally"
severity: medium
---

# Unnecessary Dependency

## Pattern

PRs adding unnecessary dependency get rejected.

## How to Avoid

1. Remove dependency
2. Implement locally
