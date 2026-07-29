---
type: Anti-Pattern
key: generic-resource-leak
description: "PR introducing resource leak"
symptom: "Maintainer comments: 'Resource leak'"
trigger_keywords:
  - "resource leak"
  - "file handle leak"
fix_action: "1) Close resources; 2) Use try-with-resources"
severity: high
---

# Resource Leak

## Pattern

PRs introducing resource leak get rejected.

## How to Avoid

1. Close resources
2. Use try-with-resources
