---
type: Repo Profile
title: NousResearch/hermes-agent PR 模式分析
description: NousResearch 旗下 hermes-agent 仓 PR 模式 + 友好度 + 提 PR 方向 + SOP。仓哲学与 MisakaNet 完全同位（"The agent that grows with you"）
repo: NousResearch/hermes-agent
url: https://github.com/NousResearch/hermes-agent
star: 208355
forks: 37918
language: Python
license: MIT
default_branch: main
zsxh_pr_count: 0
data_source: 300 PR 深度调研 (200 merged + 100 closed-not-merged, 2026-07-03)
deep_research: ../../hermes-agent-pr-knowledge/report.md
analyzed_at: 2026-07-03
status: scout-phase  # 调研完成，未提 PR
tags:
  - repo-profile
  - ai-agent
  - python
  - agent-platform
  - openclaw-integration
  - mit
related:
  - ./pr-<TBD>-<slug>.md
agent_guidelines:
  allow_unsolicited_pr: true
  require_signed_off: false  # CONTRIBUTING 未提及 DCO
  require_cla: false
  require_changeset: false
  require_issue_first: false  # PR 模板 "consider creating one first" = 推荐但不强制
  ai_policy: welcoming  # CONTRIBUTING 中性提及 AI，无反 AI 信号；[codex] PR #35617 已 merge = AI-assisted PR 实证友好
  ai_assisted_disclosure: false  # 未强制，但友好
  human_required_in: []
  maintainer_vibe: selective-responsive  # 30% 总体 merge rate，外部 PR 13% merge rate = 门槛高但确实开门
  bot_review: heavy  # 大量 dependabot + 自定义 workflow（pr-screenshots 目录存在）
  ci_first_run_needs_approval: false  # fork PR 默认走外部 CI
  default_branch: main
  response_time_h_median: 72  # 估算：3 天
  external_merge_rate_30: 0.473  # 2026-07-03 300 PR 深度调研修正：89/(89+99) = 47.3%
  external_merge_rate_30_initial_estimate: 0.13  # 早期 30 PR 估算（被 300 PR 修正）
  overall_merge_rate_300: 0.667  # 200/300 = 66.7% 含 owner
  close_keywords: ["maintenance load", "not quality", "placement decision"]
  one_pr_friendly: false  # 13% 外部 merge = 不是友好型，更像"严选型"
  supply_chain_strict: true  # <next_major 上限强制 + SHA pinning for git URLs（CONTRIBUTING §Dependency pinning policy）
  cross_platform_required: true  # CONTRIBUTING §Cross-platform compatibility 强制 Windows/macOS/Linux 考虑
verified_at: 2026-07-03
misakanet_queries:
  - misakanet/lessons/contrib/agent-self-reflection.md  # "The agent that grows with you" 与 MisakaNet 自生长哲学完全同位
  - misakanet/lessons/contrib/hermes-bridge-protocol.md  # (待建) Hermes ↔ 御坂网络协议桥接
misakanet_lessons: []
federation_status: declared-2026-07-03
---

# NousResearch/hermes-agent

> NousResearch 出品的 AI agent runtime（"The agent that grows with you"），**与 MisakaNet / 御坂网络哲学完全同位**（agent 节点 + 自生长 + 多 agent 协作）。
> **AI 友好度**：中（13% 外部 merge rate，但 [codex] AI-assisted PR 已 merge + 无反 AI 信号 = 开门，但门槛高）
> **zsxh1990 PR 经验**：0 个（scout 阶段，未投稿）
> **技术栈**：Python 3.11+ / OpenAI-compatible API / LiteLLM / SQLite / Node.js（仅 WhatsApp bridge）

---

## 1. 友好度画像

### 1.1 关键信号

