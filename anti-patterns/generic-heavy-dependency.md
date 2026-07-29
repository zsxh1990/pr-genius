---
type: Anti-Pattern
key: generic-heavy-dependency
description: "PR adding heavy dependency"
symptom: "Maintainer comments: 'Heavy dependency'"
trigger_keywords:
  - "heavy dependency"
  - "large dependency"
fix_action: "1) Use lighter alternative; 2) Implement locally"
severity: medium
---

# Heavy Dependency

## Pattern

PRs adding heavy dependency get rejected.

## How to Avoid

1. Use lighter alternative
2. Implement locally
