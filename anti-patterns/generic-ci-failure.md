---
type: Anti-Pattern
key: generic-ci-failure
tags: [cron, scheduling, reliability]
description: "PR with CI failure"
symptom: "CI failed"
trigger_keywords:
  - "ci failed"
  - "build failed"
fix_action: "1) Fix CI; 2) Push fix"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-ci-failure.md
updated: 2026-08-01
confidence: medium

---

# CI Failure

## Pattern

PRs with CI failure get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Fix CI
2. Push fix
