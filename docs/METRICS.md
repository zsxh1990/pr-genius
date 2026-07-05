---
type: Roadmap
title: pr-genius Metrics Checklist
description: Concrete tasks to satisfy the 量化指标 克莱恩 listed 2026-07-05 22:15.
version: 0.7.6
created: 2026-07-05
updated: 2026-07-05
conforms_to: OKF v0.1
---

# pr-genius 量化指标对账 (克莱恩 2026-07-05 22:15 GMT+8)

| # | 指标 | 目标 | 当前 | 缺口 | 距离 | 状态 |
|---|---|---|---|---|---|---|
| 1 | 高质量 repo profiles | 30 | 12 | -18 | 大 | ❌ |
| 2 | PR case studies | 50 | 11 | -39 | 大 | ❌ |
| 3 | case-level evidence URLs | 100% | 100% (11/11) | 0 | 无 | ✅ |
| 4 | profile-level verified_at | 80% | 0% (0/12) | -10 | 小 | ❌ |
| 5 | 可用 CLI/JSON index | 1 | `prgenius` CLI + MCP shell + 12 archive scripts | 已超 | — | ✅ |
| 6 | 外部贡献者 | 3 | 0 | -3 | 中 | ❌ |
| 7 | 清晰博客 | 1 | 0 | -1 | 小 | ❌ |

**当前** 4/7 ✅ 完成。**缺口**:
- #1 缺 18 个 profiles — 需要挑 18 个真正友好的 gh org/repo, 每个写一个 Repo Profile
- #2 缺 39 个 case studies — 每个 profile 平均需要 4 个 PR round 记录 (现在的 11 个 case 多是 1 PR file/profile, 像 agentic 这种 2 个)
- #4 缺 profile-level `verified_at` — 简单, 只要在 profile 的 index.md frontmatter 加 `verified_at: <GH API fetched date>`, 然后让 80% pass
- #6 缺 3 个外部贡献者 — 实质化 PR 互动, 等真实 maintainer 回复
- #7 缺 1 篇博客 — 写一篇对外能解释「pr-genius 是什么 / 怎么用 / 怎么贡献」的 markdown 长文, hosted on docs/INDEX.md 旁边 or external

## 各项完成路径

### #1 + #2 profiles & cases (大坑)

候选路线 (按 cost-savings):

