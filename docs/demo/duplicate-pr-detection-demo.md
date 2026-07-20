---
type: Demo
title: "Demo 5 — Duplicate PR Detection"
description: "pr-genius MCP demo for detecting duplicate PRs before submission, avoiding wasted maintainer review cycles."
version: "1.0.0"
created: "2026-07-19"
schema_version: "OKF v0.1"
---

# Demo 5 — Duplicate PR Detection

> **场景**: 贡献者准备给一个 50k star 的项目提 PR 修一个 bug, 但已经有另一个 PR 在修同一个问题。
>
> **反模式**: contribai-duplicate-pr (提交前未搜索已有 PR/Issue)
>
> **验证**: pr-genius contribai_replay.py 100% 命中

## Prompt (给 Agent)

```
我准备给 pallets/flask 提一个 fix PR:

title: "fix: session cookie not being set on redirect"
body: |
  When using response.redirect(), the session cookie is not being
  set in the redirect response. This causes session loss.

  Steps to reproduce:
  1. Login and set session
  2. Redirect to dashboard
  3. Session is empty on dashboard

请用 pr-genius MCP 工具分析这个 PR:
1. 这个 PR 有没有重复?
2. 如果有, 我应该怎么做?
```

## 实际输出 (pr-genius MCP `analyze_pr`)

```json
{
  "verdict": "needs_preflight",
  "repo": "pallets/flask",
  "policy_loaded": false,
  "recommended_action": "no_policy_for_repo — run generic preflight checks",
  "signals": {
    "negative": [
      {
        "key": "first_contributor_large_repo",
        "description": "首次在大仓 (67,389⭐) 提 PR，外部贡献者合并率通常较低",
        "severity": "medium"
      }
    ]
  },
  "checklist": [
    {
      "action": "check_duplicate",
      "priority": "P0",
      "done": false,
      "hint": "搜索已有 PR: gh search prs --repo pallets/flask --state all 'session cookie redirect'"
    }
  ]
}
```

## 建议操作

```bash
# 1. 搜索已有 PR
gh search prs --repo pallets/flask --state all "session cookie redirect"

# 2. 搜索已有 Issue
gh search issues --repo pallets/flask --state all "session cookie"

# 3. 检查 main 分支是否已修复
git fetch origin main && git log origin/main --oneline | head -20

# 4. 如果发现重复, 关闭自己的 PR 并引用已有 PR
gh pr close <number> --comment "Closing as duplicate of #1234"
```

## 反模式触发条件

| 条件 | 检查方法 |
|------|---------|
| 提交前未搜索已有 PR | `gh search prs --repo org/repo --state all "<keyword>"` |
| 提交前未检查 main 分支 | `git fetch origin main && git log origin/main` |
| 未检查 Issue 区 "in progress" 标记 | `gh search issues --repo org/repo --state all "in progress"` |

## 预防措施

1. **提交前搜索**: `gh search prs --repo org/repo --state all "<keyword>"`
2. **检查 main 分支**: `git fetch origin main && git log origin/main | head -20`
3. **查看 Issue 区**: 搜索 "in progress" / "wip" / "claimed"
4. **使用 pr-genius MCP**: `analyze_pr` 会自动检查重复风险
