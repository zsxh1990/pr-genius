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
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-cap-theorem.md
updated: 2026-08-01
confidence: medium
---

# CAP Theorem

## Pattern

PRs忽视CAP定理 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Understand tradeoffs
2. Get approval
