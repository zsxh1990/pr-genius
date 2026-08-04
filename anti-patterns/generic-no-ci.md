---
type: Anti-Pattern
key: generic-no-ci
tags: [cron, scheduling, reliability]
description: "PR without CI"
symptom: "Maintainer comments: 'Please run CI'"
trigger_keywords:
  - "no ci"
  - "missing ci"
fix_action: "1) Run CI; 2) Fix failures"
created: 2026-07-29
severity: medium
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-no-ci.md
updated: 2026-08-01
confidence: medium
---

# No CI

## Pattern

PRs without CI get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Run CI
2. Fix failures
