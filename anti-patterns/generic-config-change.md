---
type: Anti-Pattern
key: generic-config-change
tags: [cron, scheduling, reliability]
description: "PR with config change"
symptom: "Maintainer comments: 'Config change'"
trigger_keywords:
  - "config change"
  - "configuration change"
fix_action: "1) Document change; 2) Get approval"
created: 2026-07-29
severity: medium
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-config-change.md
updated: 2026-08-01
confidence: medium
---

# Config Change

## Pattern

PRs with config change get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Document change
2. Get approval
