---
type: Anti-Pattern
key: misakanet-superseded-pr
description: "Multiple PRs for same issue — later PR supersedes earlier"
tags: [superseded, iteration, pr-management]
created: 2026-08-23
source_url: https://github.com/Ikalus1988/MisakaNet/pull/1214
updated: 2026-08-23
confidence: high
trigger_keywords:
  - "superseded"
  - "replaced by"
  - "new PR"
severity: low
---

# Superseded PR

## Pattern

When iterating on a fix, close the old PR and create a new one rather than force-pushing major changes.

## What Happened

- PR #1213: Initial fix for fatal-guard Windows issue
- PR #1214: Improved fix with temp file approach
- Maintainer cherry-picked #1214, closed #1213

## Why This Works

- Cleaner git history
- Maintainer can compare approaches
- Review comments on old PR preserved

## How to Avoid Getting Stuck

1. If first PR has review feedback, address in new PR
2. Reference old PR in new PR description
3. Close old PR with explanation

## Applicability

Any contribution workflow where iteration is needed.
