---
type: Demo
title: "Demo 4 — astral-sh/ty 'needs RFC' detection"
description: "pr-genius MCP demo for astral-sh/ty 12k star PR, identifies needs-RFC / please-discuss-design anti-pattern (25% of ty close reasons, contributor changes type system semantics without RFC first). Klein P0: astral cannot be uniformly friendly, ty is counter-example."
version: "1.0.0"
created: "2026-07-19"
schema_version: "OKF v0.1"
---

# Demo 4 — astral-sh/ty "Needs RFC" Detection

> **场景**: 贡献者给 astral-sh/ty (12k stars, beta 阶段) 提 PR 改 type system 语义 (如 conditional types narrowing), 但没先开 RFC.
>
> **反模式**: contribai-needs-rfc-first (ty 25% close 原因)
>
> **关键警告**: 克莱恩 P0 战略评估强调 — **astral 不能整体打 friendly** (uv / ruff / ty 各自政策不同). ty 是反例: beta 阶段 != 一切开放, type system 改动必须先 RFC.
>
> **验证**: pr-genius contribai_replay.py 100% 命中

## Prompt (给 Agent)

```
我准备给 astral-sh/ty 提一个新功能 PR:

title: "feat: add new type narrowing for conditional types"
body: |
  Adds new type narrowing for conditional types. Changes
  core type semantics to handle more complex cases.

  Test included.

请用 pr-genius MCP 工具分析:
1. 我是第一次给 ty 提 PR, 能直接提吗?
2. type system 改动有什么特殊风险?
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
    "contribai-needs-rfc-first",
    "needs_preflight"
  ],
  "checklist": [
    {"action": "preflight_confirm", "priority": "P0", "done": false,
     "hint": "confirm real bug"},
    {"action": "preflight_link", "priority": "P0", "done": false,
     "hint": "link issue or maintainer request"},
    {"action": "ci_passing", "priority": "P1", "done": false,
     "hint": "确认 CI 全部通过"},
    {"action": "add_rfc_proposal", "priority": "P1", "done": false,
     "hint": "先开 RFC issue 讨论 type system 设计"},
    {"action": "add_performance_benchmark", "priority": "P1", "done": false,
     "hint": "perf benchmark before/after required"}
  ]
}
```

## Agent 解读

```
❌ REJECT — 高风险, type system 改动需要 RFC 流程.

触发的反模式:
1. contribai-needs-rfc-first: ty 25% close 是 needs RFC
2. needs_preflight: 无 profile, 必须 preflight

为什么 RFC 必填:
- type system 是 ty 的核心 (10x faster than mypy 是卖点)
- 语义改动不可逆 (一旦 merge 变成 public API)
- beta 阶段不等于一切开放 — 反馈开放 != 语义改动开放

推荐:
1. 去 https://github.com/astral-sh/ty/issues 开 "RFC: type narrowing for conditional types" issue
2. 在 issue 详细说明:
   - 为什么需要这个改动
   - 跟 mypy / pyright 的行为差异
   - 性能影响 (before/after benchmark)
   - 兼容性影响
3. 等 maintainer 同意后再提 PR
4. PR body 引用 RFC issue 链接
5. 提供 performance benchmark (10x 是核心卖点, 退化 reject)
```

## Lesson

1. **type system 改动需 RFC**: ty 是 type checker, semantics 是核心
2. **beta 阶段 != 一切开放**: beta 反馈开放 != API/语义改动开放
3. **大改先开 issue**: type system 改动先在 issue 讨论, 不要直接 PR
4. **performance benchmark 必填**: "10x faster" 是核心卖点, perf 退化 reject
5. **astral 不能整体打 friendly**: uv / ruff / ty 各自政策不同

## 关联

- 真实 PR case: `astral-sh-ty/pr-NEEDS-RFC-demo.md`
- Anti-pattern: `anti-patterns/contribai-needs-rfc-first.md`
- Profile: `astral-sh-ty/index.md` (Needs RFC 占 25%, beta 阶段 != 一切开放)
- Replay: `scripts/contribai_replay.py`
- Report: `docs/contribai_replay_report.md`

## 验证

- ✅ pr-genius contribai_replay.py: contribai-needs-rfc-first → 100% hit
- ✅ MCP smoke test: 31 passed
- ✅ confidence=medium
- ✅ 符合克莱恩 P0 战略评估 "astral 不能整体打 friendly" 原则
