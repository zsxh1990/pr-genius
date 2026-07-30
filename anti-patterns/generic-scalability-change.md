---
type: Anti-Pattern
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
---

# Scalability Change

## Pattern

PRs with scalability change get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Load test
2. Get approval
