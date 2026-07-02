---
type: Schema Reference
title: PR Case Study rounds 字段 schema
description: 多轮交互日志（Back-and-Forth）的字段定义
version: 0.1.0
created: 2026-07-02
---

# PR Case Study `rounds` Schema v0.1

> 目标：保留 PR 的"攻防过程"，不只是"最终结果"。
> 适用：每个 `pr-<num>-<slug>.md` 的 YAML frontmatter。

## 字段定义

```yaml
rounds:
  - round: 1                    # 轮次（从 1 开始）
    action: "open PR"           # agent 在本轮做的事
    delta: "+245 / -12"         # 代码变更量
    response_time_h: 6          # 维护者响应耗时（小时）
    maintainer_action: "..."    # 维护者/系统本轮的反馈
    bot_review: ["coderabbit: 2 findings"]
    blocker: null               # 本轮的卡点（如有）
    resolution: null            # 本轮的解决方式（如有）
    commit: "abc1234"           # 关联 commit SHA（短）
    timestamp: "2026-06-12T01:44:00Z"
  - round: 2
    action: "amend (CI fix: lint)"
    blocker: "Lint check failed"
    resolution: "ran cargo fmt --all + amend"
    ...
```

## 字段类型

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `round` | int | ✅ | 从 1 开始 |
| `action` | string | ✅ | open / amend / rebase / squash / close / reopen |
| `delta` | string | ❌ | `+N / -M` |
| `response_time_h` | int/number | ❌ | 距上轮响应小时数；无响应 = null |
| `maintainer_action` | string | ❌ | 评论/状态变化描述 |
| `bot_review` | string[] | ❌ | bot 反馈列表 |
| `blocker` | string | ❌ | 本轮卡点（CI 错/审查意见） |
| `resolution` | string | ❌ | 卡点如何解决 |
| `commit` | string | ❌ | commit SHA 前 7 位 |
| `timestamp` | string | ❌ | ISO-8601 UTC |

## 最终状态字段

```yaml
final_status: merged | closed-merged | closed-not-merged | open | stale
merged_at: "2026-06-09T..."  # 可选
closed_at: "2026-06-18T..."  # 可选
close_reason: "..."           # 可选
```

## Agent 调用方式

```python
def decide_next_action(pr_case_study):
    rounds = pr_case_study["rounds"]
    last = rounds[-1]
    
    if last.get("blocker") and not last.get("resolution"):
        return f"卡点未解：{last['blocker']}，需 fix_action"
    
    if pr_case_study["final_status"] == "merged":
        return "已合并，归档"
    
    if pr_case_study["final_status"] in ("closed-not-merged", "stale"):
        return "已 close，转方向"
    
    # 计算 amortize：rounds 越多越需要冷静
    if len(rounds) >= 5:
        return "5+ 轮未合，rethink 方向"
    
    return "等待 maintainer 响应"
```

## 版本

- v0.1.0 (2026-07-02)：初版（基于 uv/honcho/e2b/fastmcp 真实 PR 链路验证）