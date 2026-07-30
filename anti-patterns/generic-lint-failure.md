---
type: Anti-Pattern
key: generic-lint-failure
description: "PR with lint failure"
symptom: "Lint failed"
trigger_keywords:
  - "lint failed"
  - "style check failed"
fix_action: "1) Fix lint; 2) Run linter"
created: 2026-07-29
severity: medium
---

# Lint Failure

## Pattern

PRs with lint failure get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Fix lint
2. Run linter
