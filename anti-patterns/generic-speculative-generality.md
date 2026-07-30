---
type: Anti-Pattern
key: generic-speculative-generality
description: "PR with speculative generality"
symptom: "Maintainer comments: 'Speculative generality'"
trigger_keywords:
  - "speculative generality"
  - "premature abstraction"
fix_action: "1) Remove unused code; 2) Apply YAGNI"
created: 2026-07-29
severity: low
---

# Speculative Generality

## Pattern

PRs with speculative generality get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Remove unused code
2. Apply YAGNI
