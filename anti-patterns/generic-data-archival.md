---
type: Anti-Pattern
key: generic-data-archival
tags: [cron, scheduling, reliability]
description: "PR忽视数据归档"
symptom: "Maintainer comments: 'Data archival issue'"
trigger_keywords:
  - "data archival"
  - "cold storage"
fix_action: "1) Archive data; 2) Add storage"
created: 2026-07-29
severity: medium
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-data-archival.md
updated: 2026-08-01
confidence: medium
---

# Data Archival

## Pattern

PRs忽视数据归档 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Archive data
2. Add storage
