---
type: Anti-Pattern
key: generic-removed-feature
tags: [cron, scheduling, reliability]
description: "PR using removed feature"
symptom: "Maintainer comments: 'Removed feature'"
trigger_keywords:
  - "removed feature"
  - "no longer available"
fix_action: "1) Use alternative; 2) Update code"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-removed-feature.md
updated: 2026-08-01
confidence: medium
---

# Removed Feature

## Pattern

PRs using removed feature get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Use alternative
2. Update code
