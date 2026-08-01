---type: Success Pattern
key: large-repo-breaking-change-rfc
description: "Large repos require RFC for breaking changes — follow the process"
tags: [large-repo, breaking-change, rfc, process]
created: 2026-07-29
source_url: https://github.com/zsxh1990/pr-genius/tree/main/success-patterns/large-repo-breaking-change-rfc.md
updated: 2026-08-01
confidence: medium
---

# Large Repo: RFC for Breaking Changes

## Pattern

Large repos (React, Kubernetes, Rust, etc.) require RFC/KEP/NEP before breaking changes. Submitting a PR without prior discussion will be rejected.

## Success Strategy

1. Open RFC issue first
2. Get maintainer approval
3. Then submit implementation PR

## Evidence

- facebook/react: RFC required for all breaking changes
- kubernetes/kubernetes: KEP required
- rust-lang/rust: RFC required via rust-lang/rfcs
- numpy/numpy: NEP required

## Applicability

Large repos (>10k stars) with formal governance
