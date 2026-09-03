---
type: Anti-Pattern
key: test-bench-add-sag-lite-performance-benchmark-suit
description: "test(bench): add SAG-Lite performance benchmark suite"
symptom: "已合并 by @Ikalus1988"
trigger_keywords:
  - "test(bench)"
fix_action: "TODO: 从 maintainer 评论中提取具体修复步骤"
source_pr: "Ikalus1988/MisakaNet#949"
severity: medium
evidence:
  - "Ikalus1988/MisakaNet#949: 已合并 by @Ikalus1988"
learned_at: 2026-08-13
---

## 反模式说明

**PR**: [Ikalus1988/MisakaNet#949](https://github.com/Ikalus1988/MisakaNet/pull/949)
**作者**: @yunaremaia
**标签**: area:tests, area:scripts, shape-safe
**关闭原因**: 已合并 by @Ikalus1988

### PR 描述

Closes #909

## Goal
Benchmark suite for SAG-Lite search performance (issue #909): latency, throughput, and comparison against the lessons.json keyword fallback.

## Changes
- **scripts/benchmark_sag_lite.py** (new):
  - timed FTS5 index build from the OKF bundle
  - per-query latency (mean/min/max) for SAG-Lite vs the keyword fallback (mirroring `mcp_server._fallback_search` scoring)
  - throughput (qps) and top-1 agreement between the two paths
  - table or `--json` output for reproducible bas

### Maintainer 关键评论

无 maintainer 评论

### 如何避免

TODO: 从上述评论中总结具体避免步骤

### 历史案例

- Ikalus1988/MisakaNet#949: 已合并 by @Ikalus1988
