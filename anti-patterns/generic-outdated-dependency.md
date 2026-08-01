---type: Anti-Pattern
key: generic-outdated-dependency
tags: [cron, scheduling, reliability]
description: "PR with outdated dependency"
symptom: "Maintainer comments: 'Outdated dependency'"
trigger_keywords:
  - "outdated dependency"
  - "old version"
fix_action: "1) Update dependency; 2) Check compatibility"
created: 2026-07-29
severity: medium
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-outdated-dependency.md
updated: 2026-08-01
confidence: medium
---

# Outdated Dependency

## Pattern

PRs with outdated dependency get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Update dependency
2. Check compatibility
