---type: Anti-Pattern
key: generic-durability-change
tags: [cron, scheduling, reliability]
description: "PR with durability change"
symptom: "Maintainer comments: 'Durability change'"
trigger_keywords:
  - "durability change"
  - "persistence change"
fix_action: "1) Test thoroughly; 2) Get approval"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-durability-change.md
updated: 2026-08-01
confidence: medium
---

# Durability Change

## Pattern

PRs with durability change get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Test thoroughly
2. Get approval
