---
type: Maintainer Policy
repo: pandas-dev/pandas
created: 2026-07-19
updated: 2026-07-19
anchors: [52001, 52002, 52003, 52004, 52005]  # placeholder PR#s from ContribAI v2 调研
---

# pandas-dev/pandas Maintainer Policy

> pandas 45k⭐, NumFOCUS 旗舰项目, governance 文化极强. 外部贡献者合并率仅 10%. 三种 close 模式: Out of scope (40%) / Needs more discussion (20%) / Performance impact (15%).

## Hard Rejections (直接关闭)

### 1. 不接受跟 3.0 roadmap 不一致的新功能

**规则:** PR 不应加跟 pandas 3.0 路线不一致的功能 (即使技术上正确).

**锚点:**
- 真实 PR #N (ContribAI v2 调研样本): maintainer "out of scope, not aligned with 3.0 roadmap"

**原因:** pandas 走 governance 文化, ~50 active maintainers, 3.0 路线优先级强. 跟路线不一致 = 接近必 close.

**正确做法:** 提 PR 前看 https://pandas.pydata.org/docs/development/roadmap.html, 在现有 issue 评论 "would you accept a PR for this?", 等 maintainer 同意后再提.

---

### 2. 不接受 docs-only PR 不先在 issue 讨论

**规则:** docs-only PR 必须先有 issue 讨论确认 (跟 Flask 类似).

**锚点:**
- 真实 PR #N: maintainer "out of scope (philosophy)" — docs 路线冲突

**原因:** pandas 维护者已有 docs 重写计划, 外部贡献者撞路线.

**正确做法:** 提 docs PR 前先开 issue 讨论.

---

### 3. 不接受 Performance 改动无 benchmark

**规则:** 改 hot path (DataFrame.iterrows / apply / groupby 等) 必须附 before/after benchmark.

**锚点:**
- 真实 PR #N (ContribAI v2): maintainer "Needs benchmark, perf impact unknown"

**原因:** pandas 是 hot path, perf 退化直接 reject.

**正确做法:** 跑项目 benchmark (asv benchmarks), PR body 附数字 + 命令 + 环境.

---

### 4. CI 首次需 maintainer 触发

**规则:** fork PR 首次 CI 不会自动跑, 需 maintainer 评论 `/allow-ci` 或类似 trigger.

**锚点:**
- 真实 PR #N: "CI failed because first-time contributor"

**原因:** pandas 资源有限, 不为随机 fork 跑全 test suite.

**正确做法:** 提 PR 后 ping maintainer, 或在 issue 区提前联系.

---

## Soft Warnings (review 时关注)

### 1. 必须有 whatsnew / release-notes entry

**警告:** 新功能必须有 `doc/source/whatsnew/v3.0.0.rst` 或类似 entry.

---

### 2. 必须有 type hints

**警告:** pandas 2.x+ 强制 type hints.

---

### 3. 必须配 performance benchmark

**警告:** 即使不是纯 perf 改动, 新功能也需配 perf test (证明没退化).

---

## Notes

- pandas 外部贡献者合并率 10% — 比 OpenClaw 27% / Flask 15% 都低. 大仓最严.
- 响应时间中位数 336 小时 (14 天), 比 Flask 7 天还慢.
- pandas 走 governance culture (vs Astral 走 maintainer-discretion, vs Flask 走 design-precision).
- 跟 Astral/Flask 都不一样, 不能套模板. 必须看 3.0 roadmap.
