---
type: Success Pattern
key: generic-dco-signoff
description: "DCO sign-off required for many repos"
tags: [generic, dco, requirement]
created: 2026-07-29
source_url: https://github.com/zsxh1990/pr-genius/tree/main/success-patterns/generic-dco-signoff.md
updated: 2026-08-01
confidence: medium
---

# DCO Sign-off Requirement

## Pattern

Many repos require DCO (Developer Certificate of Origin) sign-off via `git commit -s`.

## Repos Requiring DCO

- MisakaNet
- kubernetes
- Many CNCF projects

## How To

```bash
git commit -s -m "your commit message"
```

## Applicability

Check repo's CONTRIBUTING.md for DCO requirement
