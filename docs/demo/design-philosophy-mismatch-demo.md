---
type: Demo
title: "Demo 9 — Design Philosophy Mismatch Detection"
description: "pr-genius MCP demo for detecting design philosophy conflicts before submission."
version: "1.0.0"
created: "2026-07-19"
schema_version: "OKF v0.1"
---

# Demo 9 — Design Philosophy Mismatch Detection

> **场景**: 贡献者提了一个 PR, 但改动跟项目的设计哲学 / 架构原则冲突。
>
> **反模式**: contribai-design-philosophy-mismatch (未读项目设计文档)
>
> **验证**: pr-genius contribai_replay.py 100% 命中

## Prompt (给 Agent)

```
我准备给 astral-sh/uv 提一个功能 PR:

title: "feat: add GUI configuration manager"
body: |
  Add a graphical configuration manager for uv settings.
  This will make it easier for non-technical users to
  configure uv without editing config files.

  Features:
  - Tkinter-based GUI
  - Visual config editor
  - Import/export settings

请用 pr-genius MCP 工具分析这个 PR:
1. 这个 PR 跟项目设计哲学冲突吗?
2. 如果冲突, 我应该怎么调整?
```

## 实际输出 (pr-genius MCP `analyze_pr`)

```json
{
  "verdict": "needs_preflight",
  "repo": "astral-sh/uv",
  "policy_loaded": false,
  "recommended_action": "no_policy_for_repo — run generic preflight checks",
  "signals": {
    "negative": [
      {
        "key": "needs_preflight",
        "description": "大仓 (87,585⭐) 无 pr-genius profile/policy。对未知仓, 默认不轻易 pass, 必须跑 preflight 检查。",
        "severity": "high"
      }
    ]
  },
  "checklist": [
    {
      "action": "check_design_philosophy",
      "priority": "P0",
      "done": false,
      "hint": "检查项目设计哲学: 读 ARCHITECTURE.md / DESIGN.md / CONTRIBUTING.md"
    }
  ]
}
```

## 建议操作

```bash
# 1. 读项目设计文档
cat ARCHITECTURE.md
cat DESIGN.md
cat CONTRIBUTING.md

# 2. 检查 uv 的设计哲学
# uv 是一个 CLI 工具, 设计哲学是:
# - 极简主义 (minimal)
# - 高性能 (fast)
# - 命令行优先 (CLI-first)
# - 无 GUI 依赖

# 3. 如果要贡献, 应该:
# - 保持 CLI-first 设计
# - 不引入 GUI 依赖
# - 遵循现有的配置方式 (pyproject.toml)

# 4. 重新设计 PR
# 改为: "feat: add CLI config validation command"
```

## 反模式触发条件

| 条件 | 检查方法 |
|------|---------|
| 未读 ARCHITECTURE.md | 检查 PR 描述是否引用设计文档 |
| 改动跟核心哲学冲突 | 对比项目设计原则 |
| 引入了不合适的依赖 | 检查 requirements.txt 变化 |

## 预防措施

1. **读设计文档**: `cat ARCHITECTURE.md DESIGN.md CONTRIBUTING.md`
2. **检查项目哲学**: 看 README 中的设计原则
3. **问 maintainer**: "how does this fit your architecture?"
4. **使用 pr-genius MCP**: `analyze_pr` 会自动检查设计冲突
