---
type: Anti-Pattern
key: generic-weak-crypto
description: "PR using weak cryptography"
symptom: "Maintainer comments: 'Weak cryptography'"
trigger_keywords:
  - "weak crypto"
  - "md5"
  - "sha1"
fix_action: "1) Use strong crypto; 2) Update algorithms"
severity: high
---

# Weak Cryptography

## Pattern

PRs using weak cryptography get rejected.

## How to Avoid

1. Use strong crypto
2. Update algorithms
