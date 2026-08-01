---type: Anti-Pattern
key: generic-data-formats
tags: [cron, scheduling, reliability]
description: "PR忽视数据格式"
symptom: "Maintainer comments: 'Data formats issue'"
trigger_keywords:
  - "data formats"
  - "format mismatch"
fix_action: "1) Fix formats; 2) Add validation"
created: 2026-07-29
severity: medium
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-data-formats.md
updated: 2026-08-01
confidence: medium
---

# Data Formats

## Pattern

PRs忽视数据格式 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Fix formats
2. Add validation
