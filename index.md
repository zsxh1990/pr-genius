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