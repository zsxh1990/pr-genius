---
type: Anti-Pattern
key: generic-god-class
tags: [cron, scheduling, reliability]
description: "PR with god class"
symptom: "Maintainer comments: 'God class'"
trigger_keywords:
  - "god class"
  - "too many responsibilities"
fix_action: "1) Split class; 2) Apply SRP"
created: 2026-07-29
severity: medium
---

# God Class

## Pattern

PRs with god class get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Split class
2. Apply SRP
