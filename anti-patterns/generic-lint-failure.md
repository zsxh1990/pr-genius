---
type: Anti-Pattern
key: generic-lint-failure
tags: [cron, scheduling, reliability]
description: "PR with lint failure"
symptom: "Lint failed"
trigger_keywords:
  - "lint failed"
  - "style check failed"
fix_action: "1) Fix lint; 2) Run linter"
created: 2026-07-29
severity: medium
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-lint-failure.md
updated: 2026-08-01
confidence: medium

---

# Lint Failure

## Pattern

PRs with lint failure get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Fix lint
2. Run linter
