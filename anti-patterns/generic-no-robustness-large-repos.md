---type: Anti-Pattern
key: generic-no-robustness-large-repos
tags: [cron, scheduling, reliability]
description: "Large repos require robustness"
symptom: "Maintainer comments: 'Please build robustness'"
trigger_keywords:
  - "no robustness"
  - "missing robustness"
fix_action: "1) Build robustness; 2) Push fix"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-no-robustness-large-repos.md
updated: 2026-08-01
confidence: medium
---

# No Robustness (Large Repos)

## Pattern

Large repos require robustness for all changes.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1) Build robustness
2) Push fix
