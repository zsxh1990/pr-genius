---
type: Index
title: MisakaNet Lessons — Real Failures + Recoveries
description: pr-genius 仓下的 misakanet-style lessons (75+ score threshold)
version: 0.2.0
created: 2026-07-03
updated: 2026-07-03
---

# misakanet-50/ — Lessons Index

> 克莱恩拍板 (2026-07-03 00:14): 装 agent-reach + 抓 50 条 misakanet lesson。
> 克莱恩纠正 (2026-07-03 00:46): **lesson 必须是真实故障 / fail 恢复**，不是新闻报道。
>
> **Lesson 评分门槛**: 75+/100（per `https://github.com/Ikalus1988/MisakaNet/blob/main/lessons/LESSON_QUALITY_SCORING.md`）

## 已有 lesson（10 条）

### 真实故障型（lesson-06 ~ lesson-10）✅ 符合克莱恩标准

| # | 标题 | 评分 | 真实事件源 |
|---|---|---|---|
| 06 | Git push 撞 ikalus PAT 403 | 85 | pr-genius commit `291c4b7` (2026-07-02 23:36 GMT+8) |
| 07 | uv venv --seed 替代缺 pip 的 venv | 90 | agent-reach 安装 (2026-07-03 00:25 GMT+8) |
| 08 | pip install HTTPS_TIMEOUT 撞代理 | 85 | agent-reach 安装 (2026-07-03 00:30 GMT+8) |
| 09 | V2EX API /api/topics/show.json 不稳 | 85 | lesson 抓取 (2026-07-03 00:42 GMT+8) |
| 10 | agent-reach doctor 4/15 channel baseline | 80 | 安装完成 (2026-07-03 00:32 GMT+8) |

### ⚠️ 新闻 / 观点报道型（lesson-01 ~ lesson-05）— 克莱恩 00:46 标记不符合标准

| # | 标题 | 评分 | 备注 |
|---|---|---|---|
| 01 | Vibe Coding Team Out of Control | 95 | 通用团队管理观点 — 保留作背景资料 |
| 02 | AI Code Review: When to Skip vs Read | 95 | 行业哲学讨论 — 保留作背景资料 |
| 03 | AI Monthly Cost Baseline | 90 | 数据调查 — 保留作背景资料 |
| 04 | AI API Relay Risks | 85 | 安全分析 — 保留作背景资料 |
| 05 | vless+xhttp+reality Blocked | 90 | 网络分析 — 保留作背景资料 |

**Lesson 1-5 状态**: 保留（不删除），但**不推送**到 misakanet 主仓。这些更适合作为个人 RAG 资料或新闻总结类内容，不是 misakanet 风格的 "故障+恢复" lesson。

## 主题覆盖

| Domain | 真实故障 lesson | 总 lesson |
|---|---|---|
| devops (CI/git/python env) | 06, 07, 08 (3) | 3 |
| scraping (data fetch) | 09 (1) | 1 |
| tooling (agent setup) | 10 (1) | 1 |
| agent-collaboration | — | 2 (01, 02) |
| operations | — | 1 (03) |
| security | — | 1 (04) |
| networking | — | 1 (05) |

## 与 misakanet 主仓的关系

- **lesson-01 ~ lesson-10 全部在 pr-genius 仓**：`research/big-repo-pr-knowledge/misakanet-50/`
- **未推送到 misakanet 主仓**（克莱恩 2026-07-03 删除了 MisakaNet 主仓禁区规则，但推送决策权仍归克莱恩）
- **lesson 标准**: 严格遵循 `LESSON_QUALITY_SCORING.md` 75+ 门槛 + 真实故障语义
- **真实事件优先**: 任何一条 lesson 都标注了真实事件时间戳，可在 git log / memory / agent-reach 输出中验证

## 下一步（克莱恩未拍板）

- **继续写 lesson-11+**（克莱恩要的"50 条"还差 40 条）
- **推送 lesson-06 ~ 10 到 misakanet 主仓**（以 PR 形式）
- **重写 lesson-01 ~ 05**（把新闻报道改成真实故障——但需要先有真实事件，否则就只是包装）
- **暂停 / 调整方向**（任何时候）

## 节奏守则

克莱恩 2026-07-03 拍板：
- 真实事件优先 — 不编造场景
- 卡点翻 misakanet 现成 lesson（不需要请示）
- 75+ 评分门槛 — 不达不收
- 不动 destructive 操作（不删 commit 历史、不 force push）