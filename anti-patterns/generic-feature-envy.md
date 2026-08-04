---
type: Anti-Pattern
key: generic-feature-envy
tags: [cron, scheduling, reliability]
description: "PR with feature envy"
symptom: "Maintainer comments: 'Feature envy'"
trigger_keywords:
  - "feature envy"
  - "method belongs elsewhere"
fix_action: "1) Move method; 2) Apply SRP"
created: 2026-07-29
severity: low
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-feature-envy.md
updated: 2026-08-01
confidence: medium
---

# Feature Envy

## Pattern

PRs with feature envy get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Move method
2. Apply SRP
