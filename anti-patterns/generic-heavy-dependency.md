---
type: Anti-Pattern
key: generic-heavy-dependency
description: "PR adding heavy dependency"
symptom: "Maintainer comments: 'Heavy dependency'"
trigger_keywords:
  - "heavy dependency"
  - "large dependency"
fix_action: "1) Use lighter alternative; 2) Implement locally"
created: 2026-07-29
severity: medium
---

# Heavy Dependency

## Pattern

PRs adding heavy dependency get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Use lighter alternative
2. Implement locally
