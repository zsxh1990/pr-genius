---
type: Demo
title: "Demo 10 — First-Time Large Repo Contributor Detection"
description: "pr-genius MCP demo for first-time contributors to large repositories, addressing trust deficit."
version: "1.0.0"
created: "2026-07-19"
schema_version: "OKF v0.1"
---

# Demo 10 — First-Time Large Repo Contributor Detection

> **场景**: 首次贡献者向 ≥10k star 的大仓提 PR, 但没有建立信任, 维护者默认怀疑。
>
> **反模式**: contribai-first-time-large-repo (信用未建立)
>
> **验证**: pr-genius contribai_replay.py 100% 命中

## Prompt (给 Agent)

```
我准备给 kubernetes/kubernetes 提一个 fix PR:

title: "fix: pod scheduling race condition"
body: |
  There's a race condition in the pod scheduler when
  multiple nodes are available. The scheduler sometimes
  assigns pods to the wrong node.

  This PR fixes the mutex locking in the scheduler.

请用 pr-genius MCP 工具分析这个 PR:
1. 我是第一次给 Kubernetes 提 PR, 有什么风险?
2. 我应该怎么建立信任?
```

## 实际输出 (pr-genius MCP `analyze_pr`)

```json
{
  "verdict": "needs_preflight",
  "repo": "kubernetes/kubernetes",
  "policy_loaded": false,
  "recommended_action": "no_policy_for_repo — run generic preflight checks",
  "signals": {
    "negative": [
      {
        "key": "first_contributor_large_repo",
        "description": "首次在大仓 (123,781⭐) 提 PR，外部贡献者合并率通常较低",
        "severity": "medium"
      },
      {
        "key": "needs_preflight",
        "description": "大仓 (123,781⭐) 无 pr-genius profile/policy。对未知仓, 默认不轻易 pass, 必须跑 preflight 检查。",
        "severity": "high"
      }
    ]
  },
  "checklist": [
    {
      "action": "build_trust",
      "priority": "P1",
      "done": false,
      "hint": "先在 Issue 中参与讨论、回复评论，建立维护者信任后再提 PR"
    }
  ]
}
```

## 建议操作

```bash
# 1. 先在 issue 区建立信任 (回复 5+ 个其他 issue)
gh search issues --repo kubernetes/kubernetes --state open --limit 10

# 2. 提简单 fix (typo / docs 补 example) 建立信用
# 3. 再提复杂 PR

# 4. 如果一定要提复杂 PR, 必须:
#    - 在 issue 先讨论方案
#    - 提供详细的设计文档
#    - 有测试用例
#    - 有 migration plan
```

## 反模式触发条件

| 条件 | 检查方法 |
|------|---------|
| 首次贡献者 | 检查 author_association == "NONE" |
| 仓库 ≥10k stars | 检查 star_count |
| 没有历史贡献 | 检查该用户的 merged PR 数量 |

## 预防措施

1. **先建立信任**: 在 issue 区参与 2-4 周
2. **提简单 fix**: 先提 typo / docs 补 example
3. **在 issue 讨论**: 先开 issue 讨论方案
4. **使用 pr-genius MCP**: `analyze_pr` 会自动检查首次贡献者风险
