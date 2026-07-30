---
type: Anti-Pattern
key: generic-partition-tolerance-change
tags: [cron, scheduling, reliability]
description: "PR with partition tolerance change"
symptom: "Maintainer comments: 'Partition tolerance change'"
trigger_keywords:
  - "partition tolerance"
  - "network partition"
fix_action: "1) Test thoroughly; 2) Get approval"
created: 2026-07-29
severity: high
---

# Partition Tolerance Change

## Pattern

PRs with partition tolerance change get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Test thoroughly
2. Get approval
