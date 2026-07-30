---
type: Anti-Pattern
key: generic-no-resilience-large-repos
tags: [cron, scheduling, reliability]
description: "Large repos require resilience"
symptom: "Maintainer comments: 'Please build resilience'"
trigger_keywords:
  - "no resilience"
  - "missing resilience"
fix_action: "1) Build resilience; 2) Push fix"
created: 2026-07-29
severity: high
---

# No Resilience (Large Repos)

## Pattern

Large repos require resilience for all changes.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1) Build resilience
2) Push fix
