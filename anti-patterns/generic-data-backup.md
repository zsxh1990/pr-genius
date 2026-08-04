---
type: Anti-Pattern
key: generic-data-backup
tags: [cron, scheduling, reliability]
description: "PR忽视数据备份"
symptom: "Maintainer comments: 'Data backup issue'"
trigger_keywords:
  - "data backup"
  - "disaster recovery"
fix_action: "1) Add backup; 2) Test recovery"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-data-backup.md
updated: 2026-08-01
confidence: medium
---

# Data Backup

## Pattern

PRs忽视数据备份 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add backup
2. Test recovery
