---type: Anti-Pattern
key: generic-complex-code
tags: [cron, scheduling, reliability]
description: "PR with overly complex code"
symptom: "Maintainer comments: 'Too complex'"
trigger_keywords:
  - "too complex"
  - "cyclomatic complexity"
fix_action: "1) Simplify code; 2) Extract functions"
created: 2026-07-29
severity: low
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-complex-code.md
updated: 2026-08-01
confidence: medium
---

# Complex Code

## Pattern

PRs with overly complex code get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Simplify code
2. Extract functions
