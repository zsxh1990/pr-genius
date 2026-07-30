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
---

# Data Sanitization

## Pattern

PRs忽视数据清理 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add sanitization
2. Add tests
