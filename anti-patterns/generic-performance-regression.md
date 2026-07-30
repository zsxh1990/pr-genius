---
type: Anti-Pattern
key: generic-performance-regression
tags: [cron, scheduling, reliability]
description: "PR causing performance regression"
symptom: "Maintainer comments: 'Performance regression'"
trigger_keywords:
  - "performance regression"
  - "slower"
fix_action: "1) Profile; 2) Optimize"
created: 2026-07-29
severity: high
---

# Performance Regression

## Pattern

PRs causing performance regression get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Profile
2. Optimize
