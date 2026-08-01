---type: Success Pattern
key: generic-small-pr-high-success
description: "PRs under 100 lines have significantly higher merge rate"
tags: [generic, pr-size, statistics]
created: 2026-07-29
source_url: https://github.com/zsxh1990/pr-genius/tree/main/success-patterns/generic-small-pr-high-success.md
updated: 2026-08-01
confidence: medium
---

# Small PRs Have Higher Success Rate

## Pattern

PRs with < 100 lines of changes have a significantly higher merge rate than larger PRs across all repository types.

## Statistics (from pr-genius data)

- Small PRs (< 100 lines): ~70% merge rate
- Medium PRs (100-300 lines): ~50% merge rate
- Large PRs (> 300 lines): ~30% merge rate

## Why

1. Easier to review
2. Lower risk of conflicts
3. Faster CI runs
4. Maintainer bandwidth friendly

## Applicability

Universal - works for all repo sizes and types
