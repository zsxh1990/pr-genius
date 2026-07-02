---
type: PR Case Study
title: future-agi PR #778 - span list view without project_id
description: zsxh1990 在 future-agi 提的 span list PR，bot review 已修，克莱恩亲自 check-in
pr_number: 778
pr_url: https://github.com/future-agi/future-agi/pull/778
repo: future-agi/future-agi
author: zsxh1990
status: open
opened_at: 2026-06-04
last_activity: 2026-06-28
tags:
  - pr-case-study
  - open
  - high-priority
  - ikalus-checkin
  - clickhouse
related:
  - ../index.md
related_issues:
  - https://github.com/future-agi/future-agi/issues/775
---

# future-agi PR #778: feat: enable span list view without project_id (fix #775)

> zsxh1990 在 [future-agi/future-agi#778](https://github.com/future-agi/future-agi/pull/778) 的 span list PR。  
> **状态**：🟢 open（27 天）  
> **优先级**：🔴 **最高**（克莱恩 2026-06-28 14:25 GMT+8 亲自发 friendly check-in）。

---

## PR 内容

**问题**：[#775](https://github.com/future-agi/future-agi/issues/775) - span 列表必须传 project_id，导致没有 project 的 span 无法查看  
**方案**：list_spans_observe 允许 project_id=None，按 NULL project_id 查 ClickHouse  
**规模**：+2 / -2 / 1 file（极小）

---

## 关键反馈时间线

| 时间 | 事件 | 评论 |
|---|---|---|
| 2026-06-04 10:59 | entelligence AI v1 | "project_id 现在必填；缺则抛异常" |
| 2026-06-08 16:31 | zsxh1990 | "Will push fix for the NULL project_id EndUser lookup issue" |
| 2026-06-08 16:38 | entelligence AI v2 | （细节未深读） |
| 2026-06-28 07:25 | **@Ikalus1988（克莱恩主号）** | **friendly check-in 全文**（见下） |

---

## 克莱恩的 check-in（关键信号）

> "Hi team — friendly check-in on this one 🙂  
> 
> It's been a couple weeks since the PR was opened. The bot review flagged two items (project=None NameError, NULL project_id EndUser lookup) which I've addressed.  
> 
> Happy to make any adjustments if there's feedback from the human review."

**信号强度**：
1. ✅ 克莱恩用主号（Ikalus1988）发 = 主动关联
2. ✅ "I've addressed" 而非 "will address" = 已修
3. ✅ "any adjustments" = 谦虚 + 主动姿态
4. ⚠️ 但 zsxh1990 没用主号发 = 仍是小号在跑

---

## 下一步

- ⚠️ **等 maintainer 真实 review**
- ⏰ 7/5 前无回应 → zsxh1990 再 bump 一次
- ⏰ 7/12 前无回应 → 主动 close

---

## 关联文档

- [future-agi 仓 Profile](../index.md)
- [MEMORY.md Ikalus1988 ↔ zsxh1990 隔离](../../../MEMORY.md)