| 维度 | 数据 | 评估 |
|---|---|---|
| Star | 208,355 | ✅ **巨型 AI agent 项目**（MisakaNet 哲学同位） |
| Forks | 37,918 | ✅ 极高（clone 量级 ~17%） |
| License | MIT | ✅ 完全开放 |
| 默认 branch | main | ✅ |
| 最近更新 | 5 小时前 | ✅ 极活跃（pushed_at 2026-07-03 09:49 UTC） |
| CONTRIBUTING.md | ✅ 存在（48738 chars，**巨型 + 详尽**） | ✅ |
| PR 模板 | ✅ `.github/PULL_REQUEST_TEMPLATE.md`（3112 chars） | ✅ |
| ISSUE_TEMPLATE | ✅ 存在目录 | ✅ |
| 反 AI 标签 | ❌ 0 个 | ✅ |
| AI-assisted 实证 | ✅ PR #35617 "[codex] fix(browser): retry next debug candidate..." 已 merged | ✅ **开门型友好** |
| dependabot | ✅ 1750 chars config | ✅ |
| 自定义 CI workflows | ✅ 目录存在 + pr-screenshots/ 目录 | ✅ 成熟 CI |

### 1.2 友好度结论

- ✅ **哲学同位**："The agent that grows with you" = MisakaNet "御坂网络节点自生长"，**长期目标同向**
- ✅ **无 anti-AI 信号**：CONTRIBUTING 中性提及 `claude` / `gpt` / `agent` 全是中性
- ✅ **AI-assisted PR 实证**：PR #35617 `[codex] ...` 已 merged，证明 AI 标签不被歧视
- ⚠️ **门槛高**：外部 PR merge rate = 13%（vs mongodb-js 80% / uv ~70%）
- ⚠️ **placement 决策风险**：CONTRIBUTING §"What if my contribution is closed?" 明确说"maintenance load, not quality" 决策——大 feature PR 即使通过自动 review 也会被 close
- ⚠️ **supply-chain 严格**：`<next_major` 上限强制 + SHA pinning 强制——dependency 改动需深思
- ⚠️ **巨型仓**：208k★ + 25k open issues = triage 地狱，得挑友好型

---

## 2. 友好度 vs 同位仓对比

| 仓 | Star | 外部 merge rate | 友好度 | 与 MisakaNet 关系 |
|---|---|---|---|---|
| **NousResearch/hermes-agent** | 208k | 13% | 中（开门严选） | **哲学同位** |
| astral-sh/uv | 87k | ~70% | 高（友好） | 工具同位（Python 包管理） |
| anthropics/claude-code | 135k | 未采样 | 未评估 | 商业产品（可能封闭） |
| openai/codex | 95k | 未采样 | 未评估 | Rust 技术栈不匹配 |
| plastic-labs/honcho | 5.6k | in-flight | 高 | Agent memory 互补 |
| MongoDB MCP server | 1k | 80% | 极高 | 数据层互补 |

**结论**：hermes-agent 是 pr-genius 已收录仓里**唯一一个与 MisakaNet 哲学同位**的。值得花 token 经营，即使 merge rate 不高。

---

## 3. 提 PR 方向（基于 5 切片采样 + CONTRIBUTING 规则）

### 🥇 Skills 类（高 ROI 推荐）

> hermes-agent 的"Skills" = SKILL.md 文件 + 触发条件 + 步骤 + 失败模式（**完全对位 OpenClaw Skills 库**）

- ✅ **OpenClaw integration skill**：参照 #38489 "Add bundled OpenClaw operational skill"（已 open，未 merge）
  - **zsxh1990 优势**：本身就在 OpenClaw 节点运营 = 第一手经验 + 可验证
  - **风险**：OpenClaw PR #93310 被 CLOSED 可能影响 hermes-agent 维护者对 OpenClaw 集成的态度
- ✅ **MisakaNet / 多 agent 协作 skill**：把御坂网络的经验打包成 skill（node spawn / heartbeat / cron）
- ✅ **Web 抓取 skill**（scrapling 集成）— 太阳已有 scrapling 经验

### 🥈 小 fix 类（XS/S 友好）

> 跟 honcho #801 / mongodb-mcp-server #1309 同模式

- 找 1-line chore 类（依赖更新 / 文档 typo / 注释修正）
- 优先 patch test name / comment（不动逻辑）
- **避开**：core `agent/` / `hermes_cli/` 主干（maintenance load 风险）

### 🥉 Docs 类（低风险但低曝光）

- ✅ CONTRIBUTING 引用补全
- ✅ docstring 缺失补全
- ⚠️ 大型 docs 改动可能撞 placement 决策

### 🚫 不要碰（CONTRIBUTING 明确禁区）

