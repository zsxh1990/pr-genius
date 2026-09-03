---
type: Anti-Pattern
key: generic-no-tests
tags: [cron, scheduling, reliability]
description: "PR without tests"
symptom: "Maintainer comments: 'Please add tests'"
trigger_keywords:
  - "no tests"
  - "missing tests"
fix_action: "1) Add tests; 2) Verify coverage"
created: 2026-07-29
severity: medium
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-no-tests.md
updated: 2026-08-01
confidence: medium

---

# No Tests

## Pattern

PRs without tests get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add tests
2. Verify coverage
