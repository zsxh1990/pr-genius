---
type: Anti-Pattern
key: generic-deserialization
description: "PR introducing deserialization vulnerability"
symptom: "Maintainer comments: 'Deserialization vulnerability'"
trigger_keywords:
  - "deserialization"
  - "unsafe deserialization"
fix_action: "1) Validate input; 2) Use safe deserializer"
severity: high
---

# Deserialization

## Pattern

PRs introducing deserialization vulnerability get rejected.

## How to Avoid

1. Validate input
2. Use safe deserializer
