---
type: Anti-Pattern
key: generic-breaking-change-scikit-learn
tags: [cron, scheduling, reliability]
description: "Scikit-learn rejects breaking changes without discussion"
symptom: "Maintainer comments: 'Please discuss first'"
trigger_keywords:
  - "breaking change"
  - "discussion"
fix_action: "1) Open discussion; 2) Get approval; 3) Then submit PR"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-breaking-change-scikit-learn.md
updated: 2026-08-01
confidence: medium

---

# Scikit-learn Breaking Change

## Pattern

Scikit-learn requires discussion for breaking changes.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Open discussion first
2. Get approval
3. Then submit PR
