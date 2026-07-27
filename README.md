---
type: Knowledge Bundle
title: PR Genius — 提交前改进顾问
description: 大型开源项目 PR 知识库 + 提交前改进顾问，Agent 可读结构化数据
version: 1.3.0
created: 2026-07-01
updated: 2026-07-22
author: zsxh1990
conforms_to: OKF v0.1 (Sudhakaran88/okf-conformance) + agent_guidelines extension
---
mcp-name: io.github.zsxh1990/pr-genius

# PR Genius — 知道什么 PR 会被关的顾问

> **550+ 真实案例，帮你找到合并概率最大的提 PR 路径。**
> Clone → paste MCP config → ask "Should I open this PR to encode/httpx?"

<p align="center">
  <a href="https://glama.ai/mcp/servers"><img src="https://glama.ai/mcp/servers/zsxh1990/pr-genius/badge" alt="MCP Server on Glama"/></a>
  <a href="https://github.com/zsxh1990/pr-genius/blob/main/LICENSE"><img src="https://img.shields.io/github/license/zsxh1990/pr-genius?style=flat&color=blueviolet" alt="License"/></a>
  <a href="https://github.com/zsxh1990/pr-genius"><img src="https://img.shields.io/badge/cases-550+-blue?label=Cases" alt="Cases"/></a>
  <a href="https://github.com/zsxh1990/pr-genius"><img src="https://img.shields.io/badge/profiles-58-blue?label=Profiles" alt="Profiles"/></a>
</p>

---

## 🛡️ 为什么用 pr-genius

**pr-genius 不是"会写 PR 的 AI"，而是"知道什么 PR 会被关的顾问"。**

| 能力 | 大模型直接提 PR | 爬虫 Agent | pr-genius |
|------|----------------|-----------|-----------|
| 知识来源 | 训练数据 | 实时爬取 | 550+ 结构化 case studies |
| 仓库理解 | 通用知识 | stars/issues | 17 字段 agent_guidelines |
| 失败模式 | 不知道 | 不知道 | 68 anti-patterns |
| 维护者偏好 | 猜 | 看最近 PR | 结构化 policy |
| 合并概率 | 无法估算 | 无法估算 | 基于仓库合并率 |

**真实教训（只有被关过才知道）：**
- MisakaNet 不接受"破坏性 README 重写"（#491, #496）
- huggingface 要"内部处理"tokenizers 版本（#47434）
- encode/httpx 不接受外部贡献者（restricted interactions）
- Glama badge 是 awesome-mcp-servers 的必须项（#10393）

## 🚀 Quick Start

```bash
pip install prgenius-core

# 分析 PR
python3 -m prgenius analyze "feat: add feature" --repo org/repo --body "Fixes #123"

# Coach (pass/fail)
python3 -m prgenius coach "feat: add feature" --repo org/repo

# Triage (policy check)
python3 -m prgenius triage "docs: typo" --repo org/repo --diff-stat "docs/faq.md | 3 ++-"
```

## 🤖 MCP 配置

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

Docker: `docker run --rm -i ghcr.io/zsxh1990/pr-genius:1.3.0`

### 8 个 MCP Tools

| Tool | 用途 |
|------|------|
| `analyze_pr` | 合并概率 + 优化路径 + 三档风险 |
| `coach_pr` | go/no-go 决策（pass/fail） |
| `triage_pr` | 维护者政策检查（9 条规则） |
| `get_repo_profile` | 仓库画像（17 字段） |
| `list_open_prs` | open PR 列表 |
| `get_case_study` | PR 案例详情 |
| `search_patterns` | 反模式/成功模式搜索 |
| `schema_info` | OKF schema 版本 |

## 📊 数据规模

| 维度 | 数量 |
|------|------|
| Repo profiles | 58 |
| Case studies | 50+ |
| Anti-patterns | 68 |
| Success patterns | 40+ |
| Coach accuracy | 87% (257 cases, LORO validated) |
| 已覆盖仓库 | 35+ |

## 📖 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). AI-assisted PRs welcome.

## 🤝 Community

- 📋 [Code of Conduct](CODE_OF_CONDUCT.md)
- 🔒 [Security Policy](SECURITY.md)
- 🐛 [Issue Tracker](../../issues)
- 📜 [Changelog](CHANGELOG.md)

## 引用

```bibtex
@misc{pr-genius-2026,
  title  = {PR Genius — Evidence-backed PR Contribution Advisor},
  author = {zsxh1990},
  year   = {2026},
  url    = {https://github.com/zsxh1990/pr-genius}
}
```
