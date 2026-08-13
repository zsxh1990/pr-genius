---
type: Anti-Pattern
key: generic-breaking-change-facebook-react
tags: [cron, scheduling, reliability]
description: "Facebook React rejects breaking changes without RFC"
symptom: "Maintainer comments: 'Please open an RFC first'"
trigger_keywords:
  - "breaking change"
  - "RFC"
fix_action: "1) Open RFC issue; 2) Get approval; 3) Then submit PR"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-breaking-change-facebook-react.md
updated: 2026-08-01
confidence: medium

---

# Facebook React Breaking Change

## Pattern

Facebook React requires RFC for breaking changes.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Open RFC issue first
2. Get approval
3. Then submit PR
