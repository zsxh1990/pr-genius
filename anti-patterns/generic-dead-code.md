---
type: Anti-Pattern
key: generic-dead-code
description: "PR with dead code"
symptom: "Maintainer comments: 'Dead code'"
trigger_keywords:
  - "dead code"
  - "unused code"
fix_action: "1) Remove dead code; 2) Add tests"
created: 2026-07-29
severity: low
---

# Dead Code

## Pattern

PRs with dead code get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Remove dead code
2. Add tests
