---
type: Anti-Pattern
key: generic-index-out-of-bounds
description: "PR introducing index out of bounds"
symptom: "Maintainer comments: 'Index out of bounds'"
trigger_keywords:
  - "index out of bounds"
  - "array index"
fix_action: "1) Add bounds check; 2) Validate index"
severity: medium
---

# Index Out of Bounds

## Pattern

PRs introducing index out of bounds get rejected.

## How to Avoid

1. Add bounds check
2. Validate index
