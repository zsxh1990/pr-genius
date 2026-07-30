---
type: Anti-Pattern
key: generic-code-duplication
tags: [cron, scheduling, reliability]
description: "PR with code duplication"
symptom: "Maintainer comments: 'Code duplication'"
trigger_keywords:
  - "code duplication"
  - "duplicate code"
fix_action: "1) Extract common code; 2) Use functions"
created: 2026-07-29
severity: low
---

# Code Duplication

## Pattern

PRs with code duplication get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Extract common code
2. Use functions
