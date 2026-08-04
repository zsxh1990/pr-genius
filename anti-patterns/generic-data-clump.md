---
type: Anti-Pattern
key: generic-data-clump
tags: [cron, scheduling, reliability]
description: "PR with data clump"
symptom: "Maintainer comments: 'Data clump'"
trigger_keywords:
  - "data clump"
  - "grouped data"
fix_action: "1) Extract class; 2) Use value object"
created: 2026-07-29
severity: low
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-data-clump.md
updated: 2026-08-01
confidence: medium
---

# Data Clump

## Pattern

PRs with data clump get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Extract class
2. Use value object
