---
type: Anti-Pattern
key: generic-duplicate-pr
description: "Duplicate PR from same author"
symptom: "Maintainer comments: 'Duplicate of #NNN'"
trigger_keywords:
  - "duplicate"
  - "already exists"
fix_action: "1) Check existing PRs; 2) Close duplicate"
severity: high
---

# Duplicate PR

## Pattern

Duplicate PRs from same author get closed.

## How to Avoid

1. Check existing PRs before submitting
2. Close duplicate if found
