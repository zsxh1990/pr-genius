---
type: Demo
title: "Demo 6 — Archived Repository Detection"
description: "pr-genius MCP demo for detecting archived repositories before submitting PR, avoiding wasted effort."
version: "1.0.0"
created: "2026-07-19"
schema_version: "OKF v0.1"
---

# Demo 6 — Archived Repository Detection

> **场景**: 贡献者准备给一个项目提 PR, 但该项目已被维护者标记为 archived (不再维护)。
>
> **反模式**: contribai-archived-repo (提 PR 前没查 repo 状态)
>
> **验证**: pr-genius contribai_replay.py 100% 命中

## Prompt (给 Agent)

```
我准备给 old-project/legacy-lib 提一个 fix PR:

title: "fix: memory leak in connection pool"
body: |
  The connection pool is not properly closing connections,
  causing memory leaks in long-running processes.

请用 pr-genius MCP 工具分析这个 PR:
1. 这个仓库还能提 PR 吗?
2. 如果不能, 我应该怎么做?
```

## 实际输出 (pr-genius MCP `analyze_pr`)

```json
{
  "verdict": "needs_preflight",
  "repo": "old-project/legacy-lib",
  "policy_loaded": false,
  "recommended_action": "no_policy_for_repo — run generic preflight checks",
  "signals": {
    "negative": [
      {
        "key": "needs_preflight",
        "description": "大仓 (未知⭐) 无 pr-genius profile/policy。对未知仓, 默认不轻易 pass, 必须跑 preflight 检查。",
        "severity": "high"
      }
    ]
  },
  "checklist": [
    {
      "action": "check_repo_status",
      "priority": "P0",
      "done": false,
      "hint": "检查仓库状态: gh repo view old-project/legacy-lib --json isArchived,isDisabled"
    }
  ]
}
```

## 建议操作

```bash
# 1. 检查仓库状态
gh repo view old-project/legacy-lib --json isArchived,isDisabled,isFork

# 2. 如果 archived, 查找 successor
gh repo view old-project/legacy-lib --json description,homepageUrl

# 3. 搜索 successor 项目
gh search repos "legacy-lib" --sort=stars --limit=5

# 4. 转向 successor 项目提 PR
```

## 反模式触发条件

| 条件 | 检查方法 |
|------|---------|
| 仓库已 archived | `gh repo view org/repo --json isArchived` |
| 仓库已 disabled | `gh repo view org/repo --json isDisabled` |
| 维护者不再活跃 | 检查最近 commit 时间 |

## 预防措施

1. **提交前检查**: `gh repo view org/repo --json isArchived,isDisabled`
2. **查看最近活动**: `gh api repos/org/repo/commits?per_page=1 --jq '.[0].commit.author.date'`
3. **搜索 successor**: 如果 archived, 搜索替代项目
4. **使用 pr-genius MCP**: `analyze_pr` 会自动检查仓库状态
