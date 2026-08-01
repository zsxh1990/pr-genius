---type: Anti-Pattern
key: generic-data-corruption
tags: [cron, scheduling, reliability]
description: "PR导致数据损坏"
symptom: "Maintainer comments: 'Data corruption'"
trigger_keywords:
  - "data corruption"
  - "data loss"
fix_action: "1) Add checksums; 2) Add validation"
created: 2026-07-29
severity: critical
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-data-corruption.md
updated: 2026-08-01
confidence: medium
---

# Data Corruption

## Pattern

PRs导致数据损坏 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add checksums
2. Add validation
