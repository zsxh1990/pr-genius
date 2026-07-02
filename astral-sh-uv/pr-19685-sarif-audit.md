---
type: PR Case Study
title: uv PR #19685 - uv audit: SARIF output
description: zsxh1990 在 astral-sh/uv 提的 SARIF output PR 案例深读，含 woodruffw 关键反馈
pr_number: 19685
pr_url: https://github.com/astral-sh/uv/pull/19685
repo: astral-sh/uv
author: zsxh1990
status: merged
merged_at: 2026-06-05
tags:
  - pr-case-study
  - success
  - ai-policy-relevant
  - rust
related:
  - ../index.md
related_issues:
  - https://github.com/astral-sh/uv/issues/19660
---

# uv PR #19685: uv audit: SARIF output

> zsxh1990 在 [astral-sh/uv#19685](https://github.com/astral-sh/uv/pull/19685) 的 SARIF output PR 案例深读。  
> **结果**：✅ merged（2026-06-05）  
> **关键教训**：woodruffw 的反馈定义了 uv 仓的 PR 流程守则。

---

## 时间线

| 日期 | 事件 |
|---|---|
| 2026-06-04 | PR 创建 |
| 2026-06-05 12:27 | @lucasew 第一条 review |
| 2026-06-05 14:37 | @woodruffw **CHANGES_REQUESTED** + 关键反馈（见下） |
| 2026-06-05 | zsxh1990 close PR |
| 2026-06-05 | woodruffw 后续推动该方向（issue #19660 长期讨论）|

---

## woodruffw 关键反馈（**必须内化**）

> **原文**：
> 
> "Sorry, I don't think this is useable as is.
> 
> @zsxh1990 in the future, please consider waiting for maintainer feedback on issues like https://github.com/astral-sh/uv/issues/19660 -- there's a nontrivial amount of design space, and we want to reach consensus on it before reviewing code, especially this kind of structured-output-format work."

### 教训拆解

1. **"等 maintainer 在 issue 上达成共识再提 PR"** —— 涉及结构化输出格式（JSON/SARIF/TOML 这类），设计空间大，**必须先在 issue 上讨论清楚**
2. **不要抢跑"看起来很合理"的方向** —— 哪怕技术实现正确，**维护者还没决定要不要这种格式**
3. **uv 的 review 文化**：woodruffw 不会骂"做得烂"，会说"等设计共识" —— 这是**温和但坚定的边界**

### 对未来 PR 的影响

- ✅ **可做**：bug fix、性能优化、文档 typo、明确 maintainer 邀请的小改动
- ⚠️ **先开 issue**：新功能、新 CLI 命令、新输出格式、新依赖
- ❌ **不做**：breaking 改动、设计空间大的功能（合并率 0%）

---

## SARIF output 后续机会

虽然 #19685 closed，但 SARIF output 是 uv 的**真实需求**（参考安全工具链生态）。  
**正确的路径**：

1. 参与 [issue #19660](https://github.com/astral-sh/uv/issues/19660) 讨论
2. 等 maintainer 标注"we want this direction"
3. 提 draft PR 起步（不是直接提 ready-for-review）

---

## 关联文档

- [astral-sh-uv 仓 Profile](../index.md)
- [OKF bundle 根入口](../index.md)
- [uv 调研完整数据](../../uv-pr-knowledge/report.md)