---
type: Anti-Pattern
key: generic-schema-change
description: "PR with schema change"
symptom: "Maintainer comments: 'Schema change'"
trigger_keywords:
  - "schema change"
  - "database change"
fix_action: "1) Add migration; 2) Get approval"
created: 2026-07-29
severity: high
---

# Schema Change

## Pattern

PRs with schema change get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add migration
2. Get approval