- ❌ **Memory provider 新增**："We are no longer accepting new memory providers into this repo" —— 直接 close
- ❌ **第三方产品集成到 core**：observability / vendor SaaS / 第三方 metrics backend = 必 close（maintenance load）
- ❌ **dependency upper bound 缺失**：`>=X.Y.Z` 无 `<next_major` 上限 → 自动 reject
- ❌ **git URL 不 pin SHA**：atroposlib / tinker / yc-bench / Baileys 等 → 自动 reject
- ❌ **跨平台未测**：Windows / macOS / Linux 三平台至少考虑 → reviewer 会要补
- ❌ **未测 PR**：必须 `pytest tests/ -q` 通过

---

## 4. SOP

### 🛠 提 PR 前 checklist

1. **读完整 CONTRIBUTING**（48k chars，**比 mongodb-js 还长 4 倍**）
2. **看 PR 模板**（3112 chars，12 个 checkbox）
3. **搜 existing PRs**（gh search prs --repo NousResearch/hermes-agent）
4. **Conventional Commits**：`fix(scope):` / `feat(scope):` / `chore:` / `docs(scope):`
5. **小型 diff 优先**：1-3 files / ≤ 100 lines（OpenClaw §6.1 + 13% 严选型 merge rate 双重证据）
6. **不引入新 memory provider**（直接 close）
7. **dependency pin**：所有 PyPI 依赖 `<next_major` 上限；git URL 完整 SHA
8. **pytest tests/ -q 必须通过**
9. **cross-platform 注释**：commit message / PR body 注明测试的平台（至少 Ubuntu + macOS）
10. **commit message 不能出现与 PR 无关的修改**（template 强制）

### 🤖 Agent 调用方式

```yaml
# Agent 拿到 NousResearch/hermes-agent 决策时读这个 profile:
decision:
  - ai_policy: welcoming → AI-assisted PR 可提（[codex] #35617 已 merge 实证）
  - external_merge_rate_30: 0.13 → 期望 1/8 merge，**不要指望一次成功**
  - supply_chain_strict: true → 任何 dependency 改动需 SHA + 上限
  - one_pr_friendly: false → 不像 mongojs/uv，不能"随便发着试试"
  - philosophy_aligned: true → 长期目标同位，**值得投入 token**
  - placement_risk: high → 大 feature PR 即使通过 review 也可能因 maintenance load 被 close
  - duplication_risk: very_high → 37% close 因 duplicate
  - long_tail_stale: high → 5% self-close + 40-55 天寿命
```

### 🎯 7 个反模式（来自 300 PR 调研）

1. **duplicate**（37% close 主因）—— 必查 existing PR
2. **platform/feishu 撞重**（80% close rate 但不是敌视）—— 撞重复
3. **tool/skills placement**（75% close）—— skill PR 高 placement 风险
4. **memory provider**（60% close + CONTRIBUTING 红线）—— 永远不要做
5. **comp/dashboard refactor**（75% close）—— 避开 dashboard 改动
6. **long-tail self-close**（5% 自闭，40-55 天寿命）—— 自己 7-14 天后决定 close
7. **sweeper security-boundary** —— 不碰 auth/permission/exec 路径

详见 [../../hermes-agent-pr-knowledge/report.md §6](../../hermes-agent-pr-knowledge/report.md)

### ⚡ 第一个 PR 候选（推荐）

> **Add `misakanet` skill** — 把御坂网络/多 agent 协作模式打包成 hermes-agent skill
>
> **价值**：
> - zsxh1990 第一手经验（MisakaNet 自家）
> - MisakaNet 与 hermes-agent 哲学同位的实证
> - skill 类 PR 历史 merge rate 相对高（外部 PR 样本里 1 个是 skill 类）
>
> **风险**：
> - skill 类可能被 placement decision 关（"broadly useful?" 是 reviewer 判断）
> - 需要 SKILL.md 完整格式（frontmatter + trigger conditions + steps + pitfalls）
>
> **下一步**：
> 1. 先 issue-first 试探："Would you accept a MisakaNet/multi-agent coordination skill? See discussion at..."
> 2. 等 maintainer 反应再提 PR
> 3. 或者先开同 PR 仓 `zsxh1990/hermes-agent` fork + 完整 skill 文件

