---
type: Anti-Pattern
key: generic-data-retention
description: "PR忽视数据保留"
symptom: "Maintainer comments: 'Data retention issue'"
trigger_keywords:
  - "data retention"
  - "data lifecycle"
fix_action: "1) Set retention; 2) Add cleanup"
severity: medium
---

# Data Retention

## Pattern

PRs忽视数据保留 get rejected.

## How to Avoid

1. Set retention
2. Add cleanup
