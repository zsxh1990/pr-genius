---
type: Anti-Pattern
key: generic-hardcoded-secret
description: "PR with hardcoded secret"
symptom: "Maintainer comments: 'Hardcoded secret'"
trigger_keywords:
  - "hardcoded secret"
  - "hardcoded password"
fix_action: "1) Remove secret; 2) Use environment variable"
severity: critical
---

# Hardcoded Secret

## Pattern

PRs with hardcoded secret get rejected.

## How to Avoid

1. Remove secret
2. Use environment variable
