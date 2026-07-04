---
type: Knowledge Bundle
title: Big-Repo PR 知识库
description: 大型开源项目（star ≥ 1k）PR 模式 + 经验沉淀，Agent 可读结构化数据
version: 0.2.0
created: 2026-07-01
updated: 2026-07-02
author: zsxh1990 + 太阳 (Misaka10004)
based_on:
  - openclaw-pr-knowledge/report.md
  - uv-pr-knowledge/report.md
conforms_to: OKF v0.1 (Sudhakaran88/okf-conformance) + agent_guidelines extension
---

# Big-Repo PR 知识库

> 在大型开源项目（star ≥ 1k）上提 PR 的模式与经验沉淀。  
> 收录对每个目标仓的**画像**（友好的维护者风格、提 PR 方向、SOP、反模式） + **单 PR 案例**（合并 / close / amend 完整链路）。  
> 格式遵循 [Google Open Knowledge Format v0.1](https://github.com/Sudhakaran88/okf-conformance) —— 纯 Markdown + YAML frontmatter，路径即 ID，零运行时依赖。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OKF v0.1](https://img.shields.io/badge/OKF-v0.1-blue.svg)](https://github.com/Sudhakaran88/okf-conformance)
[![AI-assisted](https://img.shields.io/badge/AI-assisted-welcomed-brightgreen.svg)](CONTRIBUTING.md#ai-assisted-contributions)
[![Validate](https://img.shields.io/badge/validate-passing-brightgreen.svg)](./validate.py)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/zsxh1990/pr-genius.git
cd pr-genius

# Validate
python3 validate.py        # soft checks
python3 validate.py --strict  # strict checks

# Browse
cat index.md               # root entry
cat <org>-<repo>/index.md  # repo profile
cat <org>-<repo>/pr-N-*.md # PR case study
```

## 📖 Contributing

We welcome contributions — see [CONTRIBUTING.md](CONTRIBUTING.md) for the
quick-start guide. AI-assisted PRs are first-class citizens; please disclose
when you open a PR.

## 🤝 Community

- 📋 [Code of Conduct](CODE_OF_CONDUCT.md)
- 🐛 [Issue Tracker](../../issues)
- 💬 [Discussions](../../discussions)
- 📜 [Changelog](CHANGELOG.md)
- 🚫 [Blacklist](BLACKLIST.md) — repos we won't track

## 📊 Stats

| Metric | Value |
|---|---|
| Repo profiles | 11 (incl. NousResearch/hermes-agent) |
| PR case studies | 11 (2 migrated to v0.5.0 schema, 9 in legacy v0.1) |
| Anti-patterns | 4 |
| Lessons (misakanet-50) | 10 |
| Validator checks | 4 (frontmatter / links / consistency / rounds schema) |
| OKF compliance | ✅ v0.1 |
| Schema version | rounds v0.5.0 |

## 这是什么 / 给谁看

- **作者背景**：维护者提外部 PR（AI-assisted 公开声明），失败/合并均记录。  
- **读者画像**：想在大仓提 PR 的外部贡献者、想了解 vibe-coding / AI-assisted PR 在主流社区命中率的观察者、做工具自动化扫描的 agent。  
- **不收录**：被永久拉黑的仓（microG / OpenBSD / GNOME / Linux kernel / systemd / Vite）、单 PR 失败仓（无重复模式可沉淀的）。  
- **格式契约**：每个仓 = 1 个 `index.md`（Repo Profile）+ 1+ 个 `pr-<num>-<slug>.md`（PR Case Study），所有概念走 frontmatter `type` 字段分类。

## 入口

→ **[index.md](./index.md)** 是 OKF bundle 根入口（知识包主索引）

## 进阶结构（Agent-first）

- 📋 **[AGENT_GUIDELINES_SCHEMA.md](./AGENT_GUIDELINES_SCHEMA.md)** — 每个仓 frontmatter 里 `agent_guidelines` 字段的 schema（Agent 可读 yaml 控制流）
- 🚫 **[BLACKLIST.md](./BLACKLIST.md)** — 永久拉黑仓（Vite / microG / OpenBSD / GNOME / Linux / systemd）
- ⚠️  **[anti-patterns/](./anti-patterns/README.md)** — 可检索反模式库（CI 报错 / 维护者拒绝语 → fix_action 秒级自愈）
- 🔁 **[ROUNDS_SCHEMA.md](./ROUNDS_SCHEMA.md)** — PR Case Study `rounds` 字段 schema（多轮交互日志）
- 🔧  **[validate.py](./validate.py)** — OKF v0.1 校验脚本（frontmatter + 死链 + 一致性）

## 统计

| 维度 | 数据 |
|---|---|
| 覆盖大仓（star ≥ 1k）| **8 个** |
| 总 .md 文件 | **27 个** |
| Repo Profile（仓画像）| 8 |
| PR Case Study（单 PR 深读 + rounds）| 8 |
|   ├─ 已迁 v0.5.0 schema（action enum + delta object + close_decision）| 2 (honcho + qdrant) |
|   └─ 未迁 v0.5.0 schema（warning 状态）| 6 |
| Anti-Pattern（反模式）| 4 |
| Schema Reference / Blacklist / Bundle | 6 |
| 总大小 | ~255 KB |
| Agent 友好度结构化（agent_guidelines）| **8/8 仓 ✅** |
| 联邦声明（federates_with）| **根 + 8 仓 ✅** |
| validate.py Check 数 | **4** (frontmatter / 死链 / 一致性 / rounds v0.5.0) |

## 8 个大仓速查

| 仓 | Star | 仓 Profile | 关键 PR |
|---|---|---|---|
| astral-sh/uv | 86.9k | [astral-sh-uv/](./astral-sh-uv/index.md) | [pr-19685](./astral-sh-uv/pr-19685-sarif-audit.md) |
| plastic-labs/honcho | 5.6k | [plastic-labs-honcho/](./plastic-labs-honcho/index.md) | [pr-801](./plastic-labs-honcho/pr-801-queue-purge.md) |
| harbor-framework/harbor | 2.8k | [harbor-framework-harbor/](./harbor-framework-harbor/index.md) | [pr-2121](./harbor-framework-harbor/pr-2121-optional-deps.md) |
| punkpeye/fastmcp | 3.2k | [punkpeye-fastmcp/](./punkpeye-fastmcp/index.md) | [pr-282](./punkpeye-fastmcp/pr-282-test-with-ollama.md) |
| sourcebot-dev/sourcebot | 3.5k | [sourcebot-dev-sourcebot/](./sourcebot-dev-sourcebot/index.md) | [pr-1383](./sourcebot-dev-sourcebot/pr-1383-ctags-failure-detection.md) |
| future-agi/future-agi | 1.2k | [future-agi-future-agi/](./future-agi-future-agi/index.md) | [pr-778](./future-agi-future-agi/pr-778-span-list-without-project-id.md) |
| qdrant/mcp-server-qdrant | 1.4k | [qdrant-mcp-server-qdrant/](./qdrant-mcp-server-qdrant/index.md) | [pr-143](./qdrant-mcp-server-qdrant/pr-143-ollama-provider.md) |
| e2b-dev/E2B | 12.7k | [e2b-dev-e2b/](./e2b-dev-e2b/index.md) | [pr-1413](./e2b-dev-e2b/pr-1413-rich-to-ansi.md) |

## OKF 合规

- ✅ M1: bundle = 目录 + 17 .md 文件
- ✅ M2: 每个 .md 以 YAML frontmatter 起头
- ✅ M3: 每个概念文件有 `type` 字段（Knowledge Bundle / Repo Profile / PR Case Study）
- ✅ M4: 59 个内部 .md 链接全部解析
- ✅ M5: 路径即 ID
- ✅ M6: 纯文本，无 SDK/网络依赖
- ✅ S1: 根 `index.md` 入口
- ✅ S2: 每子目录 `index.md` 索引子概念
- ✅ S4: 无孤立文件

## 工作流

### 新仓加入

```bash
# 1. 创建子目录
mkdir research/big-repo-pr-knowledge/<org>-<repo>/

# 2. 写 <org>-<repo>/index.md（Repo Profile）
#    - YAML frontmatter + type: Repo Profile
#    - 友好度画像 + zsxh1990 PR 历史 + 提 PR 方向 + SOP + 反模式

# 3. 写 <org>-<repo>/pr-<num>-<slug>.md（PR Case Study）
#    - 每次提新 PR 都补一份

# 4. 更新根 index.md（链接新仓）
```

### 增量更新

每次提新 PR → 必须补 `PR Case Study`，否则不符合 OKF S3（单职责）。
每次 close / merge → 更新对应 PR Case Study 的 `status` 字段 + 加教训到 `MEMORY.md`。

## 关联

- [OpenClaw PR 知识库（200 PR 深读）](../openclaw-pr-knowledge/README.md) — 单独归档，OpenClaw 是极端大仓
- [uv PR 精简报告](../uv-pr-knowledge/report.md) — uv 调研原始数据
- [OKF 规范](https://github.com/Sudhakaran88/okf-conformance/blob/main/CONFORMANCE.md)

## 🔗 MisakaNet Federation（联邦声明，v0.3.0）

> 本仓是 [MisakaNet](https://github.com/Ikalus1988/MisakaNet) 的**外部 PR 经验子库**。  
> 采用**声明式联邦**模式：pr-genius 与 MisakaNet 主树互相声明对方为知识源，**不迁移内容、不改主树结构**。

### 联邦原则

- ✅ **声明 ≠ 迁移**：本仓保留完整所有权，MisakaNet 保留完整所有权
- ✅ **查询路径而非内容**：本仓的 `misakanet_queries` 字段声明"想从 MisakaNet 拉取什么"，但实际查询走 MisakaNet
- ✅ **单向贡献**：本仓的 lessons 可以被 MisakaNet 引用（如 honcho #801 的 default-parameter-trap），但不自动同步
- ❌ **不**双向 push、❌ 不同步 commit、❌ 不改 MisakaNet 主树

### 联邦字段规范

```yaml
# pr-genius 一侧（本仓）
federates_with:
  - misakanet/lessons/contrib/pr-strategy.md
federation_mode: query-only

# 每个 repo profile 加：
misakanet_queries:
  - <misakanet 路径>#<anchor>  # 本仓想拉的查询
misakanet_lessons:
  - id: <lesson-slug>
    contributed_via: <org>/<repo>#<num>  # 反向贡献来源
```

### MisakaNet 一侧（计划中，克莱恩拍板后实施）

预计在 MisakaNet 主树加：
- `lessons/contrib/pr-strategy.md`（从本仓 8 仓画像蒸馏的策略总表）
- `agents/sun/federation/peers/pr-genius.md`（太阳节点联邦声明）
- `tools/federation.py`（双向查询脚本 v1）

### 受益表

| 谁 | 受益 |
|---|---|
| 太阳 (Misaka10004) | 提 PR 时 1ms 拉 yaml 控制流决策，不读 5k 散文 |
| MisakaNet | 多一个外部 PR 经验数据源（只读） |
| 后续 1000+ 节点 | 同上，无需重新调研 8 仓 |

### 当前状态

- ✅ 根 `index.md` 加 `federates_with`（v0.3.0）
- ✅ 8 仓 repo profile 加 `misakanet_queries` + `misakanet_lessons`
- ✅ 本 README 加 Federation 节
- ✅ validate.py 不破（frontmatter / 死链 / 一致性全绿）
- ⏸ MisakaNet 主树：不动（克莱恩拍板后）

## 引用本仓库

```bibtex
@misc{pr-genius-2026,
  title  = {Big-Repo PR Knowledge Base},
  author = {zsxh1990},
  year   = {2026},
  url    = {https://github.com/zsxh1990/pr-genius}
}
```

---

## 📝 更新日志

### 2026-07-02 v0.5.0（rounds schema 实证升级）

- ✅ **action 枚举化**（9 值：`open`/`amend`/`bot_review`/`human_review`/`check_in`/`bump`/`close`/`merge`/`decision`）
- ✅ **delta 对象化**：`{kind, value}` 三类 `code_change` / `no_code_change` / `unknown` 解决裸 null 歧义
- ✅ **close_decision case-level**：5 status `pending`/`close`/`keep_open`/`merged`/`superseded`，不再野外字段
- ✅ **2 真实 PR 样本迁移**（honcho #801 4 rounds + qdrant #143 3 rounds）
- ✅ **validate.py Check 4** + `--strict` 模式（非迁移 = warning，--strict = error）
- ✅ **6 case 未迁移**（克莱恩 gate "别全仓大迁移"，保持 warning 状态）
- 触发：honcho + qdrant 2 真实样本证明 schema 缺陷不个别 → 升 v0.5.0

### 2026-07-02 v0.4.0（多轮交互日志 rounds）

- ✅ **ROUNDS_SCHEMA.md** 新增（PR Case Study `rounds` 字段 schema）
- ✅ **8/8 PR Case Study** 全加 `rounds` 字段（保留攻防过程，不只是结果）
- 总 rounds 计数：uv 2 / honcho 3 / harbor 1 / fastmcp 2 / sourcebot 1 / future-agi 3 / qdrant 1 / E2B 2
- 最终状态：1 merged (E2B #1413) / 1 closed-not-merged (uv #19685) / 6 open（含 1 stale）
- 触发：克莱恩 5 条升级建议第 3 条「多轮交互逻辑」+ 2026-07-02 23:25 GMT+8 拍板启动

### 2026-07-02 v0.3.0（MisakaNet 联邦声明）

- ✅ 根 `index.md` 加 `federates_with` 字段 + 2 个查询路径
- ✅ 8 仓 repo profile 加 `misakanet_queries` + `misakanet_lessons` + `federation_status`
- ✅ README 加 "MisakaNet Federation" 节（声明原则 + 字段规范 + 受益表）
- ✅ **不动 MisakaNet 主树 / 不迁移内容 / 不改目录结构**
- 触发：克莱恩 2026-07-02 23:07 GMT+8 拍板（federation gate）

### 2026-07-02 v0.2.0（克莱恩拍板升级 → Agent-first）

- ✅ **agent_guidelines 字段** 加入所有 8 仓 frontmatter（17 个 yaml 键）
- ✅ **AGENT_GUIDELINES_SCHEMA.md** 文档（schema 定义 + 调用示例）
- ✅ **BLACKLIST.md** 永久拉黑仓排雷指南（6 仓 + 2 归档方向）
- ✅ **anti-patterns/** 目录（4 条真实反模式：uv cargo fmt / Vite 秒拒 / honcho db 陷阱 / e2b not adding）
- ✅ **validate.py** OKF v0.1 校验脚本（frontmatter + 死链 + 一致性，3 check）
- ✅ README 加 frontmatter + 进阶结构章节
- 触发：克莱恩 5 条升级建议（结构化友好度 / 反模式 / 多轮日志 / 黑名单 / 校验脚本）前 4 条落地
- 下一步：阶段 3（多轮交互日志 rounds 字段）—— 克莱恩拍板后启动

### 2026-07-01 v0.1.0（克莱恩拍板建立）

- 创建 OKF bundle 结构（17 文件 / 8 仓）
- 8 个仓 Profile + 8 个 PR Case Study 占位/完整
- OKF M1-M6 + S1-S4 全合规
- 增量规则：提新 PR → 自动补 PR Case Study