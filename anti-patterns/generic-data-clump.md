---
type: Anti-Pattern
key: generic-data-clump
description: "PR with data clump"
symptom: "Maintainer comments: 'Data clump'"
trigger_keywords:
  - "data clump"
  - "grouped data"
fix_action: "1) Extract class; 2) Use value object"
severity: low
---

# Data Clump

## Pattern

PRs with data clump get rejected.

## How to Avoid

1. Extract class
2. Use value object
