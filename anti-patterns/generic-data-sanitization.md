---
type: Anti-Pattern
key: generic-data-sanitization
description: "PR忽视数据清理"
symptom: "Maintainer comments: 'Data sanitization issue'"
trigger_keywords:
  - "data sanitization"
  - "input sanitization"
fix_action: "1) Add sanitization; 2) Add tests"
severity: high
---

# Data Sanitization

## Pattern

PRs忽视数据清理 get rejected.

## How to Avoid

1. Add sanitization
2. Add tests
