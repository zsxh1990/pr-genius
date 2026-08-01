---type: Anti-Pattern
key: generic-no-test-coverage-large
tags: [cron, scheduling, reliability]
description: "Large repos require test coverage"
symptom: "Maintainer comments: 'Please add tests'"
trigger_keywords:
  - "no tests"
  - "missing tests"
fix_action: "1) Add tests; 2) Verify coverage"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-no-test-coverage-large.md
updated: 2026-08-01
confidence: medium
---

# No Test Coverage (Large Repos)

## Pattern

Large repos require test coverage for all changes.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add tests
2. Verify coverage
