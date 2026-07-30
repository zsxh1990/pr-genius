---
type: Anti-Pattern
key: generic-breaking-change-kubernetes
description: "Kubernetes rejects breaking changes without KEP"
symptom: "Maintainer comments: 'Please open a KEP first'"
trigger_keywords:
  - "breaking change"
  - "KEP"
fix_action: "1) Open KEP; 2) Get approval; 3) Then submit PR"
created: 2026-07-29
severity: high
---

# Kubernetes Breaking Change

## Pattern

Kubernetes requires KEP for breaking changes.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Open KEP first
2. Get approval
3. Then submit PR
