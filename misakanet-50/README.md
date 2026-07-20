---
type: Index
title: MisakaNet Lessons — pr-genius Source Quality Index
description: pr-genius 仓下 misakanet-style lessons (75+ score threshold)
version: 0.3.0
created: 2026-07-03
updated: 2026-07-03
---

# misakanet-50/ — Lessons Index

> 克莱恩 2026-07-03 拍板（v0.3.0 修订）：
> - lesson **不要求真实事件**（克莱恩 00:57 纠正）
> - **要求**：过程描述详尽 / 细节值得推敲 / 权威仓库推荐 / 主题类似 misakanet / 足够泛化 / 脱敏
> - **要求**：建立置信度评分系统（见 `SCORING.md`）

## Lesson 评分门槛

按 `SCORING.md` v0.1 体系：
- **4 维度**：源可信度(30) + 细节质量(25) + 通用化(25) + 脱敏度(20)
- **75+ 入库**（misakanet `LESSON_QUALITY_SCORING.md` 同步校验）
- **A/B/D 三档**：A=85+/100, B=75-84, D=<75

## Lesson 分类（18 条 + 评分）

### A. 真实故障 + 高源可信度（lesson-06 ~ 10）✅ 双向合格

| # | 标题 | 源类型 | 源分 | 总分 | 主题 | misakanet 收录？ |
|---|---|---|---|---|---|---|
| 06 | git push 撞 ikalus PAT 403 | own-git-history | 25 | 85 | devops | ✅ |
| 07 | uv venv --seed 替代缺 pip | own-install-experience | 25 | 90 | devops | ✅ |
| 08 | pip install HTTPS_TIMEOUT 撞代理 | own-install-experience | 25 | 85 | devops | ✅ |
| 09 | V2EX API /api/topics/show.json 不稳 | own-fetching | 22 | 85 | scraping | ✅ |
| 10 | agent-reach doctor baseline | own-install-test | 22 | 80 | tooling | ✅ |

### B. 论坛高赞帖 + 主题类内（lesson-01, 02, 04, 05）✅ 主题内，可入库

| # | 标题 | 源类型 | 源分 | 总分 | 主题 | misakanet 收录？ |
|---|---|---|---|---|---|---|
| 01 | Vibe Coding Team Out of Control | forum_thread (V2EX 93 reply) | 20 | 85 | agent | ✅ |
| 02 | AI Code Review: When to Skip vs Read | forum_thread (V2EX 68 reply) | 20 | 85 | agent | ✅ |
| 04 | AI API Relay Risks | forum_thread + own-knowledge | 22 | 83 | claude/codex | ✅ |
| 05 | vless+xhttp+reality Blocked | forum_thread + own-knowledge | 22 | 83 | network | ✅ |

### C. 主题不直接收（lesson-03）— 留作 pr-genius 个人资料

| # | 标题 | 源类型 | 源分 | 总分 | 主题 | misakanet 收录？ |
|---|---|---|---|---|---|---|
| 03 | AI Monthly Cost Baseline | forum_thread (V2EX 130 reply) | 20 | 76 | data-survey | ❌ 不属于"踩坑"语义 |

### D. pr-genius 实战沉淀（lesson-11, 13 ~ 18）✅ Month 2/3 P0 — A 级全员

| # | 标题 | 源类型 | 源分 | 总分 | 主题 | misakanet 收录？ |
|---|---|---|---|---|---|---|
| 11 | MCP typo-pool x3 merged | own-git-history | 26 | 88 | mcp | ✅ |
| 13 | Glama Private MCP Verification Gate (4 evidence) | own-deploy-experience | 28 | 92 | deployment | ✅ |
| 14 | Check Tier Upgrade warning → error 模式 | own-rule-engine | 28 | 95 | rule-engine | ✅ |
| 15 | Duplicate Detector Trigger 4 → 7 扩展 (hard/soft/info) | own-rule-engine | 28 | 95 | rule-engine | ✅ |
| 16 | ContribAI Replay 15/15 = 100% Hit Rate | own-evaluation | 28 | 93 | evaluation | ✅ |
| 17 | Data Snapshot / README Metric Unification | own-documentation | 27 | 95 | documentation | ✅ |
| 18 | Knowledge Bundle Self-Reference Boundary | own-architecture | 28 | 96 | architecture | ✅ |

### E. 其他（lesson-12）— 占位

| # | 标题 | 源类型 | 源分 | 总分 | 主题 | misakanet 收录？ |
|---|---|---|---|---|---|---|
| 12 | (空号，未占用) | — | — | — | — | — |

## 克莱恩纠偏记录

| 时间 | 拍板 | 含义 |
|---|---|---|
| 00:14 | 要 agent-reach + 50 lessons | 工具与目标 |
| 00:46 | lesson 必须真实故障 | 起初标准 |
| 00:57 | **纠正**：不要求真实，要求评分系统 | **修订标准**：源可信度 + 细节 + 通用化 + 脱敏 |
| 2026-07-20 18:42 | **拍板 pr-genius Month 3 P0 沉淀** | C 先 5 条 lessons,A 再 private 验证,B 不上 public |

**v0.5.1 → v0.5.2 调整**：lesson-01 ~ 05 从"⚠️ 不符合"标记改成"✅ 主题内可入库"——克莱恩原意是"新闻报道 too shallow"，不是"不能用论坛源"。

**v0.5.2 → v0.5.3 调整**：lesson-11 + 13-17 补入 — Month 2/3 pr-genius 实战沉淀全部 A 级 — 克莱恩 2026-07-20 18:42 拍板

## 下一步（克莱恩未拍板）

- **A**: 推送 lesson-01/02/04/05/06/07/08/09/10/11/13/14/15/16/17 到 misakanet 主仓（PR 形式）
- **B**: 继续抓 lesson-12,18+（用 GitHub Search API 找权威 issue/discussion）
- **C**: 用 `SCORING.md` 重评分全部 17 条 + 输出"推送候选"列表
- **D**: 跑 A 阶段 Glama private 4 项 evidence（克莱恩 2026-07-20 18:42 拍板）

## 节奏守则

克莱恩 2026-07-03 拍板：
- **过程描述详尽 / 细节值得推敲** = lesson 价值的核心
- **权威源推荐** = 4 维度里源可信度的关键
- **不要为抓取而抓取**：lesson 主题必须类内 + 可复用 + 脱敏
- 75+ 评分门槛
- 不动 destructive 操作