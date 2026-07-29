---
type: Anti-Pattern
key: generic-deep-nesting
description: "PR with deep nesting"
symptom: "Maintainer comments: 'Deep nesting'"
trigger_keywords:
  - "deep nesting"
  - "arrow code"
fix_action: "1) Flatten nesting; 2) Use early returns"
severity: low
---

# Deep Nesting

## Pattern

PRs with deep nesting get rejected.

## How to Avoid

1. Flatten nesting
2. Use early returns
