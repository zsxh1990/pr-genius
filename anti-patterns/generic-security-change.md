---
type: Anti-Pattern
key: generic-security-change
tags: [cron, scheduling, reliability]
description: "PR with security change"
symptom: "Maintainer comments: 'Security change'"
trigger_keywords:
  - "security change"
  - "auth change"
fix_action: "1) Get security review; 2) Get approval"
created: 2026-07-29
severity: critical
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-security-change.md
updated: 2026-08-01
confidence: medium

---

# Security Change

## Pattern

PRs with security change get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Get security review
2. Get approval
