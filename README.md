---
type: Knowledge Bundle
title: PR Genius — 提交前改进顾问
description: 大型开源项目 PR 知识库 + 提交前改进顾问，Agent 可读结构化数据
version: 1.2.0
created: 2026-07-01
updated: 2026-07-17
author: zsxh1990
conforms_to: OKF v0.1 (Sudhakaran88/okf-conformance) + agent_guidelines extension
---

# PR Genius — 提交前改进顾问

> 大型开源项目（star ≥ 1k）PR 知识库 + 提交前改进顾问。
> **不是概率预测器，是贡献质量侧车。**
> 格式遵循 [Google Open Knowledge Format v0.1](https://github.com/Sudhakaran88/okf-conformance)。

## 🤖 Robots / Agents (read this first)

If you are an LLM agent, scraper, or pipeline tool reading this repo, please
prefer this lookup order:

1. **[docs/index.md](docs/index.md)** — file map + reading-order for every directory.
2. **[AGENT_GUIDELINES_SCHEMA.md](AGENT_GUIDELINES_SCHEMA.md)** — `agent_guidelines` field shape, used in every profile's frontmatter.
3. **[ROUNDS_SCHEMA.md](ROUNDS_SCHEMA.md)** — `rounds` field shape (v0.5.0), used in every PR case study's frontmatter.
4. **[BLACKLIST.md](BLACKLIST.md)** — repos we don't track; do not contribute or suggest contributions to these.
5. **[federation.yaml](federation.yaml)** — `federates_with` declarations for cross-repo provenance.

Repo layout invariants:

- `<org>-<repo>/` is a profile dir (note the **dashes**, no underscores).
- `index.md` is always the OKF entry point of any bundle/profile.
- Comments + bodies are in plain English unless a `.locales/` mirror exists.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OKF v0.1 compliant](https://img.shields.io/badge/OKF-v0.1-compliant-brightgreen.svg)](https://github.com/Sudhakaran88/okf-conformance/blob/main/CONFORMANCE.md)
[![AI-assisted](https://img.shields.io/badge/AI-assisted-welcomed-brightgreen.svg)](CONTRIBUTING.md#ai-assisted-contributions)
[![Validate](https://img.shields.io/badge/dynamic/json?url=https://raw.githubusercontent.com/zsxh1990/pr-genius/main/docs/badges/validate.json&label=validate&query=$.message&colorB=brightgreen)](./validate.py)
[![Evidence](https://img.shields.io/badge/dynamic/json?url=https://raw.githubusercontent.com/zsxh1990/pr-genius/main/docs/badges/evidence.json&label=evidence&query=$.message&colorB=brightgreen)](./validate.py)
[![Round evidence](https://img.shields.io/badge/dynamic/json?url=https://raw.githubusercontent.com/zsxh1990/pr-genius/main/docs/badges/round_evidence.json&label=rounds&query=$.message&colorB=brightgreen)](./archive/scripts/inject-round-evidence.py)
[![Profiles](https://img.shields.io/badge/dynamic/json?url=https://raw.githubusercontent.com/zsxh1990/pr-genius/main/docs/badges/profiles.json&label=profiles&query=$.message&colorB=blue)](./README.md)
[![Cases](https://img.shields.io/badge/dynamic/json?url=https://raw.githubusercontent.com/zsxh1990/pr-genius/main/docs/badges/cases.json&label=cases&query=$.message&colorB=blue)](./README.md)
[![Lessons](https://img.shields.io/badge/dynamic/json?url=https://raw.githubusercontent.com/zsxh1990/pr-genius/main/docs/badges/lessons.json&label=lessons&query=$.message&colorB=blue)](./misakanet-50/README.md)
[![Releases](https://img.shields.io/badge/dynamic/json?url=https://raw.githubusercontent.com/zsxh1990/pr-genius/main/docs/badges/releases.json&label=releases&query=$.message&colorB=blue)](https://github.com/zsxh1990/pr-genius/releases)
[![Latest release](https://img.shields.io/github/v/release/zsxh1990/pr-genius)](https://github.com/zsxh1990/pr-genius/releases)
[![prgenius](https://img.shields.io/badge/dynamic/json?url=https://raw.githubusercontent.com/zsxh1990/pr-genius/main/docs/badges/prgenius_version.json&label=prgenius&query=$.message&colorB=blue)](./prgenius/README.md)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/zsxh1990/pr-genius.git
cd pr-genius
pip install -e prgenius/  # optional: install as package

# 提交前分析 (主命令)
python3 -m prgenius analyze "feat: add feature" --repo org/repo --body "Fixes #123"

# Agent PR Dojo (exit 0=pass, 1=fail)
python3 -m prgenius coach "feat: add feature" --repo org/repo --body "Fixes #123"

# 被拒 PR → lesson/anti-pattern draft
python3 -m prgenius harvest org/repo 123 --type lesson

# 查看仓库画像
python3 -m prgenius profile get Ikalus1988/MisakaNet

# Validate
python3 validate.py --strict
```

## 📖 Contributing

We welcome contributions — see [CONTRIBUTING.md](CONTRIBUTING.md) for the
quick-start guide. AI-assisted PRs are first-class citizens; please disclose
when you open a PR.

> 📝 **Read first**: [docs/BLOG.md](docs/BLOG.md) — a 300-line walkthrough
> of what this repo is, who uses it, how to install, and a real example
> case study (honcho#801 round-by-round). For the metrics roadmap see
> [docs/METRICS.md](docs/METRICS.md).

## 🤝 Community

- 📋 [Code of Conduct](CODE_OF_CONDUCT.md)
- 🔒 [Security Policy](SECURITY.md) (private advisory for security issues)
- 🐛 [Issue Tracker](../../issues)
- 💬 [Discussions](../../discussions) — until enabled, see [DISCUSSIONS.md](DISCUSSIONS.md)
- 📜 [Changelog](CHANGELOG.md)
- 🩷 [Maintaining & Releases](https://github.com/zsxh1990/pr-genius/releases)
- 🚫 [Blacklist](BLACKLIST.md) — repos we won't track

## 📊 Stats

| Metric | Value |
|---|---|
| Version | 1.2.0 |
| Repo profiles | 49 (含 Profile 仓画像 + stub + federation) |
| Case studies (.md) | 25 (含 rounds + close_decision 完整 schema) |
| Anti-patterns (.md) | 67 (含 15 ContribAI 闭 PR 反模式) |
| Anti-patterns (.json) | 59 |
| Success patterns (.md) | 38 |
| Success patterns (.json) | 73 |
| Review cases (.json) | 94 |
| Lessons (misakanet-50) | 11 |
| Total files | 228 .md |
| Validator checks | ✅ 0 errors |
| OKF compliance | ✅ v0.1 |
| Coach accuracy | 83.2% (226 cases, 28 repos) |

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

| Metric | Value |
|---|---|
| Version | 1.2.0 |
| Repo profiles | 49 |
| Case studies (.md) | 29 |
| Anti-patterns (.md) | 67 |
| Anti-patterns (.json) | 59 |
| Success patterns (.md) | 38 |
| Success patterns (.json) | 73 |
| Review cases (.json) | 94 |
| Lessons (misakanet-50) | 11 |
| Validator checks | ✅ 0 errors |
| OKF compliance | ✅ v0.1 |
| Coach accuracy | 83.2% (241 cases, 38 repos) |

## 35 个大仓速查

### 已提 PR 的仓

| 仓 | Star | 状态 | Profile |
|---|---|---|---|
| astral-sh/uv | 87k | ✅ #19685 | [astral-sh-uv/](./profiles/astral-sh-uv/index.md) |
| plastic-labs/honcho | 5.6k | 🟢 #801 | [plastic-labs-honcho/](./profiles/plastic-labs-honcho/index.md) |
| harbor-framework/harbor | 2.8k | 🟢 #2121 | [harbor-framework-harbor/](./profiles/harbor-framework-harbor/index.md) |
| punkpeye/fastmcp | 3.2k | 🟢 #282 | [punkpeye-fastmcp/](./profiles/punkpeye-fastmcp/index.md) |
| sourcebot-dev/sourcebot | 3.5k | 🟢 #1383 | [sourcebot-dev-sourcebot/](./profiles/sourcebot-dev-sourcebot/index.md) |
| future-agi/future-agi | 1.2k | 🟢 #778 | [future-agi-future-agi/](./profiles/future-agi-future-agi/index.md) |
| qdrant/mcp-server-qdrant | 1.4k | 🟢 #143 | [qdrant-mcp-server-qdrant/](./profiles/qdrant-mcp-server-qdrant/index.md) |
| e2b-dev/E2B | 12.7k | ❌ 教训 | [e2b-dev-e2b/](./profiles/e2b-dev-e2b/index.md) |
| agentic-community/mcp-gateway-registry | 765 | ✅ #1382 | [agentic-community-mcp-gateway-registry/](./profiles/agentic-community-mcp-gateway-registry/index.md) |
| mongodb-js/mongodb-mcp-server | 1.1k | 🟢 #1309 | [mongodb-js-mongodb-mcp-server/](./profiles/mongodb-js-mongodb-mcp-server/index.md) |
| NousResearch/hermes-agent | 208k | ⚪ 仅画像 | [NousResearch-hermes-agent/](./profiles/NousResearch-hermes-agent/index.md) |
| Ikalus1988/MisakaNet | — | 🟢 federation | [Ikalus1988-MisakaNet/](./profiles/Ikalus1988-MisakaNet/index.md) |

### 大仓画像（每日扩充数据源）

| 仓 | Star | 语言 | 合并率 | Profile |
|---|---|---|---|---|
| facebook/react | 247k | JS | 37% | [facebook-react/](./profiles/facebook-react/index.md) |
| huggingface/transformers | 163k | Python | 70% | [huggingface-transformers/](./profiles/huggingface-transformers/index.md) |
| microsoft/markitdown | 167k | Python | 7% | [microsoft-markitdown/](./profiles/microsoft-markitdown/index.md) |
| rust-lang/rust | 115k | Rust | 90% | [rust-lang-rust/](./profiles/rust-lang-rust/index.md) |
| kubernetes/kubernetes | 124k | Go | 77% | [kubernetes-kubernetes/](./profiles/kubernetes-kubernetes/index.md) |
| fastapi/fastapi | 101k | Python | 67% | [fastapi-fastapi/](./profiles/fastapi-fastapi/index.md) |
| tailwindlabs/tailwindcss | 96k | TS | 30% | [tailwindlabs-tailwindcss/](./profiles/tailwindlabs-tailwindcss/index.md) |
| grafana/grafana | 76k | TS | 67% | [grafana-grafana/](./profiles/grafana-grafana/index.md) |
| hashicorp/terraform | 49k | Go | 73% | [hashicorp-terraform/](./profiles/hashicorp-terraform/index.md) |
| cli/cli | 45k | Go | 50% | [cli-cli/](./profiles/cli-cli/index.md) |
| docker/compose | 38k | Go | 67% | [docker-compose/](./profiles/docker-compose/index.md) |
| openai/openai-python | 31k | Python | 30% | [openai-openai-python/](./profiles/openai-openai-python/index.md) |
| pydantic/pydantic | 28k | Python | 57% | [pydantic-pydantic/](./profiles/pydantic-pydantic/index.md) |
| chroma-core/chroma | 29k | Rust | 23% | [chroma-core-chroma/](./profiles/chroma-core-chroma/index.md) |
| qdrant/qdrant | 33k | Rust | 80% | [qdrant-qdrant/](./profiles/qdrant-qdrant/index.md) |
| encode/httpx | 15k | Python | 20% | [encode-httpx/](./profiles/encode-httpx/index.md) |
| actions/checkout | 8.5k | TS | 60% | [actions-checkout/](./profiles/actions-checkout/index.md) |
| microsoft/TypeScript | 103k | TS | 50% | [microsoft-TypeScript/](./profiles/microsoft-TypeScript/index.md) |
| langchain-ai/langchain | 141k | Python | 18% | [langchain-ai-langchain/](./profiles/langchain-ai-langchain/index.md) |
| vercel/next.js | 134k | TS | — | [vercel-next.js/](./profiles/vercel-next.js/index.md) |

## 📈 每日内容扩充 + Coach 契合度

### 每日扩充流程

每天 20:37 自动从 32 个大中仓采样 50 个 PR，按 7 个质量类别分类入库：

```bash
python3 scripts/daily_content_expand.py --limit 50
```

| 类别 | 目标 | 数据来源 |
|------|------|----------|
| merged_success | 15 | 已合并 PR（成功模式） |
| closed_rejected | 8 | 被关闭 PR（反模式） |
| closed_duplicate | 4 | 重复 PR |
| closed_already_done | 3 | 已有人做 |
| review_changes_requested | 5 | 要求修改 |
| review_approved_pending | 5 | 已批准待合并 |
| open_pending | 10 | 等待 review |

**仓库池：** pydantic, rust-lang, kubernetes, huggingface, react, httpx, uv, ruff, markitdown, tailwindcss, terraform, grafana, docker-compose, cli, openai-python, fastapi, chroma, qdrant, deno, TypeScript 等。

### Coach 契合度（预测 vs 实际）

```bash
python3 scripts/coach_cases.py
```

**121 个 case，20 个仓库，v3 最终结果：**

| 指标 | v1 | v2 | v3 |
|------|-----|-----|-----|
| ✅ 正确（精确匹配） | 38% | 44% | **45%** |
| 🟡 接近（差一级） | 37% | 36% | **42%** |
| ❌ 错误 | 25% | 21% | **13%** |
| **准确率** | 75% | 79% | **87%** |

**改进过程：**

1. **v1 → v2：** 添加 metadata-based 信号（is_small_pr, is_backport, is_dependency_update），解决 bot PR 信号全假问题。全假率 43% → 33%。
2. **v2 → v3：** 合并率 >0.8 的大仓取消"首次大仓提 PR"负面信号。高合并率 = 仓库接受外部 PR，不应惩罚。

**瓶颈：** 剩余 13% 错误主要是 evaluator 无法判断的上下文（内部 vs 外部贡献者、Issue 关联度、维护者个人偏好）。突破 90% 需要从启发式规则转向基于 case 的 few-shot 匹配。

**每日扩充仓库画像：** 35 个仓库（含 external_merge_rate、ai_policy、response_time_h_median 等结构化字段）。

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

## 🤖 MCP 集成（v1.3.0）

pr-genius 是 **evidence-backed PR contribution advisor MCP**：本地只读、证据驱动、OKF 合规，告诉 agent 哪些 PR **不该提**，不是代码 review 工具。

8 个 MCP tools（所有 read-only / non-destructive / idempotent）：

| Tool | 用途 |
|---|---|
| `analyze_pr` | 分析 PR 并生成结构化改进建议 + 三档风险 |
| `coach_pr` | Agent PR Dojo: pass/fail + checklist |
| `triage_pr` | Policy-aware PR 鉴别：pass / warn / reject / needs_preflight |
| `get_repo_profile` | 返回仓画像（17 个 agent_guidelines 字段） |
| `list_open_prs` | 列出所有 open PR Case Study |
| `get_case_study` | 返回单个 PR Case Study |
| `search_patterns` | 按关键词搜 anti-patterns + success-patterns |
| `schema_info` | 返回支持的 OKF schema 版本和枚举值 |

### Claude Code / Cursor / Cline 配置

加到 `~/.claude/mcp.json`（Claude Code）/ `~/.cursor/mcp.json`（Cursor）/ `cline_mcp_settings.json`（Cline）：

```json
{
  "mcpServers": {
    "pr-genius": {
      "command": "python",
      "args": ["-m", "prgenius", "mcp", "serve"]
    }
  }
}
```

Docker 部署：

```bash
docker run --rm -i ghcr.io/zsxh1990/pr-genius:1.3.0
```

### 3 个 Demo Prompts（v1.4.0 / Glama public 验收）

**Demo 1：Flask 大仓 PR 风险预审** （P0 验收门槛）

```
我准备给 pallets/flask 提一个 docs PR："docs: add installation instructions"
body: "Adds README section"

请用 pr-genius MCP 工具分析这个 PR，并告诉我:
1. 能不能直接提？
2. 如果不能，最低要补什么才能过 maintainer review？
```

预期输出（克莱恩 14:54 验收命令）：

```json
{
  "tier": "high_risk",
  "signals": {
    "negative": [
      {"key": "needs_preflight", "severity": "high",
       "description": "大仓 (67,000⭐) 无 pr-genius profile/policy",
       "generic_checks": [
         "confirm real bug (not feature request)",
         "link issue or maintainer request",
         "check CONTRIBUTING",
         "check duplicate PRs",
         "check archived status",
         "run tests + check CI"
       ]}
    ]
  },
  "checklist": [
    {"action": "preflight_confirm", "priority": "P0", ...},
    {"action": "preflight_link", "priority": "P0", ...},
    ...6 条 P0 preflight...
  ]
}
```

结论：docs-only PR 到 67k⭐ Flask = 默认 high_risk，**不要直接提**。

---

**Demo 2：MisakaNet policy triage**（已收录 P0 验收门槛）

```
我要给 Ikalus1988/MisakaNet 提 PR：
title: "fix: tiny typo"
body: "Fix typo in README"
diff_stat: "docs/faq.md | 3 ++-"

请用 pr-genius 跑 triage_pr，判断是否违反 maintainer policy。
```

预期输出：

```json
{
  "verdict": "pass",
  "policy_loaded": true,
  "violations": [],
  "recommended_action": "safe_to_review"
}
```

结论：clean PR 对 MisakaNet 直接 pass，可以提。

---

**Demo 3：uv repo profile 查询 + coach**（v1.3.0 已收录）

```
我要给 astral-sh/uv 提 PR：
title: "fix: typo in docs/quickstart.md"
body: ""

请用 pr-genius:
1. get_repo_profile astral-sh/uv — 给我维护者政策
2. coach_pr — 判断能不能提
```

预期输出：

```json
// get_repo_profile
{
  "repo": "astral-sh/uv",
  "agent_guidelines": {
    "ai_policy": "conditional",  // 欢迎但有规则
    "maintainer_vibe": "responsive",
    "require_signed_off": false,
    "external_merge_rate_30": 0.47
  }
}

// coach_pr
{
  "tier": "low_risk",
  "pass": true,
  "checklist": [
    {"action": "ci_passing", "priority": "P1", ...},
    {"action": "add_issue_link", "priority": "P2", ...}
  ]
}
```

结论：typo fix + maintainer-responsive = low_risk, 可以提。

---

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

### MisakaNet 一侧（计划中）

预计在 MisakaNet 主树加：
- `lessons/contrib/pr-strategy.md`（从本仓 8 仓画像蒸馏的策略总表）
- `agents/sun/federation/peers/pr-genius.md`（自动代理节点 联邦声明）
- `tools/federation.py`（双向查询脚本 v1）

### 受益表

| 受益方 | 受益方式 |
|---|---|
| External contributors | 提 PR 时 0ms 拉 yaml 控制流决策，不读 5k 散文 |
| MisakaNet federation | 多一个外部 PR 经验数据源（只读） |
| Downstream nodes | 同上，无需重新调研 8 仓 |

### 当前状态

- ✅ 根 `index.md` 加 `federates_with`（v0.3.0）
- ✅ 8 仓 repo profile 加 `misakanet_queries` + `misakanet_lessons`
- ✅ 本 README 加 Federation 节
- ✅ validate.py 不破（frontmatter / 死链 / 一致性全绿）

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
- ✅ **6 case 未迁移**（maintainer gate "别全仓大迁移"，保持 warning 状态；— 2026-07-04 v0.6.2 后已迁 0 个剩余，待 v0.7.0 BC 门面后重启）
- 触发：honcho + qdrant 2 真实样本证明 schema 缺陷不个别 → 升 v0.5.0

### 2026-07-02 v0.4.0（多轮交互日志 rounds）

- ✅ **ROUNDS_SCHEMA.md** 新增（PR Case Study `rounds` 字段 schema）
- ✅ **8/8 PR Case Study** 全加 `rounds` 字段（保留攻防过程，不只是结果）
- 总 rounds 计数：uv 2 / honcho 3 / harbor 1 / fastmcp 2 / sourcebot 1 / future-agi 3 / qdrant 1 / E2B 2
- 最终状态：1 merged (E2B #1413) / 1 closed-not-merged (uv #19685) / 6 open（含 1 stale）
- 触发：5 条升级建议第 3 条「多轮交互逻辑」+ 2026-07-02 23:25 GMT+8 拍板启动

### 2026-07-02 v0.3.0（MisakaNet 联邦声明）

- ✅ 根 `index.md` 加 `federates_with` 字段 + 2 个查询路径
- ✅ 8 仓 repo profile 加 `misakanet_queries` + `misakanet_lessons` + `federation_status`
- ✅ README 加 "MisakaNet Federation" 节（声明原则 + 字段规范 + 受益表）
- ✅ **不动 MisakaNet 主树 / 不迁移内容 / 不改目录结构**
- 触发：2026-07-02 23:07 GMT+8 拍板（federation gate）

### 2026-07-02 v0.2.0（maintainer 拍板升级 → Agent-first）

- ✅ **agent_guidelines 字段** 加入所有 8 仓 frontmatter（17 个 yaml 键）
- ✅ **AGENT_GUIDELINES_SCHEMA.md** 文档（schema 定义 + 调用示例）
- ✅ **BLACKLIST.md** 永久拉黑仓排雷指南（6 仓 + 2 归档方向）
- ✅ **anti-patterns/** 目录（4 条真实反模式：uv cargo fmt / Vite 秒拒 / honcho db 陷阱 / e2b not adding）
- ✅ **validate.py** OKF v0.1 校验脚本（frontmatter + 死链 + 一致性，3 check）
- ✅ README 加 frontmatter + 进阶结构章节
- 触发：5 条升级建议（结构化友好度 / 反模式 / 多轮日志 / 黑名单 / 校验脚本）前 4 条落地
- 下一步：阶段 3（多轮交互日志 rounds 字段）—— 拍板后启动

### 2026-07-01 v0.1.0（maintainer 拍板建立）

- 创建 OKF bundle 结构（17 文件 / 8 仓）
- 8 个仓 Profile + 8 个 PR Case Study 占位/完整
- OKF M1-M6 + S1-S4 全合规
- 增量规则：提新 PR → 自动补 PR Case Study