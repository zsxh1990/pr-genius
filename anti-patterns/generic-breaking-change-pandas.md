---
type: Anti-Pattern
key: generic-breaking-change-pandas
description: "Pandas rejects breaking changes without deprecation"
symptom: "Maintainer comments: 'Please add deprecation warning first'"
trigger_keywords:
  - "breaking change"
  - "deprecation"
fix_action: "1) Add deprecation warning; 2) Wait 2 releases; 3) Then remove"
created: 2026-07-29
severity: high
---

# Pandas Breaking Change

## Pattern

Pandas requires deprecation warning before breaking changes.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add deprecation warning
2. Wait 2 releases
3. Then remove
