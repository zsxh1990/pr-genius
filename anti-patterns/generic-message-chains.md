---
type: Anti-Pattern
key: generic-message-chains
tags: [cron, scheduling, reliability]
description: "PR with message chains"
symptom: "Maintainer comments: 'Message chains'"
trigger_keywords:
  - "message chains"
  - "train wreck"
fix_action: "1) Use law of Demeter; 2) Extract method"
created: 2026-07-29
severity: low
---

# Message Chains

## Pattern

PRs with message chains get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Use law of Demeter
2. Extract method
