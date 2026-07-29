---
type: Anti-Pattern
key: generic-no-ci
description: "PR without CI"
symptom: "Maintainer comments: 'Please run CI'"
trigger_keywords:
  - "no ci"
  - "missing ci"
fix_action: "1) Run CI; 2) Fix failures"
severity: medium
---

# No CI

## Pattern

PRs without CI get rejected.

## How to Avoid

1. Run CI
2. Fix failures
