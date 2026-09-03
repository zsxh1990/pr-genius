---
type: Anti-Pattern
key: generic-breaking-change-pytorch
tags: [cron, scheduling, reliability]
description: "PyTorch rejects breaking changes without RFC"
symptom: "Maintainer comments: 'Please open an RFC first'"
trigger_keywords:
  - "breaking change"
  - "RFC"
fix_action: "1) Open RFC; 2) Get approval; 3) Then submit PR"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-breaking-change-pytorch.md
updated: 2026-08-01
confidence: medium

---

# PyTorch Breaking Change

## Pattern

PyTorch requires RFC for breaking changes.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Open RFC first
2. Get approval
3. Then submit PR
