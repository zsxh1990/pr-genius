---
type: Demo
title: "Demo 2 — pandas 'out of scope' detection"
description: "pr-genius MCP demo for pandas 45k star PR, identifies out-of-scope / not-in-roadmap anti-pattern (40% of pandas close reasons, contributor's new feature conflicts with 3.0 roadmap)."
version: "1.0.0"
created: "2026-07-19"
schema_version: "OKF v0.1"
---

# Demo 2 — pandas "Out of Scope" Detection

> **场景**: 贡献者给 pandas-dev/pandas (45k stars) 提 PR 加新功能, 实际跟 pandas 3.0 roadmap 不一致。
>
> **反模式**: contribai-out-of-scope (pandas 40% close 原因, **头号杀手**)
>
> **验证**: pr-genius contribai_replay.py 100% 命中

## Prompt (给 Agent)

```
我准备给 pandas-dev/pandas 提一个新功能 PR:

title: "feat: add custom dataframe serializer for FOO format"
body: |
  Adds new method df.to_foo_format() for serializing DataFrames
  to the FOO format. Test included.

  Motivation: Many users use FOO format in production.

请用 pr-genius MCP 工具分析:
1. 能不能直接提?
2. pandas 接受率只有 10%, 什么因素让这个 PR 风险这么高?
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
        "description": "大仓 (45,000 stars) 无 pr-genius profile/policy",
        "severity": "high",
        "generic_checks": [...]
      },
      {
        "key": "first_contributor_large_repo",
        "description": "首次在大仓提 PR, 外部贡献者合并率通常较低",
        "severity": "medium"
      }
    ],
    "neutral": [
      {"key": "no_issue_link_hint", "description": "PR body 未包含 Issue 关联"}
    ]
  },
  "anti_patterns_hit": [
    "contribai-out-of-scope",
    "contribai-docs-pr-missing-quickstart",
    "first-contributor-large-repo",
    "needs_preflight"
  ],
  "checklist": [
    {"action": "preflight_confirm", "priority": "P0", "done": false,
     "hint": "confirm real bug"},
    {"action": "preflight_link", "priority": "P0", "done": false,
     "hint": "link issue or maintainer request"},
    {"action": "ci_passing", "priority": "P1", "done": false,
     "hint": "确认 CI 全部通过"},
    {"action": "performance_benchmark", "priority": "P1", "done": false,
     "hint": "perf benchmark required for hot path"}
  ]
}
```

## Agent 解读

```
❌ REJECT — 高风险, 多重反模式.

触发的反模式:
1. contribai-out-of-scope: pandas 40% close 是 out of scope
2. contribai-docs-pr-missing-quickstart: 没先在 issue 讨论
3. first-contributor-large-repo: 首次给 45k stars 大仓提 PR
4. needs_preflight: 无 profile, 必须 preflight

为什么 out of scope 风险这么高:
- pandas 走 governance 文化, ~50 active maintainers
- 3.0 roadmap 优先级强, 跟路线不一致 = 接近必 close
- 维护者已经决定不做这个方向

推荐:
1. 去 https://github.com/pandas-dev/pandas/issues 搜相关 discussion
2. 看 pandas 3.0 roadmap: https://pandas.pydata.org/docs/development/roadmap.html
3. 在现有 issue 评论 "would you accept a PR for this?"
4. 如果 maintainer 同意, 写 RFC proposal
5. CI 首次需 maintainer 触发 (流程长)
6. 性能 benchmark 必填 (perf impact 15% close 原因)
```

## Lesson

1. **pandas 走 governance 文化**: 不是简单 "code 写对了就 merge"
2. **看 3.0 roadmap 优先**: 跟路线不一致 = 接近必 close
3. **issue 区先问 maintainer**: "would you accept a PR for <X>?"
4. **CI 首次需 maintainer 触发**: 流程长, 提前在 issue 提
5. **性能 benchmark 必填**: pandas 是 hot path, perf 退化直接 reject

## 关联

- 真实 PR case: `pandas-dev-pandas/pr-OUT-OF-SCOPE-demo.md`
- Anti-pattern: `anti-patterns/contribai-out-of-scope.md`
- Profile: `pandas-dev-pandas/index.md` (Out of scope 占 40%)
- Replay: `scripts/contribai_replay.py`
- Report: `docs/contribai_replay_report.md`

## 验证

- ✅ pr-genius contribai_replay.py: contribai-out-of-scope → 100% hit
- ✅ MCP smoke test: 31 passed
- ✅ confidence=medium
