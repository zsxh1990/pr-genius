---
type: Risk Reference
title: ag2ai/ag2 风险决策
description: 小 PR 探路评估（轻量记录，不展开长报告）
version: 0.1.0
created: 2026-07-03
---

# ag2ai/ag2 — Skip for now

## Decision

**skip-for-now**

## Reason

- ❌ 0 个 `good first issue` 标签
- ❌ 0 个 `help wanted` 标签
- ❌ 22 个 open issue 全是 `enhancement` / `bug`，没 docs/typo/error-message 类小型 issue
- ⚠️ docs typo / CI flaky / dep pin 类改动要读全仓代码找 = 高 token 成本

## Signal

- ✅ 最近 20 closed PR merge rate 65%（13 merged / 7 closed-not-merged）
- ✅ 最近 merged PR 简短 chore 类（如 `#3041 chore: remove classic CLI`）
- ⚠️ 但 merge 主体大概率是 maintainer 自己或熟人贡献，**不是新人友好型**

## 2026-07-04 重新侦察 (克莱恩 20min gate)

- ❌ docs label 7 个 issue 全是 feat(beta) 巨型 PR (middleware/network/prometheus)，不是 typo 修复
- ❌ 22 open, 5 真 issue 全是 enhancement/bug/agent behavior 红海
- ❌ good first issue / help wanted = 0 (再次确认)
- ⚠️ 6 月经历 `ag2 → autogen → ag2-classic` 大改名一波 (#3023 / #3047)，typo 窗口已清
- ⚠️ 最近 6 closed PR 100% codecov bot 评论 (无人类文字 review)
- ✅ vibe AI-friendly 但**不在 typo 修复期**

结论: SKIP 维持。**不写新 gate**，等改名降温 + maintainer 切回 bug 修复型节奏

## Revisit When

- good-first issue 标签出现
- 看到具体 typo / docs 拼错 / CI flaky / dep pin 错位 任何一项
- rename 风波结束 (估计 7/15 后) + 新 typo 自然积累

## 不展开依据（克莱恩拍板"别写长报告"）

不写"为什么 merge rate 65% 低" — 这是细节，不是判断主线。
不写"docs.ag2.ai CONTRIBUTING 内容全文" — 没影响决策。
不写"具体 5 个 open issue 列表" — 克莱恩禁了 enhancement，不进。

## 路径

仓 dir: `ag2ai-ag2/` (未建 profile，因为 skip)

如果未来 revisit，建 `ag2ai-ag2/index.md` (Repo Profile) + `pr-<num>-<slug>.md` (PR Case Study)。
