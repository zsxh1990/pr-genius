---
type: Anti-Pattern
key: generic-primitive-obsession
tags: [cron, scheduling, reliability]
description: "PR with primitive obsession"
symptom: "Maintainer comments: 'Primitive obsession'"
trigger_keywords:
  - "primitive obsession"
  - "using primitives"
fix_action: "1) Use value objects; 2) Extract class"
created: 2026-07-29
severity: low
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-primitive-obsession.md
updated: 2026-08-01
confidence: medium

---

# Primitive Obsession

## Pattern

PRs with primitive obsession get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Use value objects
2. Extract class
