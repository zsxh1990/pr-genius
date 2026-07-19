---
type: Anti-Pattern
key: contribai-missing-tests
symptom: |
  PR 改了代码但没补 / 没改测试。Close 关键词: "needs tests", "missing tests", "test coverage", "please add tests"
root_cause: 只想改代码, 不补测试; 或不知道该补什么测试。
trigger_keywords:
  - "needs tests"
  - "missing tests"
  - "test coverage"
  - "please add tests"
  - "without tests this can't be merged"
fix_action: |
  1) 找到现有 test 模式 (unit / integration / e2e)
  2) 写 failing test 先复现 bug
  3) 改代码让 test 通过
  4) coverage 报告不能降
source_pr: "ContribAI 14 closed PR 中 ~20% 提到 missing tests"
prevention: |
  提 PR 前:
  - 找到项目 test 模式
  - 至少补 1 个 failing test + 1 个 passing test
  - 跑 coverage 报告不降
learned_at: 2026-07-19
---

## ContribAI 实证 close 数据

- pandas-dev/pandas: ~30% close 提到 missing tests
- HolmesGPT/holmesgpt: ~30% (kubernetes 兼容性 test)
- marimo-team/marimo: ~30%
- 通用: 15-30% close 提 missing tests

## 反模式特征

1. **只改 src 不改 test** — 一半 PR 都有这问题
2. **没复现 test** — 改完代码, 没证明之前是坏的
3. **没回归 test** — 修了一个 bug, 别的功能可能挂
4. **coverage 降** — 新代码没 test 覆盖

## 自检清单

提 PR 前:
- [ ] 找到项目 test 模式 (pytest / unittest / go test)
- [ ] 写 failing test 复现 bug
- [ ] 跑 coverage, 不降
- [ ] integration test 覆盖新功能

## 关联

- honcho: `anti-patterns/honcho-default-db-module-trap.md`
