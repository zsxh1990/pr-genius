---type: Anti-Pattern
key: generic-no-changelog
tags: [cron, scheduling, reliability]
description: "PR without changelog"
symptom: "Maintainer comments: 'Please update changelog'"
trigger_keywords:
  - "no changelog"
  - "missing changelog"
fix_action: "1) Update changelog; 2) Add entry"
created: 2026-07-29
severity: low
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-no-changelog.md
updated: 2026-08-01
confidence: medium
---

# No Changelog

## Pattern

PRs without changelog get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Update changelog
2. Add entry
