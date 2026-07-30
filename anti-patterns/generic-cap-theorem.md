---
type: Anti-Pattern
key: generic-cap-theorem
tags: [cron, scheduling, reliability]
description: "PR忽视CAP定理"
symptom: "Maintainer comments: 'CAP theorem'"
trigger_keywords:
  - "cap theorem"
  - "consistency availability partition"
fix_action: "1) Understand tradeoffs; 2) Get approval"
created: 2026-07-29
severity: high
---

# CAP Theorem

## Pattern

PRs忽视CAP定理 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Understand tradeoffs
2. Get approval
