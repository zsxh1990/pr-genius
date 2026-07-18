---
type: Knowledge Bundle
title: Big-Repo PR 知识库
description: zsxh1990 已提 PR 的大仓（star ≥ 1k）PR 模式 + 经验沉淀，按 Google Open Knowledge Format (OKF v0.1) 组织
version: 1.1.0
created: 2026-07-01
updated: 2026-07-09
author: zsxh1990
based_on:
  - openclaw-pr-knowledge/report.md
  - uv-pr-knowledge/report.md
conforms_to: OKF v0.1 (Sudhakaran88/okf-conformance)
federates_with:
  - misakanet/lessons/contrib/pr-strategy.md  # 查询路径（声明，不迁移）
  - misakanet/agents/sun/index.md              # 太阳节点身份
federation_mode: query-only  # 仅声明 + 查询，不同步内容
federated_at: 2026-07-02
---

# 大仓 PR 知识库

> zsxh1990 已提过 PR 的"大仓"（star ≥ 1k）PR 模式 + 经验沉淀。  
> 数据基础：50 个 PR 中 35 个 closed（17 merged / 20 closed-not-merged）+ 13 个 open。  
> 格式：[Google Open Knowledge Format v0.1](https://github.com/Sudhakaran88/okf-conformance) — 可移植、交叉链接的 markdown 知识包，AI agent 可直接读取。

---

## 🎯 目标仓 + 大仓画像

### 已提 PR 的仓

| # | 仓 | Star | 状态 | 文档 |
|---|---|---|---|---|
| 1 | [astral-sh/uv](https://github.com/astral-sh/uv) | 87k | ✅ #19685 | [astral-sh-uv/index.md](./astral-sh-uv/index.md) |
| 2 | [plastic-labs/honcho](https://github.com/plastic-labs/honcho) | 5.6k | 🟢 #801 | [plastic-labs-honcho/index.md](./plastic-labs-honcho/index.md) |
| 3 | [harbor-framework/harbor](https://github.com/harbor-framework/harbor) | 2.8k | 🟢 #2121 | [harbor-framework-harbor/index.md](./harbor-framework-harbor/index.md) |
| 4 | [punkpeye/fastmcp](https://github.com/punkpeye/fastmcp) | 3.2k | 🟢 #282 | [punkpeye-fastmcp/index.md](./punkpeye-fastmcp/index.md) |
| 5 | [sourcebot-dev/sourcebot](https://github.com/sourcebot-dev/sourcebot) | 3.5k | 🟢 #1383 | [sourcebot-dev-sourcebot/index.md](./sourcebot-dev-sourcebot/index.md) |
| 6 | [future-agi/future-agi](https://github.com/future-agi/future-agi) | 1.2k | 🟢 #778 | [future-agi-future-agi/index.md](./future-agi-future-agi/index.md) |
| 7 | [qdrant/mcp-server-qdrant](https://github.com/qdrant/mcp-server-qdrant) | 1.4k | 🟢 #143 | [qdrant-mcp-server-qdrant/index.md](./qdrant-mcp-server-qdrant/index.md) |
| 8 | [e2b-dev/E2B](https://github.com/e2b-dev/E2B) | 12.7k | ❌ 教训 | [e2b-dev-e2b/index.md](./e2b-dev-e2b/index.md) |
| 9 | [agentic-community/mcp-gateway-registry](https://github.com/agentic-community/mcp-gateway-registry) | 765 | ✅ #1382/#1383 | [agentic-community-mcp-gateway-registry/index.md](./agentic-community-mcp-gateway-registry/index.md) |
| 10 | [mongodb-js/mongodb-mcp-server](https://github.com/mongodb-js/mongodb-mcp-server) | 1.1k | 🟢 #1309 | [mongodb-js-mongodb-mcp-server/index.md](./mongodb-js-mongodb-mcp-server/index.md) |
| 11 | [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) | 208k | ⚪ 仅画像 | [NousResearch-hermes-agent/index.md](./NousResearch-hermes-agent/index.md) |
| 12 | [Ikalus1988/MisakaNet](https://github.com/Ikalus1988/MisakaNet) | — | 🟢 federation peer | [Ikalus1988-MisakaNet/index.md](./Ikalus1988-MisakaNet/index.md) |

### 大仓画像（交叉验证用）

| 仓 | Star | 文档 |
|---|---|---|
| langchain-ai/langchain | 141k | [langchain-ai-langchain/index.md](./langchain-ai-langchain/index.md) |
| yt-dlp/yt-dlp | 177k | [yt-dlp-yt-dlp/index.md](./yt-dlp-yt-dlp/index.md) |
| microsoft/markitdown | 164k | [microsoft-markitdown/index.md](./microsoft-markitdown/index.md) |
| langchain-ai/langgraph | 37k | [langchain-ai-langgraph/index.md](./langchain-ai-langgraph/index.md) |
| onyx-dot-app/onyx | 31k | [onyx-dot-app-onyx/index.md](./onyx-dot-app-onyx/index.md) |
| danny-avila/LibreChat | 40k | [danny-avila-LibreChat/index.md](./danny-avila-LibreChat/index.md) |
| goreleaser/nfpm | 2.6k | [goreleaser-nfpm/index.md](./goreleaser-nfpm/index.md) |
| python-jsonschema/jsonschema | 5k | [python-jsonschema-jsonschema/index.md](./python-jsonschema-jsonschema/index.md) |
| woodruffw/zizmor | 5.8k | [woodruffw-zizmor/index.md](./woodruffw-zizmor/index.md) |
| encode/httpx | 15k | [encode-httpx/index.md](./encode-httpx/index.md) |
| actions/checkout | 8.5k | [actions-checkout/index.md](./actions-checkout/index.md) |
| pydantic/pydantic | 28k | [pydantic-pydantic/index.md](./pydantic-pydantic/index.md) |
| tailwindlabs/tailwindcss | 96k | [tailwindlabs-tailwindcss/index.md](./tailwindlabs-tailwindcss/index.md) |
| huggingface/transformers | 163k | [huggingface-transformers/index.md](./huggingface-transformers/index.md) |
| hashicorp/terraform | 49k | [hashicorp-terraform/index.md](./hashicorp-terraform/index.md) |
| grafana/grafana | 76k | [grafana-grafana/index.md](./grafana-grafana/index.md) |
| kubernetes/kubernetes | 124k | [kubernetes-kubernetes/index.md](./kubernetes-kubernetes/index.md) |
| docker/compose | 38k | [docker-compose/index.md](./docker-compose/index.md) |
| cli/cli | 45k | [cli-cli/index.md](./cli-cli/index.md) |
| openai/openai-python | 31k | [openai-openai-python/index.md](./openai-openai-python/index.md) |
| rust-lang/rust | 115k | [rust-lang-rust/index.md](./rust-lang-rust/index.md) |
| facebook/react | 247k | [facebook-react/index.md](./facebook-react/index.md) |
| fastapi/fastapi | 101k | [fastapi-fastapi/index.md](./fastapi-fastapi/index.md) |
| chroma-core/chroma | 29k | [chroma-core-chroma/index.md](./chroma-core-chroma/index.md) |
| qdrant/qdrant | 33k | [qdrant-qdrant/index.md](./qdrant-qdrant/index.md) |

> 🟢 = open / ✅ = merged / ❌ = 关闭但有教训 / ⚠️ = 需关注
> **OpenClaw 单独走自己的知识库**（已在 [openclaw-pr-knowledge/](../openclaw-pr-knowledge/README.md)），不计入本 bundle。

---

## 🛠️ 工具

| 工具 | 用途 | 命令 |
|------|------|------|
| **analyze** | 提交前改进建议 | `python3 -m prgenius analyze "title" --repo org/repo --body "..."` |
| **coach** | Agent PR Dojo (exit 0/1) | `python3 -m prgenius coach "title" --repo org/repo --body "..."` |
| **harvest** | 被拒 PR → lesson/anti-pattern | `python3 scripts/harvest.py org/repo 123` |
| **eval** | 兼容旧命令 (三档) | `python3 -m prgenius eval "title" --repo org/repo` |
| **cross_validate** | 交叉验证 | `python3 scripts/cross_validate.py --all` |

---

## 📐 OKF 格式说明

本知识库严格遵循 [OKF v0.1 conformance](https://github.com/Sudhakaran88/okf-conformance/blob/main/CONFORMANCE.md) 规则：

### MUST（违反即不合规）

- **M1**: bundle = 目录 + .md 文件
- **M2**: 每个 .md 文件以 YAML frontmatter 起头（`---` 包裹）
- **M3**: 每个概念文件必须有非空 `type` 字段
- **M4**: 所有 `.md` 内部链接可解析到存在的文件
- **M5**: 文件路径即概念 ID
- **M6**: bundle 纯文本，无 SDK/网络/数据库依赖

### SHOULD（建议）

- **S1**: 根目录 `index.md` 作为入口
- **S2**: 文件夹逐级 `index.md` 索引子概念
- **S3**: 单文件单职责
- **S4**: 无孤立文件
- **S5**: `timestamp` 用 ISO-8601，`tags` 用 list

### 我们的 type 词汇表

| type | 用途 | 示例 |
|---|---|---|
| `Knowledge Bundle` | 入口 / 目录索引 | 本文件 |
| `Repo Profile` | 单仓 PR 模式分析 | `astral-sh-uv/index.md` |
| `PR Case Study` | 单个 PR 深读 + 教训 | `astral-sh-uv/pr-19685.md` |
| `Cross-Repo Pattern` | 跨仓通用模式 / SOP | 待创建 |
| `Risk Registry` | 敌视/危险社区清单 | 待创建 |

---

## 🧭 使用场景

**External contributor 准备提 PR 前**：

1. 看 [astral-sh-uv/index.md](./astral-sh-uv/index.md) 确认目标仓是否已覆盖
2. 如果未覆盖：**先写 `Repo Profile` + 跑 5 切片采样 → 再写 PR 候选**
3. 提 PR 后：补 `PR Case Study`，记录 maintainer 反馈 + 教训
4. 跨仓模式（如"必须 v1 就带 proof"、"避免 security-boundary 改动"）：写 `Cross-Repo Pattern`

**Maintenance reviewer / AI-assisted tool 调用时**：

1. 看 [astral-sh-uv/index.md](./astral-sh-uv/index.md) 拿"该仓 AI 友好度 + 5 目标 + SOP"
2. 看 [Cross-Repo Pattern](#)（待建）拿跨仓通用守则
3. 看 [Risk Registry](#)（待建）确认不要往敌视社区塞 PR

---

## 📚 关联资源

- [OpenClaw PR 知识库（已完成 200 PR 深读）](../openclaw-pr-knowledge/README.md)
- [uv PR 精简报告（5h 调研）](../uv-pr-knowledge/report.md)
- [OKF 规范](https://github.com/Sudhakaran88/okf-conformance)
- [MEMORY.md §5 个 OpenClaw fix PR 目标](../../MEMORY.md)

---

## 🗂️ 仓内导航（OKF S2/S4 自动链接）

> 由 [Sudhakaran88/okf-conformance](https://github.com/Sudhakaran88/okf-conformance) validator
> 强制要求：每个 concept 至少被一个链接引用（无孤儿），`index.md` 必须链所有 sibling concept。
> 2026-07-19 克莱恩拍板补链，4 个 MUST 错误 + 120 warnings → 0。

### 仓根核心文档

- [README.md](./README.md) · [README.zh.md](./README.zh.md) · [CHANGELOG.md](./CHANGELOG.md)
- [CONTRIBUTING.md](./CONTRIBUTING.md) · [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) · [SECURITY.md](./SECURITY.md)
- [DISCUSSIONS.md](./DISCUSSIONS.md) · [KNOWN_ISSUES.md](./KNOWN_ISSUES.md)
- [AGENT_GUIDELINES_SCHEMA.md](./AGENT_GUIDELINES_SCHEMA.md) · [ROUNDS_SCHEMA.md](./ROUNDS_SCHEMA.md) · [BLACKLIST.md](./BLACKLIST.md)

### 📐 docs/ — 文档与报告

- [BLOG.md](./docs/BLOG.md) · [index.md](./docs/index.md) · [METRICS.md](./docs/METRICS.md)
- [anti-pattern-analysis-methodology.md](./docs/anti-pattern-analysis-methodology.md) — PR 反模式分析 — 从被拒 PR 中提取可复用教训
- [coach-smoke-test-2026-07-15.md](./docs/coach-smoke-test-2026-07-15.md) — Coach Smoke Test — 5 Large Repos × 20 PRs
- [rejected-pr-retrospective.md](./docs/rejected-pr-retrospective.md) — 被拒 PR 复盘 — 18 个被拒 PR 的反模式分析
- [success-pr-retrospective.md](./docs/success-pr-retrospective.md) — 成功 PR 复盘 — 21 个已合并 PR 的成功模式分析

### ⚠️ anti-patterns/ — 反模式库（46 项）

> [README 索引](./anti-patterns/README.md) · 主条目按反模式 slug 组织。

**AI/Vibe 编码反模式**

- [ai-generated-content.md](./anti-patterns/ai-generated-content.md)
- [anthropics-anthropic-sdk-python-1757.json](./anti-patterns/anthropics-anthropic-sdk-python-1757.json)
- [missing-issue-reference.md](./anti-patterns/missing-issue-reference.md)
- [nousresearch-comp-desktop.md](./anti-patterns/nousresearch-comp-desktop.md)
- [nousresearch-cron-risk.md](./anti-patterns/nousresearch-cron-risk.md)
- [nousresearch-duplicate-pr.md](./anti-patterns/nousresearch-duplicate-pr.md)
- [nousresearch-provider-specific.md](./anti-patterns/nousresearch-provider-specific.md)
- [nousresearch-tool-specific.md](./anti-patterns/nousresearch-tool-specific.md)
- [nousresearch-sweeper-blast-broad.md](./anti-patterns/nousresearch-sweeper-blast-broad.md)
- [nousresearch-sweeper-blast-contained.md](./anti-patterns/nousresearch-sweeper-blast-contained.md)
- [nousresearch-sweeper-blast-moderate.md](./anti-patterns/nousresearch-sweeper-blast-moderate.md)
- [nousresearch-sweeper-implemented-on-main.md](./anti-patterns/nousresearch-sweeper-implemented-on-main.md)
- [nousresearch-sweeper-not-planned.md](./anti-patterns/nousresearch-sweeper-not-planned.md)
- [nousresearch-sweeper-risk-caching.md](./anti-patterns/nousresearch-sweeper-risk-caching.md)
- [nousresearch-sweeper-risk-message-delivery.md](./anti-patterns/nousresearch-sweeper-risk-message-delivery.md)

**代码/工程反模式**

- [breaking-change-no-compat.md](./anti-patterns/breaking-change-no-compat.md)
- [cosmetic-no-user-pain.md](./anti-patterns/cosmetic-no-user-pain.md)
- [duplicate-pr-same-author.md](./anti-patterns/duplicate-pr-same-author.md)
- [fork-main-sync-upstream.md](./anti-patterns/fork-main-sync-upstream.md)
- [fork-pr-ci-permission-error.md](./anti-patterns/fork-pr-ci-permission-error.md)
- [github-pr-diff-caching.md](./anti-patterns/github-pr-diff-caching.md)
- [honcho-default-db-module-trap.md](./anti-patterns/honcho-default-db-module-trap.md)
- [low-value-contribution.md](./anti-patterns/low-value-contribution.md)
- [stale-pr-far-behind-main.md](./anti-patterns/stale-pr-far-behind-main.md)
- [superseded-by-maintainer.md](./anti-patterns/superseded-by-maintainer.md)
- [upstream-already-implementing.md](./anti-patterns/upstream-already-implementing.md)
- [uv-cargo-fmt-required.md](./anti-patterns/uv-cargo-fmt-required.md)

**OpenClaw 专项反模式（25 项，从 PR #93310 复盘提取）**

- [nousresearch-risk-platform-windows.md](./anti-patterns/nousresearch-risk-platform-windows.md)
- [nousresearch-risk-security-boundary.md](./anti-patterns/nousresearch-risk-security-boundary.md)
- [nousresearch-risk-session-state.md](./anti-patterns/nousresearch-risk-session-state.md)
- [openclaw-auth-provider-risk.md](./anti-patterns/openclaw-auth-provider-risk.md)
- [openclaw-availability-risk.md](./anti-patterns/openclaw-availability-risk.md)
- [openclaw-compatibility-risk.md](./anti-patterns/openclaw-compatibility-risk.md)
- [openclaw-duplicate-pr.md](./anti-patterns/openclaw-duplicate-pr.md)
- [openclaw-merge-risk-blast-contained.md](./anti-patterns/openclaw-merge-risk-blast-contained.md)
- [openclaw-merge-risk-caching.md](./anti-patterns/openclaw-merge-risk-caching.md)
- [openclaw-message-delivery-risk.md](./anti-patterns/openclaw-message-delivery-risk.md)
- [openclaw-missing-proof.md](./anti-patterns/openclaw-missing-proof.md)
- [openclaw-module-refactored.md](./anti-patterns/openclaw-module-refactored.md)
- [openclaw-needs-real-behavior-proof.md](./anti-patterns/openclaw-needs-real-behavior-proof.md)
- [openclaw-platform-windows.md](./anti-patterns/openclaw-platform-windows.md)
- [openclaw-refactor-risk.md](./anti-patterns/openclaw-refactor-risk.md)
- [openclaw-security-boundary-risk.md](./anti-patterns/openclaw-security-boundary-risk.md)
- [openclaw-session-state-risk.md](./anti-patterns/openclaw-session-state-risk.md)
- [openclaw-stale-pr.md](./anti-patterns/openclaw-stale-pr.md)
- [openclaw-stale-with-proof.md](./anti-patterns/openclaw-stale-with-proof.md)
- [openclaw-sweeper-not-planned.md](./anti-patterns/openclaw-sweeper-not-planned.md)
- [openclaw-triage-needs-pr-context.md](./anti-patterns/openclaw-triage-needs-pr-context.md)
- [openclaw-waiting-on-author.md](./anti-patterns/openclaw-waiting-on-author.md)

**真实 PR 反模式案例（按仓组织）**

- [awesome-mcp-servers-glama-badge-required.md](./anti-patterns/awesome-mcp-servers-glama-badge-required.md) — awesome-mcp-servers 仓 Glama score badge requirement
- [vite-sapphi-red-instant-close.md](./anti-patterns/vite-sapphi-red-instant-close.md) — Vite 仓 sapphi-red 秒拒反 AI PR
- [e2b-feature-not-adding-canned-response.md](./anti-patterns/e2b-feature-not-adding-canned-response.md) — E2B 仓"we're not adding this feature"反模式
- [trusted-publisher-oidc-insufficient.md](./anti-patterns/trusted-publisher-oidc-insufficient.md) — PyPI Trusted Publisher OIDC 权限缺失
- [actions-checkout-2509.json](./anti-patterns/actions-checkout-2509.json)
- [actions-checkout-2517.json](./anti-patterns/actions-checkout-2517.json)
- [actions-checkout-2520.json](./anti-patterns/actions-checkout-2520.json)
- [astral-sh-uv-20487.json](./anti-patterns/astral-sh-uv-20487.json)
- [chroma-core-chroma-7434.json](./anti-patterns/chroma-core-chroma-7434.json)
- [docker-compose-13930.json](./anti-patterns/docker-compose-13930.json)
- [docker-compose-13932.json](./anti-patterns/docker-compose-13932.json)
- [encode-httpx-3765.json](./anti-patterns/encode-httpx-3765.json)
- [facebook-react-37042.json](./anti-patterns/facebook-react-37042.json)
- [goharbor-harbor-23566.json](./anti-patterns/goharbor-harbor-23566.json)
- [goharbor-harbor-23567.json](./anti-patterns/goharbor-harbor-23567.json)
- [golang-go-80407.json](./anti-patterns/golang-go-80407.json)
- [grafana-grafana-128644.json](./anti-patterns/grafana-grafana-128644.json)
- [grafana-grafana-128650.json](./anti-patterns/grafana-grafana-128650.json)
- [hashicorp-terraform-38874.json](./anti-patterns/hashicorp-terraform-38874.json)
- [hashicorp-terraform-38886.json](./anti-patterns/hashicorp-terraform-38886.json)
- [hashicorp-terraform-38889.json](./anti-patterns/hashicorp-terraform-38889.json)
- [microsoft-TypeScript-63622~63638.json](./anti-patterns/microsoft-TypeScript-63622.json)（共 9 条）
- [microsoft-markitdown-2200.json](./anti-patterns/microsoft-markitdown-2200.json)
- [pydantic-pydantic-13439~13455.json](./anti-patterns/pydantic-pydantic-13439.json)（共 7 条）
- [tailwindlabs-tailwindcss-20323~20342.json](./anti-patterns/tailwindlabs-tailwindcss-20323.json)（共 7 条）

### ✅ success-patterns/ — 成功模式库（31 项）

> [README 索引](./success-patterns/README.md) · 主条目按成功模式 slug 组织。

**MisakaNet 模式（4 项，从 PR #248/#244 合并提取）**

- [misakanet-frontmatter-normalization.md](./success-patterns/misakanet-frontmatter-normalization.md) — frontmatter 规范化模板
- [misakanet-lesson-contribution.md](./success-patterns/misakanet-lesson-contribution.md) — lesson 贡献 SOP
- [misakanet-mcp-quickstart.md](./success-patterns/misakanet-mcp-quickstart.md) — MCP quickstart 模式
- [misakanet-reputation-system.md](./success-patterns/misakanet-reputation-system.md) — sigmoid cap 反刷分

**OpenClaw 模式（17 项，从 PR #93310 复盘提取）**

- [openclaw-app-fix.md](./success-patterns/openclaw-app-fix.md)
- [openclaw-channel-fix.md](./success-patterns/openclaw-channel-fix.md)
- [openclaw-dependency-update.md](./success-patterns/openclaw-dependency-update.md)
- [openclaw-docs-fix.md](./success-patterns/openclaw-docs-fix.md)
- [openclaw-extension-fix.md](./success-patterns/openclaw-extension-fix.md)
- [openclaw-maintainer-pr.md](./success-patterns/openclaw-maintainer-pr.md)
- [openclaw-p0-priority-fix.md](./success-patterns/openclaw-p0-priority-fix.md)
- [openclaw-p1-priority-fix.md](./success-patterns/openclaw-p1-priority-fix.md)
- [openclaw-p2-priority-fix.md](./success-patterns/openclaw-p2-priority-fix.md)
- [openclaw-plugin-fix.md](./success-patterns/openclaw-plugin-fix.md)
- [openclaw-proof-sufficient.md](./success-patterns/openclaw-proof-sufficient.md)
- [openclaw-scripts-fix.md](./success-patterns/openclaw-scripts-fix.md)
- [openclaw-small-focused-fix.md](./success-patterns/openclaw-small-focused-fix.md)

**NousResearch 模式（12 项）**

- [nourresearch-comp-desktop-fix.md](./success-patterns/nourresearch-comp-desktop-fix.md)
- [nousresearch-area-fix.md](./success-patterns/nousresearch-area-fix.md)
- [nousresearch-bug-fix.md](./success-patterns/nousresearch-bug-fix.md)
- [nousresearch-comp-agent-fix.md](./success-patterns/nousresearch-comp-agent-fix.md)
- [nousresearch-comp-cli-fix.md](./success-patterns/nousresearch-comp-cli-fix.md)
- [nousresearch-comp-gateway-fix.md](./success-patterns/nousresearch-comp-gateway-fix.md)
- [nousresearch-dependency-update.md](./success-patterns/nousresearch-dependency-update.md)
- [nousresearch-p1-priority-fix.md](./success-patterns/nousresearch-p1-priority-fix.md)
- [nousresearch-p2-priority-fix.md](./success-patterns/nousresearch-p2-priority-fix.md)
- [nousresearch-p3-priority-fix.md](./success-patterns/nousresearch-p3-priority-fix.md)
- [nousresearch-platform-fix.md](./success-patterns/nousresearch-platform-fix.md)
- [nousresearch-platform-telegram-fix.md](./success-patterns/nousresearch-platform-telegram-fix.md)
- [nousresearch-refactor.md](./success-patterns/nousresearch-refactor.md)
- [nousresearch-type-bug-fix.md](./success-patterns/nousresearch-type-bug-fix.md)
- [nousresearch-type-refactor.md](./success-patterns/nousresearch-type-refactor.md)

**通用模式**

- [agentclaimguard-langchain-middleware.md](./success-patterns/agentclaimguard-langchain-middleware.md)
- [bilig-docs-relative-paths.md](./success-patterns/bilig-docs-relative-paths.md)
- [cortex-memory-tiers-guide.md](./success-patterns/cortex-memory-tiers-guide.md)
- [evotown-timezone-fix.md](./success-patterns/evotown-timezone-fix.md)
- [llmservingsim-docs-overrides.md](./success-patterns/llmservingsim-docs-overrides.md)
- [mcp-gateway-secret-uri-safe.md](./success-patterns/mcp-gateway-secret-uri-safe.md)

### 📚 misakanet-50/ — MisakaNet 经验蒸馏（12 项）

> [README](./misakanet-50/README.md) · [SCORING](./misakanet-50/SCORING.md) · 4 维度源可信度评分 v0.1

### 🛡️ docs/policies/ — 维护者政策（v1.2.0 新增）

> 维护者政策 memory：从实际 PR 拒绝记录提炼的 hard/soft 规则，供 triage command 自动筛 PR。

- [Ikalus1988-MisakaNet.md](./docs/policies/Ikalus1988-MisakaNet.md) — MisakaNet 9 条 hard/soft 规则，锚定 PR #491-#497

- [lesson-01-vibe-coding-team-out-of-control.md](./misakanet-50/lesson-01-vibe-coding-team-out-of-control.md) — Vibe Coding Team Out of Control
- [lesson-02-ai-code-review-flow.md](./misakanet-50/lesson-02-ai-code-review-flow.md) — AI Code Review: Skip vs Read
- [lesson-03-ai-monthly-cost-baseline.md](./misakanet-50/lesson-03-ai-monthly-cost-baseline.md) — AI 月度成本基线（中国，2026）
- [lesson-04-ai-api-relay-risks.md](./misakanet-50/lesson-04-ai-api-relay-risks.md) — AI 中转站风险
- [lesson-05-vless-reality-blocked-detection.md](./misakanet-50/lesson-05-vless-reality-blocked-detection.md) — vless+xhttp+reality 封锁检测
- [lesson-06-git-push-credential-helper-403.md](./misakanet-50/lesson-06-git-push-credential-helper-403.md) — Git Push PAT 选错
- [lesson-07-uv-venv-seed-fix-no-pip.md](./misakanet-50/lesson-07-uv-venv-seed-fix-no-pip.md) — WSL Python venv 缺 pip — uv seed 修复
- [lesson-08-pip-https-proxy-clash.md](./misakanet-50/lesson-08-pip-https-proxy-clash.md) — WSL pip HTTPS 走 Clash
- [lesson-09-v2ex-api-show-endpoint-unstable.md](./misakanet-50/lesson-09-v2ex-api-show-endpoint-unstable.md) — V2EX API 不稳 — 改 r.jina.ai
- [lesson-10-agent-reach-doctor-baseline.md](./misakanet-50/lesson-10-agent-reach-doctor-baseline.md) — Agent-Reach doctor 基线
- [lesson-11-mcp-typo-pool-x3-merged.md](./misakanet-50/lesson-11-mcp-typo-pool-x3-merged.md) — MCP Gateway x3 Mermaid 占位池

### 🎯 MisakaNet PR 案例（5 项）

> [Ikalus1988-MisakaNet/ 仓 Profile](./Ikalus1988-MisakaNet/index.md)

- [pr-439-pep668-lesson.md](./Ikalus1988-MisakaNet/pr-439-pep668-lesson.md) — MisakaNet #439 — PEP 668 lesson
- [pr-440-frontmatter-tests.md](./Ikalus1988-MisakaNet/pr-440-frontmatter-tests.md) — MisakaNet #440 — frontmatter 边界测试
- [pr-441-smart-fallback.md](./Ikalus1988-MisakaNet/pr-441-smart-fallback.md) — MisakaNet #441 — smart fallback with telemetry
- [pr-452-frontmatter-batch.md](./Ikalus1988-MisakaNet/pr-452-frontmatter-batch.md) — MisakaNet #452 — 20 bare JSON → YAML
- [pr-474-fanuc-lessons.md](./Ikalus1988-MisakaNet/pr-474-fanuc-lessons.md) — MisakaNet #474 — 7 FANUC 机器人课程

### 🛠️ skill/ — 内部脚本与工具

- [README.md](./skill/README.md)
- [skill.md](./skill/skill.md)

### 📦 其他孤立文档

- [KNOWN_ISSUES.md](./KNOWN_ISSUES.md) — Known Issues 跟踪表
- [ag2ai-ag2/RISK.md](./ag2ai-ag2/RISK.md) — ag2ai/ag2 风险决策
- [datalayer-jupyter-mcp-server/pr-266-configurable-timeout.md](./datalayer-jupyter-mcp-server/pr-266-configurable-timeout.md) — jupyter-mcp-server #266
- [samanhappy-mcphub/pr-987-rce-fix.md](./samanhappy-mcphub/pr-987-rce-fix.md) — mcphub #987 — proxychains4 RCE fix
- [yorgai-ORG2/pr-350-linux-downloads.md](./yorgai-ORG2/pr-350-linux-downloads.md) — ORG2 #350 — Linux download links

### 📜 归档脚本

- [archive/scripts/pr-genius-landscape-search/README.md](./archive/scripts/pr-genius-landscape-search/README.md) — PR 同类仓调研脚本集（5 个 search/fetch 脚本）

---

## 📝 更新日志

### 2026-07-02 v0.3.0（联邦声明）

- ✅ 根 index.md 加 `federates_with` 字段 + 声明 2 个查询路径
- ✅ 8 仓 repo profile 加 `misakanet_queries` 字段
- ✅ README 加 "MisakaNet Federation" 节
- ✅ **不改 MisakaNet 主树 / 不迁移内容 / 不改目录结构**
- 触发：2026-07-02 23:07 GMT+8 拍板（federation gate）

### 2026-07-02 v0.2.0（Agent-first 升级）

- 详见 README.md v0.2.0 段

### 2026-07-01 v0.1.0（maintainer 拍板建立）

- 创建 OKF bundle 结构（8 仓子目录）
- 入口 `index.md` + 8 个仓 `index.md` 占位
- 完整示例：[astral-sh-uv/](./astral-sh-uv/index.md)
- 增量规则：提新 PR → 自动补 PR Case Study