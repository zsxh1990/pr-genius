---
type: Anti-Pattern
key: generic-no-ci-large
tags: [cron, scheduling, reliability]
description: "Large repos require CI"
symptom: "Maintainer comments: 'Please run CI'"
trigger_keywords:
  - "no ci"
  - "missing ci"
fix_action: "1) Run CI; 2) Fix failures"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-no-ci-large.md
updated: 2026-08-01
confidence: medium

---

# No CI (Large Repos)

## Pattern

Large repos require CI for all changes.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Run CI
2. Fix failures