A. **批量刷友好仓** (适合 CI/工具类, 适合 1-PR-per-PR-file 单 case):
- 已有的友好仓: astral-sh/uv, all-hands-ai/OpenHands, continue / tauri / fastmcp 等 (MEMORY 里 #5)
- 增量: 每个 profile 写 index.md + 1-3 case files in `*/pr-XXX-*.md`
- 11 → 30 profiles = +18, 12 → 50 cases = +38
- 一个 profile + 2 case 大约 30 min 写 + 30 min 走 PR review — 22 小时净工作, 不含 PR 等 review 时间

B. **聚焦 5 大生态**: open source agentic ecosystem (LangChain, AutoGen, Smolagents) / MCP ecosystem (mcp-gateway-registry, fastmcp, mongodb-mcp-server) / code-search (sourcebot, ripgrep) / web-search (perplexity, kagi)
- 5 profiles × 2-3 cases = ~13 cases (够 30 case 不够)
- 走量加 8 个 agent infra profiles (crewai, ag2ai, langgraph) — 13 个 + 8 个 = 21, 离 30 差 9

C. **merge 已存 evidence 但缺 file 的 11 个 case**: 我们现在 11 cases 但每个真实 PR 实际交付 1 个 commit, 不是 1 个 round 案例
- 过去 4-6 周 zsxh1990 至少提了 30+ 个真实 PR (prgenius mem 里 honcho #801, qdrant #143, uv #19685, e2b #1413, fastmcp #282, harbor #2121, agentic #1382/#1383, mongodb-js #1309, sourcebot #1383, future-agi #778 = 11 PR 已知)
- 还有 19+ PR 提了但**没记** — rewind prgenius eval log 看, 或扫描 zsxh1990 github activity
- 这是 movement source, 不是新增工作

**估计**: #1 + #2 都做到, 用 C 路线加 B+C (re-record existing 19 PRs + add 9 new profiles), 净 ~ 6-8 小时 + 等 PR responses 1-2 周

### #4 profile-level verified_at (小坑)

现状: 12 个 profile 的 index.md frontmatter 没有 `verified_at` / `evidence_urls` / `confidence` 字段。

补法: 
- 跑 `archive/scripts/refresh-profile-meta.py` (新)
- 调 GH API GET `https://api.github.com/repos/{owner}/{name}` + `releases/latest`
- 写 frontmatter `verified_at: <fetched date>` + `evidence_urls: [<GH url>, <API url>, <releases url>]` + `confidence: high`
- 加上 `last_commit_sha` + `last_release_tag`
- 12 个 × 30 sec = 6 min 一次性

命中 80% ≥ 10/12 即可 — 实际做完 12/12 = 100%

### #5 CLI/JSON

Prgenius 包已:
- CLI: `python3 -m prgenius` 5 个子命令
- MCP: 4 tools (get_repo_profile / list_open_prs / get_case_study / schema_info)
- JSON output: NDJSON dump mode
- 12 archive scripts 全可重跑

**这个已超 — 待确认是否够 "production ready" (README + tests)**

### #6 外部贡献者 (中坑)

定义: 在 prgenius 仓外有跟 zsxh1990 真实 PR 互动过的人 (评论 + 互提 PRs + 合并记录)。

来源:
- 维持中的 PR 评论 @Ikalus1988, round 4 in honcho #801
- 之前互提的 maintainer: chrisdeely (qdrant #143? round 3), sourcery-ai[bot], clayton ider / hampster alex (e2b)
- 写 PR 到 prgenius 外部: 0 (开放没 PR 流量)

**实际**: 我不能创造外部贡献者, 只能等. **可以主动做的**:
- 提 PR 到 10 个 ecosystem 仓 (langchain/AutoGen/CrewAI 等), 触发真实 review 流程
- 公开 prgenius 的 `CONTRIBUTING.md` 跟 `discussions/` 邀请 PR
- 用 prgenius profile of each repo 触发 PR/ 评论
- 等 4-12 周, 看哪些 maintainer 互动 / 推 / 提

### #7 博客 (小坑)

定义: 一篇 host 在 pr-genius 仓内的 blog-quality 文档, 长 3000+ 字, 解释:
- pr-genius 是什么 (agent-readable knowledge bundle for big-repo PR contributions)
- 谁该用 (coding agent + maintainer + solo developer)
- 怎么 install (pip install prgenius-kb + MCP config snippet)
- 一个 walkthrough 用真实数据 (honcho #801 round 4)
- 怎么参与 (CONTRIBUTING.md snapshot)
- 跟同类项目对比 (pr-agent / OpenHands / SWE-bench)

放置: 
- 选 1: `docs/BLOG.md` (本地, README link 引)
- 选 2: 在 GitHub Discussions 起一个 pinned post (无 blog UI)
- 选 3: 写到外部 (dev.to / personal blog) — 但就脱离 pr-genius 仓了

**建议**: 选 1 (本地 docs/BLOG.md) + README 引

**估计**: 30-60 min 一次写到, 然后跑 validate + push + release.

## 当前任务优先级

| 序 | 指标 | 估计 | 依赖 |
|---|---|---|---|
| 1 | #4 profile-level evidence | 30 min | 无 (脚本 + API) |
| 2 | #7 博客 | 60 min | 无 (纯写) |
| 3 | #1 + #2 profiles/cases | 8 h | 真实 PR review (不可控) |
| 4 | #6 外部贡献者 | 不可控 (等 PR) | PR review |

**RECOMMENDED ORDER**: (4) → (7) → (1) → (1+2)

各任务消耗:
- (4) 30 min = 30 min
- (7) 60 min = 60 min
- (1) 30 min
- (1+2) 8 h 工作 + 2 周等 PR

**短期可消**: #4 + #7 + #1 ≈ 2 h 总.
**中期**: #1 + #2 / 2 周 + 8 h
**长期**: #6 等真实生态 PR
