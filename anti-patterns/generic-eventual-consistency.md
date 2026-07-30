---
type: Anti-Pattern
key: generic-eventual-consistency
tags: [cron, scheduling, reliability]
description: "PR忽视eventual consistency"
symptom: "Maintainer comments: 'Eventual consistency'"
trigger_keywords:
  - "eventual consistency"
  - "weak consistency"
fix_action: "1) Understand tradeoffs; 2) Get approval"
created: 2026-07-29
severity: medium
---

# Eventual Consistency

## Pattern

PRs忽视eventual consistency get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Understand tradeoffs
2. Get approval
