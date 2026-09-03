---
type: Anti-Pattern
key: generic-insufficient-entropy
tags: [cron, scheduling, reliability]
description: "PR with insufficient entropy"
symptom: "Maintainer comments: 'Insufficient entropy'"
trigger_keywords:
  - "insufficient entropy"
  - "weak random"
fix_action: "1) Use secure random; 2) Increase entropy"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-insufficient-entropy.md
updated: 2026-08-01
confidence: medium

---

# Insufficient Entropy

## Pattern

PRs with insufficient entropy get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Use secure random
2. Increase entropy
