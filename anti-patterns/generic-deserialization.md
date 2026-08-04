---
type: Anti-Pattern
key: generic-deserialization
tags: [cron, scheduling, reliability]
description: "PR introducing deserialization vulnerability"
symptom: "Maintainer comments: 'Deserialization vulnerability'"
trigger_keywords:
  - "deserialization"
  - "unsafe deserialization"
fix_action: "1) Validate input; 2) Use safe deserializer"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-deserialization.md
updated: 2026-08-01
confidence: medium
---

# Deserialization

## Pattern

PRs introducing deserialization vulnerability get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Validate input
2. Use safe deserializer
