---type: Success Pattern
key: generic-resolve-conflicts
description: "PRs with merge conflicts cannot be merged"
tags: [generic, conflicts, blocker]
created: 2026-07-29
source_url: https://github.com/zsxh1990/pr-genius/tree/main/success-patterns/generic-resolve-conflicts.md
updated: 2026-08-01
confidence: medium
---

# Resolve Merge Conflicts

## Pattern

PRs with merge conflicts cannot be merged. Must rebase or resolve conflicts first.

## How To

```bash
git fetch upstream main
git rebase upstream/main
# resolve conflicts
git push --force-with-lease
```

## Applicability

Universal - all repos
