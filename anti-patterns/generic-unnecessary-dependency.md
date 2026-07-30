---
type: Anti-Pattern
key: generic-unnecessary-dependency
tags: [cron, scheduling, reliability]
description: "PR adding unnecessary dependency"
symptom: "Maintainer comments: 'Unnecessary dependency'"
trigger_keywords:
  - "unnecessary dependency"
  - "too many dependencies"
fix_action: "1) Remove dependency; 2) Implement locally"
created: 2026-07-29
severity: medium
---

# Unnecessary Dependency

## Pattern

PRs adding unnecessary dependency get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Remove dependency
2. Implement locally
