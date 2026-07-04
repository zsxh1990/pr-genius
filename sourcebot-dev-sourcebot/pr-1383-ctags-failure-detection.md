---
type: PR Case Study
title: sourcebot PR #1383 - detect and surface ctags indexing failures
description: zsxh1990 在 sourcebot 提的 ctags 失败检测 PR，CodeRabbit 已审
pr_number: 1383
pr_url: https://github.com/sourcebot-dev/sourcebot/pull/1383
repo: sourcebot-dev/sourcebot
author: zsxh1990
status: open
opened_at: 2026-06-28
last_activity: 2026-06-28
tags:
  - pr-case-study
  - open
  - ctags
  - observability
  - small-pr
related:
  - ../index.md
rounds:
  - round: 1
    action: open
    delta:
      kind: code_change
      value: "+60 / -6 / 2 files"  # 极小 PR - OpenClaw §6.1 #2 ideal
    response_time_h: 0.5
    maintainer_action: null
    bot_review:
      - "coderabbit: 1 actionable finding (未修)"
    timestamp: "2026-06-28T09:23:00Z"
close_decision:
  status: pending
  reason: "auto-migrated from v0.1; pending close decision by zsxh1990"
  decided_at: null
  actor: zsxh1990
final_status: open
opened_at: "2026-06-28T09:23:00Z"
last_activity: "2026-06-28T09:23:00Z"
next_action: "修 CodeRabbit 1 finding，等 maintainer review"
---

# sourcebot PR #1383: feat: detect and surface ctags indexing failures

> zsxh1990 在 [sourcebot-dev/sourcebot#1383](https://github.com/sourcebot-dev/sourcebot/pull/1383) 的 ctags 失败检测 PR。  
> **状态**：🟢 open（3 天）  
> **特征**：极小 PR（+60/-6，2 files）= 理想 size（学 OpenClaw §6.1 #2）。

---

## PR 内容

**问题**：ctags 索引失败时静默（用户看不到，搜索结果空）  
**方案**：捕获 ctags 失败 → 暴露到连接状态 UI  
**规模**：+60 / -6 / 2 files

---

## CodeRabbit 反馈

- 1 actionable finding（细节未读）
- zsxh1990 未提 amend

---

## 关联文档

- [sourcebot 仓 Profile](../index.md)
- [OpenClaw 守则 §6.1 #2 XS/S size](../../../MEMORY.md)