---
type: Anti-Pattern
key: generic-force-push
description: "Force push to shared branch"
symptom: "Maintainer comments: 'Please don't force push'"
trigger_keywords:
  - "force push"
  - "force-with-lease"
fix_action: "1) Use merge commit; 2) Rebase locally"
severity: high
---

# Force Push

## Pattern

Force push to shared branch gets rejected.

## How to Avoid

1. Use merge commit
2. Rebase locally
