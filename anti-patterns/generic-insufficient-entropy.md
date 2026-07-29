---
type: Anti-Pattern
key: generic-insufficient-entropy
description: "PR with insufficient entropy"
symptom: "Maintainer comments: 'Insufficient entropy'"
trigger_keywords:
  - "insufficient entropy"
  - "weak random"
fix_action: "1) Use secure random; 2) Increase entropy"
severity: high
---

# Insufficient Entropy

## Pattern

PRs with insufficient entropy get rejected.

## How to Avoid

1. Use secure random
2. Increase entropy
