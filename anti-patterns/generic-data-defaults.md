---
type: Anti-Pattern
key: generic-data-defaults
tags: [cron, scheduling, reliability]
description: "PR忽视数据默认值"
symptom: "Maintainer comments: 'Data defaults issue'"
trigger_keywords:
  - "data defaults"
  - "default values"
fix_action: "1) Set defaults; 2) Add validation"
created: 2026-07-29
severity: low
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-data-defaults.md
updated: 2026-08-01
confidence: medium
---

# Data Defaults

## Pattern

PRs忽视数据默认值 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Set defaults
2. Add validation
