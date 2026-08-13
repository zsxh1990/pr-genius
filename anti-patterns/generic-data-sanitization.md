---
type: Anti-Pattern
key: generic-data-sanitization
tags: [cron, scheduling, reliability]
description: "PR忽视数据清理"
symptom: "Maintainer comments: 'Data sanitization issue'"
trigger_keywords:
  - "data sanitization"
  - "input sanitization"
fix_action: "1) Add sanitization; 2) Add tests"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-data-sanitization.md
updated: 2026-08-01
confidence: medium

---

# Data Sanitization

## Pattern

PRs忽视数据清理 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add sanitization
2. Add tests
