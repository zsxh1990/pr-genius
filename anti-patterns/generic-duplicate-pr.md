---
type: Anti-Pattern
key: generic-duplicate-pr
tags: [cron, scheduling, reliability]
description: "Duplicate PR from same author"
symptom: "Maintainer comments: 'Duplicate of #NNN'"
trigger_keywords:
  - "duplicate"
  - "already exists"
fix_action: "1) Check existing PRs; 2) Close duplicate"
created: 2026-07-29
severity: high
---

# Duplicate PR

## Pattern

Duplicate PRs from same author get closed.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Check existing PRs before submitting
2. Close duplicate if found
