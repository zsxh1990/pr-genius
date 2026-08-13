---
type: Anti-Pattern
key: generic-data-parsing
tags: [cron, scheduling, reliability]
description: "PR忽视数据解析"
symptom: "Maintainer comments: 'Data parsing issue'"
trigger_keywords:
  - "data parsing"
  - "parse error"
fix_action: "1) Fix parsing; 2) Add tests"
created: 2026-07-29
severity: medium
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-data-parsing.md
updated: 2026-08-01
confidence: medium

---

# Data Parsing

## Pattern

PRs忽视数据解析 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Fix parsing
2. Add tests
