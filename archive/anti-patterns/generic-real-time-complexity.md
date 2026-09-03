---
type: Anti-Pattern
key: generic-real-time-complexity
tags: [cron, scheduling, reliability]
description: "PR忽视实时处理复杂性"
symptom: "Maintainer comments: 'Real-time complexity'"
trigger_keywords:
  - "real-time complexity"
  - "low latency"
fix_action: "1) Understand complexity; 2) Get approval"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-real-time-complexity.md
updated: 2026-08-01
confidence: medium

---

# Real-time Complexity

## Pattern

PRs忽视实时处理复杂性 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Understand complexity
2. Get approval
