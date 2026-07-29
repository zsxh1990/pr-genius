---
type: Anti-Pattern
key: generic-code-duplication
description: "PR with code duplication"
symptom: "Maintainer comments: 'Code duplication'"
trigger_keywords:
  - "code duplication"
  - "duplicate code"
fix_action: "1) Extract common code; 2) Use functions"
severity: low
---

# Code Duplication

## Pattern

PRs with code duplication get rejected.

## How to Avoid

1. Extract common code
2. Use functions
