---
type: Anti-Pattern
key: generic-mixed-changes
tags: [cron, scheduling, reliability]
description: "PR with mixed changes"
symptom: "Maintainer comments: 'Please separate changes'"
trigger_keywords:
  - "mixed changes"
  - "unrelated changes"
fix_action: "1) Separate changes; 2) Create multiple PRs"
created: 2026-07-29
severity: medium
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-mixed-changes.md
updated: 2026-08-01
confidence: medium
---

# Mixed Changes

## Pattern

PRs with mixed changes get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Separate changes
2. Create multiple PRs
