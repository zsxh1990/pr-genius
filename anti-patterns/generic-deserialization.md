---
type: Anti-Pattern
key: generic-deserialization
description: "PR introducing deserialization vulnerability"
symptom: "Maintainer comments: 'Deserialization vulnerability'"
trigger_keywords:
  - "deserialization"
  - "unsafe deserialization"
fix_action: "1) Validate input; 2) Use safe deserializer"
created: 2026-07-29
severity: high
---

# Deserialization

## Pattern

PRs introducing deserialization vulnerability get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Validate input
2. Use safe deserializer
