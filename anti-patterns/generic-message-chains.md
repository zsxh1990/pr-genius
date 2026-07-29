---
type: Anti-Pattern
key: generic-message-chains
description: "PR with message chains"
symptom: "Maintainer comments: 'Message chains'"
trigger_keywords:
  - "message chains"
  - "train wreck"
fix_action: "1) Use law of Demeter; 2) Extract method"
severity: low
---

# Message Chains

## Pattern

PRs with message chains get rejected.

## How to Avoid

1. Use law of Demeter
2. Extract method
