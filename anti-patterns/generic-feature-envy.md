---
type: Anti-Pattern
key: generic-feature-envy
description: "PR with feature envy"
symptom: "Maintainer comments: 'Feature envy'"
trigger_keywords:
  - "feature envy"
  - "method belongs elsewhere"
fix_action: "1) Move method; 2) Apply SRP"
severity: low
---

# Feature Envy

## Pattern

PRs with feature envy get rejected.

## How to Avoid

1. Move method
2. Apply SRP
