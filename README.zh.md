---
type: Knowledge Bundle (中文摘要)
title: Big-Repo PR 知识库
description: 大型开源项目 PR 模式 + 经验沉淀（中文导航）
version: 0.1.0
created: 2026-07-04
---
# Big-Repo PR 知识库 — 中文入口

本仓库记录在大型开源项目（star ≥ 1k）上提 PR 的模式与经验沉淀：
- **仓画像**：维护者风格、PR 方向、SOP、反模式
- **单 PR 案例**：合并 / close / amend 完整链路

格式遵循 [OKF v0.1](https://github.com/Sudhakaran88/okf-conformance) ——
纯 Markdown + YAML frontmatter，路径即 ID，零运行时依赖。

## 给中文 Agent 读者的读取顺序

1. **[docs/INDEX.md](docs/INDEX.md)** — 文件地图 + 推荐读取顺序
2. **[AGENT_GUIDELINES_SCHEMA.md](AGENT_GUIDELINES_SCHEMA.md)** — `agent_guidelines` 字段 schema
3. **[ROUNDS_SCHEMA.md](ROUNDS_SCHEMA.md)** — PR Case Study `rounds` 字段 schema (v0.5.0)
4. **[BLACKLIST.md](BLACKLIST.md)** — 永久拉黑仓清单
5. **[federation.yaml](federation.yaml)** — `federates_with` 跨仓联邦声明

## 中文读者速查

| 维度 | 数量 |
|---|---|
| 覆盖大仓（star ≥ 1k）| 11 个（含 NousResearch/hermes-agent） |
| 总 `.md` 文件 | ~270 |
| Repo Profile | 11 |
| PR Case Study | 11 |
| Anti-Pattern | 4 |
| Lessons (misakanet-50) | 10 |
| Validator Check | 4 (frontmatter / 死链 / 一致性 / rounds schema) |

## 中文版注意事项

`README.zh.md` 只是导航摘要。详细内容（仓画像、PR 案例、Schema
定义、Lessons）一律以英文原文为准——英文版本投入维护资源多、
schema 演进同步、跨 Agent 协作兼容性更好。

如果某个英文概念需要中文对照，请开 issue 或提 PR 到 README.zh.md
本节。

## 链接

- 仓库主页：https://github.com/zsxh1990/pr-genius
- 联邦上游：https://github.com/Ikalus1988/MisakaNet
- 贡献：`CONTRIBUTING.md`（英文版）
