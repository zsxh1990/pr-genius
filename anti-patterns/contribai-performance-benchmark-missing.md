---
type: Anti-Pattern
key: contribai-performance-benchmark-missing
symptom: |
  改了性能敏感代码但没附 benchmark, 维护者无法判断 perf 影响。Close 关键词: "needs benchmark", "perf impact unknown", "please provide before/after"
root_cause: 改了 hot path / 性能敏感代码, 但 PR body 没 before/after 数字。
trigger_keywords:
  - "needs benchmark"
  - "perf impact unknown"
  - "please provide before/after"
  - "show me the benchmark"
  - "we can't merge without perf data"
fix_action: |
  1) 找到项目 benchmark 工具 (pytest-benchmark / go test -bench / wrk)
  2) 跑 before/after 对比
  3) PR body 必含数字 + 命令 + 环境
source_pr: "pandas-dev/pandas ~15% close 是 perf impact, astral-sh/ty ~15%"
prevention: |
  提 PR 前:
  - 改了性能敏感代码? (parser / render / loop)
  - 跑项目 benchmark before/after
  - PR body 附数字 + 命令 + 环境
  - 性能退化 > 5% 直接 reject
learned_at: 2026-07-19
---

## ContribAI 实证 close 数据

- pandas-dev/pandas: ~15% close 是 perf impact
- astral-sh/ty: ~15% close 是 perf benchmark (核心卖点 10x)
- hot path 项目通用: 10-15% close 是 perf

## 反模式特征

1. **改 hot path 没 benchmark** — 改了 parser / loop / render
2. **没 before/after 数字** — "感觉快了" 不算
3. **benchmark 不规范** — 单机 vs 多机 / 冷启 vs 热启 / 大小数据
4. **perf 退化 5%+** — 大型项目直接 reject

## 自检清单

提 PR 前:
- [ ] 改了 parser / render / loop?
- [ ] 跑项目 benchmark before/after
- [ ] PR body 附: 命令 + 环境 + 数字
- [ ] 性能退化 < 5%?

## 关联

- pandas profile: ~15% close 是 perf
- astral-sh/ty profile: "10x faster" 是核心卖点
