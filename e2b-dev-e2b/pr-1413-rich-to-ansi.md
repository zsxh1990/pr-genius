---
type: PR Case Study
title: E2B PR #1413 - replace rich with stdlib ANSI for template logger
description: zsxh1990 在 E2B 提的 rich → stdlib ANSI refactor PR，成功合并
pr_number: 1413
pr_url: https://github.com/e2b-dev/E2B/pull/1413
repo: e2b-dev/E2B
author: zsxh1990
status: merged
merged_at: 2026-06-09
tags:
  - pr-case-study
  - success
  - refactor
  - ponytail-pattern
related:
  - ../index.md
rounds:
  - round: 1
    action: "open PR"
    delta: "未深读 (核心 commit 385971054)"
    response_time_h: 0.05  # 同分钟
    maintainer_action: null
    bot_review:
      - "cla-bot: 'is not on file' (CLA 未签)"
      - "changeset-bot: 'No Changeset found' (changeset 缺)"
      - "chatgpt-codex-connector[bot]: 自动 review"
    blocker: "CLA + changeset 硬性前置"
    timestamp: "2026-06-09T17:23:00Z"
  - round: 2
    action: "amend (CLA + changeset)"
    delta: "签 CLA + 加 changeset 文件"
    response_time_h: 1
    maintainer_action: null
    bot_review: []
    blocker: null
    resolution: "CLA + changeset 满足 → 走完整流程"
    timestamp: "2026-06-09T..."
final_status: merged
merged_at: "2026-06-09"
opened_at: "2026-06-09T..."
next_action: "已合并；与 #1458 对比: refactor + stdlib 减法 走通，新功能加法被拒"
---

# E2B PR #1413: refactor: replace rich with stdlib ANSI for template logger

> zsxh1990 在 [e2b-dev/E2B#1413](https://github.com/e2b-dev/E2B/pull/1413) 的 rich → stdlib ANSI refactor PR。  
> **结果**：✅ merged（2026-06-09）  
> **价值**：Ponytail 守则 "stdlib 有就用" 的成功案例。

---

## PR 内容

**问题**：E2B 模板 logger 用了 `rich` 库，但 rich 太重（带 colors / tables / progress 全套）  
**方案**：换 stdlib `logging` + ANSI escape codes（用 stdlib 写一个 30 行的 ColorFormatter）  
**规模**：未深读（核心 commit `385971054`）

---

## 关键反馈

| 时间 | 评论 |
|---|---|
| 2026-06-09 17:23 | @cla-bot："@zsxh1990 is not on file"（CLA 未签） |
| 2026-06-09 17:23 | @changeset-bot："No Changeset found"（changeset 缺） |
| 2026-06-09 17:24 | @chatgpt-codex-connector[bot] 自动 review |
| (zsxh1990 后续处理 CLA + changeset) | |
| 2026-06-09 | ✅ merged |

**CLA + changeset 是 E2B 合并硬性前置**。

---

## 教训内化

### ✅ 成功模式

1. **Refactor 而非新功能** = E2B 接受率高
2. **stdlib 替换重依赖** = 维护者喜欢（少一个 dep）
3. **改动小且明确** = 不撞主观拒绝
4. **CLA + changeset 都搞** = 走完整流程

### 🎯 Ponytail 守则验证

> "stdlib 有 → 用"

- `rich` 库对 logger 太重 → stdlib `logging` + ANSI 30 行等价
- 减少依赖 = 减少供应链风险 = E2B 维护者认可

---

## 与 #1458（_ERROR_HANDLER）对比

| 维度 | #1413 (refactor) | #1458 (new feature) |
|---|---|---|
| 类型 | 减法 | 加法 |
| 依赖变化 | -1 | 0 |
| 用户痛点 | 真实（rich 重） | 主观（"CLI 错误路由"） |
| maintainer 反馈 | merge | "not adding this feature" |
| 后续可拓展 | ✅ | ❌（方向归档） |

**结论**：E2B 偏好 **减法 + 重构**，回避 **新功能**（除非痛点明显）。

---

## 关联文档

- [E2B 仓 Profile](../index.md)
- [OKF bundle 根入口](../index.md)
- [MEMORY.md Ponytail 内化守则 §4 "stdlib 有就用"](../../../MEMORY.md)