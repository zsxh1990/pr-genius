---
type: Knowledge Bundle
title: Big-Repo PR 知识库
description: zsxh1990 已提 PR 的大仓（star ≥ 1k）PR 模式 + 经验沉淀，按 Google Open Knowledge Format (OKF v0.1) 组织
version: 0.3.0
created: 2026-07-01
updated: 2026-07-02
author: 太阳 (Misaka10004)
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

## 🎯 8 个目标仓（按 PR 价值排序）

| # | 仓 | Star | zsxh1990 PR 现状 | 文档 |
|---|---|---|---|---|
| 1 | [astral-sh/uv](https://github.com/astral-sh/uv) | 86.9k | ✅ #19685 closed（已合并可能）+ AI 友好 | [astral-sh-uv/index.md](./astral-sh-uv/index.md) |
| 2 | [plastic-labs/honcho](https://github.com/plastic-labs/honcho) | 5.6k | 🟢 #801 open，CodeRabbit 已审 | [plastic-labs-honcho/index.md](./plastic-labs-honcho/index.md) |
| 3 | [harbor-framework/harbor](https://github.com/harbor-framework/harbor) | 2.8k | 🟢 #2121 open，Vercel + Devin 已审 | [harbor-framework-harbor/index.md](./harbor-framework-harbor/index.md) |
| 4 | [punkpeye/fastmcp](https://github.com/punkpeye/fastmcp) | 3.2k | 🟢 #282 open，已修 Prettier | [punkpeye-fastmcp/index.md](./punkpeye-fastmcp/index.md) |
| 5 | [sourcebot-dev/sourcebot](https://github.com/sourcebot-dev/sourcebot) | 3.5k | 🟢 #1383 open，CodeRabbit 已审 | [sourcebot-dev-sourcebot/index.md](./sourcebot-dev-sourcebot/index.md) |
| 6 | [future-agi/future-agi](https://github.com/future-agi/future-agi) | 1.2k | 🟢 #778 open + 克莱恩亲自 check-in | [future-agi-future-agi/index.md](./future-agi-future-agi/index.md) |
| 7 | [qdrant/mcp-server-qdrant](https://github.com/qdrant/mcp-server-qdrant) | 1.4k | 🟢 #143 open 26 天（⚠️ stale） | [qdrant-mcp-server-qdrant/index.md](./qdrant-mcp-server-qdrant/index.md) |
| 8 | [e2b-dev/E2B](https://github.com/e2b-dev/E2B) | 12.7k | ❌ _ERROR_HANDLER 关 + 1413 已合并 | [e2b-dev-e2b/index.md](./e2b-dev-e2b/index.md) |

> 🟢 = open / ✅ = merged / ❌ = 关闭但有教训 / ⚠️ = 需关注  
> **OpenClaw 单独走自己的知识库**（已在 [openclaw-pr-knowledge/](../openclaw-pr-knowledge/README.md)），不计入本 bundle。

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

**太阳下次准备提 PR 时**：

1. 看 [astral-sh-uv/index.md](./astral-sh-uv/index.md) 确认目标仓是否已覆盖
2. 如果未覆盖：**先写 `Repo Profile` + 跑 5 切片采样 → 再写 PR 候选**
3. 提 PR 后：补 `PR Case Study`，记录 maintainer 反馈 + 教训
4. 跨仓模式（如"必须 v1 就带 proof"、"避免 security-boundary 改动"）：写 `Cross-Repo Pattern`

**克莱恩查经验时**：

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
- 触发：克莱恩 2026-07-02 23:07 GMT+8 拍板（federation gate）

### 2026-07-02 v0.2.0（Agent-first 升级）

- 详见 README.md v0.2.0 段

### 2026-07-01 v0.1.0（克莱恩拍板建立）

- 创建 OKF bundle 结构（8 仓子目录）
- 入口 `index.md` + 8 个仓 `index.md` 占位
- 完整示例：[astral-sh-uv/](./astral-sh-uv/index.md)
- 增量规则：提新 PR → 自动补 PR Case Study