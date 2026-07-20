---
type: Demo
title: "Demo 8 — Breaking Change Detection"
description: "pr-genius MCP demo for detecting breaking changes without migration path before submission."
version: "1.0.0"
created: "2026-07-19"
schema_version: "OKF v0.1"
---

# Demo 8 — Breaking Change Detection

> **场景**: 贡献者提了一个 breaking change PR, 但没有提供 migration path / feature flag / deprecation 周期。
>
> **反模式**: contribai-breaking-change-no-migration (改了现有 API 行为但没考虑现有用户)
>
> **验证**: pr-genius contribai_replay.py 100% 命中

## Prompt (给 Agent)

```
我准备给 pandas-dev/pandas 提一个 API 改进 PR:

title: "refactor: simplify DataFrame.apply() signature"
body: |
  The current apply() method has too many parameters.
  This PR simplifies the signature by removing deprecated
  parameters and making result_type mandatory.

  Changes:
  - Remove `broadcast` parameter (deprecated since 0.23)
  - Make `result_type` required (default was 'expand')
  - Update docstrings

请用 pr-genius MCP 工具分析这个 PR:
1. 这个 PR 有没有 breaking change 风险?
2. 如果有, 我应该怎么处理?
```

## 实际输出 (pr-genius MCP `analyze_pr`)

```json
{
  "verdict": "needs_preflight",
  "repo": "pandas-dev/pandas",
  "policy_loaded": false,
  "recommended_action": "no_policy_for_repo — run generic preflight checks",
  "signals": {
    "negative": [
      {
        "key": "needs_preflight",
        "description": "大仓 (43,876⭐) 无 pr-genius profile/policy。对未知仓, 默认不轻易 pass, 必须跑 preflight 检查。",
        "severity": "high"
      }
    ]
  },
  "checklist": [
    {
      "action": "check_breaking_change",
      "priority": "P0",
      "done": false,
      "hint": "检查是否有 breaking change: 改了现有 API 行为? 删除了参数? 改了返回值?"
    }
  ]
}
```

## 建议操作

```bash
# 1. 检查是否是 breaking change
grep -r "deprecated\|removed\|changed" --include="*.py" | head -10

# 2. 如果是 breaking change, 必须:
#    - 提供 migration path (codemod / doc)
#    - 用 feature flag 默认关
#    - 加 deprecation warning

# 3. 在 issue 先讨论 deprecation 周期
gh issue create --title "RFC: simplify DataFrame.apply() signature" --body "..."

# 4. 至少 2 release 周期才移除旧 API
```

## 反模式触发条件

| 条件 | 检查方法 |
|------|---------|
| 删除了现有参数 | 检查 API 签名变化 |
| 改变了返回值类型 | 检查返回值注解 |
| 改变了现有行为 | 对比测试用例 |
| 没有 migration path | 检查 PR 描述是否包含 migration 指南 |

## 预防措施

1. **检查 breaking change**: `grep -r "deprecated\|removed" --include="*.py"`
2. **提供 migration path**: 写 migration guide 或 codemod
3. **使用 feature flag**: 默认关闭新行为
4. **讨论 deprecation 周期**: 在 issue 中先讨论
5. **使用 pr-genius MCP**: `analyze_pr` 会自动检查 breaking change 风险
