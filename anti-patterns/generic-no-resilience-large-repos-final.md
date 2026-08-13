---
type: Anti-Pattern
key: generic-no-resilience-large-repos-final
tags: [cron, scheduling, reliability]
description: "Large repos require resilience"
symptom: "Maintainer comments: 'Please build resilience'"
trigger_keywords:
  - "no resilience"
  - "missing resilience"
fix_action: "1) Build resilience; 2) Push fix"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-no-resilience-large-repos-final.md
updated: 2026-08-01
confidence: medium

---

# No Resilience (Large Repos)

## Pattern

Large repos require resilience for all changes.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1) Build resilience
2) Push fix
