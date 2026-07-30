---
type: Anti-Pattern
key: generic-weak-crypto
tags: [cron, scheduling, reliability]
description: "PR using weak cryptography"
symptom: "Maintainer comments: 'Weak cryptography'"
trigger_keywords:
  - "weak crypto"
  - "md5"
  - "sha1"
fix_action: "1) Use strong crypto; 2) Update algorithms"
created: 2026-07-29
severity: high
---

# Weak Cryptography

## Pattern

PRs using weak cryptography get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Use strong crypto
2. Update algorithms
