---
type: Anti-Pattern
key: generic-magic-numbers
tags: [cron, scheduling, reliability]
description: "PR with magic numbers"
symptom: "Maintainer comments: 'Magic numbers'"
trigger_keywords:
  - "magic numbers"
  - "hardcoded values"
fix_action: "1) Extract constants; 2) Use named values"
created: 2026-07-29
severity: low
---

# Magic Numbers

## Pattern

PRs with magic numbers get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Extract constants
2. Use named values
