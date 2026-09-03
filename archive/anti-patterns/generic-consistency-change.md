---
type: Anti-Pattern
key: generic-consistency-change
tags: [cron, scheduling, reliability]
description: "PR with consistency change"
symptom: "Maintainer comments: 'Consistency change'"
trigger_keywords:
  - "consistency change"
  - "eventual consistency"
fix_action: "1) Test thoroughly; 2) Get approval"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-consistency-change.md
updated: 2026-08-01
confidence: medium

---

# Consistency Change

## Pattern

PRs with consistency change get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Test thoroughly
2. Get approval
