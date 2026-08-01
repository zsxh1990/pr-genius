---type: Anti-Pattern
key: generic-index-out-of-bounds
tags: [cron, scheduling, reliability]
description: "PR introducing index out of bounds"
symptom: "Maintainer comments: 'Index out of bounds'"
trigger_keywords:
  - "index out of bounds"
  - "array index"
fix_action: "1) Add bounds check; 2) Validate index"
created: 2026-07-29
severity: medium
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-index-out-of-bounds.md
updated: 2026-08-01
confidence: medium
---

# Index Out of Bounds

## Pattern

PRs introducing index out of bounds get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add bounds check
2. Validate index
