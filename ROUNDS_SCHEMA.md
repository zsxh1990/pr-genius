---
type: Schema Reference
title: PR Case Study rounds + delta + close_decision schema
description: 多轮交互日志（Back-and-Forth）的字段定义 + delta 对象化 + close_decision case-level 字段
version: 0.2.0
created: 2026-07-02
updated: 2026-07-02
---

# PR Case Study Schema v0.2

> 目标：保留 PR 的"攻防过程"，不只是"最终结果"。
> 适用：每个 `pr-<num>-<slug>.md` 的 YAML frontmatter。
>
> v0.2.0 升级基于 2 个真实 PR（honcho #801 + qdrant #143）的样本验证。

## 字段定义（rounds 数组）

```yaml
rounds:
  - round: 1                    # 轮次（从 1 开始）
    action: open                # 见 action 枚举
    delta:                       # 见 delta 对象
      kind: code_change
      value: "+76 / -0 / 4 files"
    response_time_h: 6
    maintainer_action: "..."
    bot_review: ["coderabbit: 2 findings"]
    blocker: null
    resolution: null
    commit: "abc1234"
    timestamp: "2026-06-12T01:44:00Z"
```

## action 枚举（v0.2.0 新增）

```yaml
action:
  enum:
    - open           # 提 PR
    - amend          # 修代码（amend commit）
    - bot_review     # bot 自动 review（本轮主事件）
    - human_review   # 人类 maintainer review（本轮主事件）
    - check_in       # friendly ping / 等回应
    - bump           # 二次 check-in（区别于 check_in）
    - close          # 主动 close
    - merge          # 合并
    - decision       # 决策点（如 stale 后决定 close-or-keep）
```

**最少 9 个值够了，不扩。**

## delta 对象（v0.2.0 新增）

```yaml
delta:
  kind: code_change | no_code_change | unknown
  value: "+76 / -0 / 4 files" | null
```

**3 种 kind 区分**：

| kind | value 示例 | 含义 |
|---|---|---|
| `code_change` | `"+76 / -0 / 4 files"` | 有真实 PR diff |
| `no_code_change` | `null` | check-in / bump / close 等无代码变更动作 |
| `unknown` | `null` | 暂未测量（最常见于历史 case 回填） |

**核心修复**：原来 `delta: null` 含义模糊（"没改" vs "没测"）—— 现在 kind 字段区分。

## close_decision case-level 字段（v0.2.0 新增）

```yaml
close_decision:
  status: pending | close | keep_open | merged | superseded
  reason: "26d stale, two check-ins, no maintainer response"
  decided_at: null  # ISO-8601 UTC，决策未定时 null
  actor: zsxh1990
```

**5 种 status**：

| status | 含义 |
|---|---|
| `pending` | 决策待定（仍 open） |
| `close` | 决定 close |
| `keep_open` | 决定保持 open（即使 stale） |
| `merged` | 已 merge（close_decision 自然结束） |
| `superseded` | 被新 PR 替代 |

## 最终状态字段

```yaml
final_status: merged | closed-merged | closed-not-merged | open | open-stale
opened_at: "..."
merged_at: "..."  # 可选
closed_at: "..."  # 可选
```

## 暂不 schema 化（克莱恩 v0.2.0 拍板）

- ❌ `stale_days`：留 case-level 普通字段
- ❌ `bot_review: []` vs `null`：不管
- ❌ `response_time_h` 语义歧义：不管
- ❌ `human_in_loop_note`：不加

## 版本

- v0.2.0 (2026-07-02)：action 枚举 + delta 对象 + close_decision case-level（基于 honcho/qdrant 2 真实样本验证）
- v0.1.0 (2026-07-02)：初版（round 字段定义）