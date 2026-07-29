---
type: Anti-Pattern
key: generic-xxe
description: "PR introducing XXE vulnerability"
symptom: "Maintainer comments: 'XXE vulnerability'"
trigger_keywords:
  - "xxe"
  - "xml external entity"
fix_action: "1) Disable external entities; 2) Validate XML"
severity: high
---

# XXE

## Pattern

PRs introducing XXE vulnerability get rejected.

## How to Avoid

1. Disable external entities
2. Validate XML
