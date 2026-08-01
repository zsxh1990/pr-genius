---type: Anti-Pattern
key: generic-scalability-change
tags: [cron, scheduling, reliability]
description: "PR with scalability change"
symptom: "Maintainer comments: 'Scalability change'"
trigger_keywords:
  - "scalability change"
  - "scale change"
fix_action: "1) Load test; 2) Get approval"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-scalability-change.md
updated: 2026-08-01
confidence: medium
---

# Scalability Change

## Pattern

PRs with scalability change get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Load test
2. Get approval
