---type: Anti-Pattern
key: generic-dead-code
tags: [cron, scheduling, reliability]
description: "PR with dead code"
symptom: "Maintainer comments: 'Dead code'"
trigger_keywords:
  - "dead code"
  - "unused code"
fix_action: "1) Remove dead code; 2) Add tests"
created: 2026-07-29
severity: low
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-dead-code.md
updated: 2026-08-01
confidence: medium
---

# Dead Code

## Pattern

PRs with dead code get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Remove dead code
2. Add tests