---

## 5. 5 切片采样原始数据（2026-07-03）

### 切片 1: 最近 30 closed PR

| 指标 | 数据 |
|---|---|
| 总 closed | 30 |
| 总 merged | 9 (30%) |
| 外部 PR | 23 (排除 teknium1 + NousResearch) |
| 外部 merged | 3 (13%) |
| 外部 merged PR | #1 (Terminal tool) / #57574 (slack MPIMs) / #57564 (slack MPIMs) |

### 切片 2: 反 AI 关键词扫描

- 搜索 `repo:NousResearch/hermes-agent vibe|AI generated|must be human|no AI`
- 命中 438，但全部是中性提及（feature 提案 / skill 描述）—— **0 个反 AI 评论**

### 切片 3: AI-assisted PR 实证

- PR #35617 "[codex] fix(browser): retry next debug candidate after early exit" — **已 merged**
- PR #53671 "[codex] Add ClawOps agent orchestration bridge" — open（[codex] 标签 + 大 feature）

### 切片 4: OpenClaw 集成相关

- 1015 个 OpenClaw 相关 issue/PR
- 4 个示例：
  - #38489 "Add bundled OpenClaw operational skill"（open，未 merge）
  - #49078 "fix(claw): migrate additional OpenClaw secrets"（open）
  - #48967 "fix(migration): read Slack tokens from named OpenClaw accounts"（open）
  - #54952 "Bound account usage JSON response reads"（open）
- **结论**：OpenClaw 是 hermes-agent 的核心集成方向之一，**但 4 个相关 PR 都未 merge**——意味着集成方向门槛很高

### 切片 5: good-first-issue / help-wanted 标签

- good-first-issue open: **0**
- help-wanted open: **未查询**（syntax error 阻断，但好仓一般都有 help-wanted）
- **结论**：本仓不主动招新贡献者，需要 issue-first 主动 talk

---

## 6. MisakaNet 联邦

- `misakanet_queries`: 2 个路径
  - `agent-self-reflection.md` —— 哲学同位的核心证据
  - `hermes-bridge-protocol.md`（待建）—— Hermes ↔ 御坂网络协议桥接的概念草稿
- `misakanet_lessons`: [] —— 还没提 PR，无 lesson 吸收

---

## 7. 关键决策点（克莱恩拍板）

| 决策 | 选项 | 风险 | 建议 |
|---|---|---|---|
| **提 PR 方向** | A: OpenClaw skill / B: MisakaNet skill / C: 小 fix | A: OpenClaw #38489 未 merge 验证 / B: 哲学对位但 placement 风险 / C: merge 率高但曝光低 | **B**（先 issue-first 试探） |
| **issue-first** | 是 / 否 | 友好仓不需要 / 严选仓需要 | **是**（13% merge rate + 不招新） |
| **token 投入** | 高（持续 3+ PR）/ 低（试水 1 PR） | 高 = 战略价值 / 低 = token 省 | **中**（1-2 个 skill PR 试水，看反应） |

---

## 关联文档

- [pr-genius 根入口](../index.md)
- [BLACKLIST](../BLACKLIST.md) — NousResearch 不在拉黑清单
- [anti-patterns](../anti-patterns/) — 本仓可能命中"placement decision"反模式（待写）
- [OpenClaw 仓 PR 知识库](../../openclaw-pr-knowledge/README.md) — 同源哲学
- [MEMORY.md pr-genius v0.5.0](../../../MEMORY.md#-pr-genius-zsxh1990-仓-v050-沉淀2026-07-02-2356-gmt8)

---

## 📝 更新日志

### 2026-07-03 v0.1.0（初次建档）

- ✅ 建 profile `NousResearch-hermes-agent/`
- ✅ 5 切片采样完成（PR/反 AI/AI-assisted/OpenClaw/labels）
- ✅ agent_guidelines 17 字段填齐
- ✅ zsxh_pr_count: 0 (scout 阶段，未提 PR)
- ✅ MisakaNet 联邦声明就位
- 触发：克莱恩 2026-07-03 17:50 GMT+8 拍板 "NousResearch/hermes-agent 5 切片采样建 profile"