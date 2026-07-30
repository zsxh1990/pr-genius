---
type: Success Pattern
key: generic-resolve-conflicts
description: "PRs with merge conflicts cannot be merged"
tags: [generic, conflicts, blocker]
created: 2026-07-29
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
