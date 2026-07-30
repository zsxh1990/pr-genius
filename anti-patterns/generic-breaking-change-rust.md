---
type: Anti-Pattern
key: generic-breaking-change-rust
description: "Rust rejects breaking changes without RFC"
symptom: "Maintainer comments: 'Please open an RFC first'"
trigger_keywords:
  - "breaking change"
  - "RFC"
fix_action: "1) Open RFC; 2) Get approval; 3) Then submit PR"
created: 2026-07-29
severity: high
---

# Rust Breaking Change

## Pattern

Rust requires RFC for breaking changes.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Open RFC first
2. Get approval
3. Then submit PR
