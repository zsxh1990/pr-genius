---
type: Success Pattern
key: large-repo-performance-benchmark
description: "Performance improvements need benchmarks"
tags: [large-repo, performance, benchmark]
created: 2026-07-29
source_url: https://github.com/zsxh1990/pr-genius/tree/main/success-patterns/large-repo-performance-benchmark.md
updated: 2026-08-01
confidence: medium
---

# Large Repo: Performance Improvements Need Benchmarks

## Pattern

Performance improvement PRs in large repos need before/after benchmarks to prove the improvement.

## Success Strategy

1. Benchmark current performance
2. Make the optimization
3. Benchmark again
4. Show improvement in PR

## Evidence

- astral-sh/uv: benchmarks required for perf changes
- rust-lang/rust: benchmarks expected
- pytorch/pytorch: performance PRs need benchmarks

## Applicability

All large repos
