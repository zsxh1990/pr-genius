---
type: Anti-Pattern
key: generic-proprietary-dependency
description: "PR adding proprietary dependency"
symptom: "Maintainer comments: 'Proprietary dependency'"
trigger_keywords:
  - "proprietary dependency"
  - "closed source"
fix_action: "1) Use open source; 2) Abstract dependency"
created: 2026-07-29
severity: high
---

# Proprietary Dependency

## Pattern

PRs adding proprietary dependency get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Use open source
2. Abstract dependency
