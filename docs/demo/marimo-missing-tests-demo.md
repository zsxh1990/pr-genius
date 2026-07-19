---
type: Demo
title: "Demo 3 — marimo 'missing tests' detection"
description: "pr-genius MCP demo for marimo 13k star PR, identifies missing-tests / please-add-tests anti-pattern (30% of marimo close reasons, contributor changes reactive cell semantics without test coverage)."
version: "1.0.0"
created: "2026-07-19"
schema_version: "OKF v0.1"
---

# Demo 3 — marimo "Missing Tests" Detection

> **场景**: 贡献者给 marimo-team/marimo (13k stars) 提 PR 改 reactive cell 语义, 但测试覆盖不足。
>
> **反模式**: contribai-missing-tests (marimo 30% close 原因)
>
> **验证**: pr-genius contribai_replay.py 100% 命中

## Prompt (给 Agent)

```
我准备给 marimo-team/marimo 提一个新功能 PR:

title: "feat: new reactive cell type for stream data"
body: |
  Adds reactive cell support for streaming data sources.
  Sample notebook included showing usage.

请用 pr-genius MCP 工具分析这个 PR:
1. 这个 PR 的最大风险是什么?
2. 我应该怎么补才能避免 close?
```

## 实际输出 (pr-genius MCP `analyze_pr`)

```json
{
  "tier": "high_risk",
  "signals": {
    "positive": [],
    "negative": [
      {
        "key": "needs_preflight",
        "description": "无 pr-genius profile/policy",
        "severity": "high",
        "generic_checks": [...]
      }
    ],
    "neutral": []
  },
  "anti_patterns_hit": [
    "contribai-missing-tests",
    "needs_preflight"
  ],
  "checklist": [
    {"action": "preflight_confirm", "priority": "P0", "done": false,
     "hint": "confirm real bug"},
    {"action": "preflight_link", "priority": "P0", "done": false,
     "hint": "link issue or maintainer request"},
    {"action": "ci_passing", "priority": "P1", "done": false,
     "hint": "确认 CI 全部通过"},
    {"action": "add_unit_tests", "priority": "P1", "done": false,
     "hint": "补 unit test for reactive cell semantics"},
    {"action": "add_integration_test", "priority": "P1", "done": false,
     "hint": "补 integration test for streaming source"}
  ]
}
```

## Agent 解读

```
❌ REJECT — 风险: missing tests (30% close 原因).

这个 PR 触发了 contribai-missing-tests 反模式:
- marimo 30% close 是 missing tests
- "Sample notebook" 不算 test, 只是 demo
- reactive cell 语义改动必须配完整 unit + integration test

推荐:
1. 补 failing test (复现 streaming source 没 reactive cell 的 bug)
2. 补 passing test (验证 reactive cell 行为正确)
3. 跑 coverage 报告, 新代码必须 >=80% 覆盖
4. reactive semantics 测试: 确保 reactivity 不被新代码破坏
5. notebook 不能代替 unit test
```

## Lesson

1. **PR 必补 test**: failing + passing test 都要
2. **coverage 不降**: 跑 coverage 报告, 新代码必须有覆盖
3. **找项目 test 模式**: pytest / unittest / go test
4. **reactive semantics 测试**: marimo 特有, 确保 reactivity 不破
5. **notebook != test**: sample notebook 只是 demo, 不算 coverage

## 关联

- 真实 PR case: `marimo-team-marimo/pr-MISSING-TESTS-demo.md`
- Anti-pattern: `anti-patterns/contribai-missing-tests.md`
- Profile: `marimo-team-marimo/index.md` (Missing tests 占 30%)
- Replay: `scripts/contribai_replay.py`
- Report: `docs/contribai_replay_report.md`

## 验证

- ✅ pr-genius contribai_replay.py: contribai-missing-tests → 100% hit
- ✅ MCP smoke test: 31 passed
- ✅ confidence=medium
