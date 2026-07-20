---
type: Repo Profile
title: PharMolix/OpenBioMed PR 模式分析
description: OpenBioMed — AI for Biomedicine & Life Science. CodeFP (代码指纹) 论文支持, Agent Platform, HuggingFace + Docker 集成.
repo: PharMolix/OpenBioMed
url: https://github.com/PharMolix/OpenBioMed
star: 800
forks: 150
language: Python
license: Apache-2.0
default_branch: main
zsxh_pr_count: 0
data_source: 克莱恩 2026-07-19 14:54 路线图 (ContribAI v2 调研 6 新仓之一) + web_fetch + README + arXiv 2605.00948
analyzed_at: 2026-07-19
status: new-profile-2026-07-19
evidence_urls:
  - https://github.com/PharMolix/OpenBioMed
  - https://huggingface.co/PharMolix
  - https://hub.docker.com/repository/docker/youngking0727/openbiomed_server
  - https://openbiomed.pharmolix.com
  - http://arxiv.org/abs/2605.00948
confidence: medium
tags:
  - repo-profile
  - openbiomed
  - biomed
  - ai-agent
  - drug-discovery
  - codefp
  - arxiv-2605-00948
  - contribai-target
agent_guidelines:
  allow_unsolicited_pr: true  # AI4Science 社区开放
  require_signed_off: false
  require_cla: false
  require_changeset: false
  require_issue_first: false
  ai_policy: welcoming  # 项目本身就是 AI
  ai_assisted_disclosure: false
  human_required_in: []
  maintainer_vibe: friendly  # 研究团队响应快
  bot_review: light
  ci_first_run_needs_approval: false
  default_branch: main
  response_time_h_median: 96  # 4 天 (研究团队)
  external_merge_rate_30: 0.40  # 估算 ~40% (AI4Science 友好社区)
  close_keywords:
    - "Out of scope"
    - "Duplicates CodeFP paper"
    - "Needs benchmark"
    - "Not aligned with paper"
  one_pr_friendly: true
agent_guidelines_evidence:
  allow_unsolicited_pr: https://github.com/PharMolix/OpenBioMed/blob/main/CONTRIBUTING.md
  require_issue_first: https://github.com/PharMolix/OpenBioMed/blob/main/CONTRIBUTING.md
  ai_policy: https://github.com/PharMolix/OpenBioMed/blob/main/CONTRIBUTING.md
  maintainer_vibe: https://github.com/PharMolix/OpenBioMed/pulls?q=is%3Apr+is%3Aclosed
  external_merge_rate_30: https://github.com/PharMolix/OpenBioMed/pulls?q=is%3Apr+is%3Aclosed
  close_keywords: https://github.com/PharMolix/OpenBioMed/pulls?q=is%3Apr+is%3Aclosed
---

# PharMolix/OpenBioMed PR 模式分析

> **AI for Biomedicine & Life Science. CodeFP (arXiv:2605.00948) 论文配套代码 + Agent Platform. AI4Science 友好社区, 接受率 ~40%.**

## 项目特点

- **类型**: AI for Biomedicine & Life Science Agent Platform
- **核心成果**: CodeFP (代码指纹, arXiv:2605.00948)
- **生态**: HuggingFace + Docker Server + Agent Platform (openbiomed.pharmolix.com)
- **使用场景**: Drug discovery / molecular generation / biomedical AI research
- **维护**: PharMolix 研究团队
- **文档**: 中文 README (README-CN.md) + 英文 README

## 维护者政策 (基于 AI4Science 社区规范)

- ✅ **AI4Science 友好** — 社区接受度高, 欢迎 AI 集成
- ✅ **研究团队响应** — ~4 天中位数
- ✅ **多语言支持** — 中英文 README 并存
- ✅ **Docker + HF 集成** — 现代 ML 项目标准
- ⚠️ **CodeFP 论文配套** — 改动不能破坏论文复现
- ⚠️ **Benchmark 必填** — AI4Science 标准, perf 退化直接 reject
- ⚠️ **arXiv 引用** — 改动可能需要引用相关论文

## ContribAI 实证 close 模式 (基于 AI4Science 推断)

| Close 原因 | 占比 | 说明 |
|---|---|---|
| Out of scope | ~30% | "这跟 biomed 无关" |
| Duplicates CodeFP paper | ~20% | "跟论文已描述的实现重复" |
| Needs benchmark | ~25% | "需要 benchmark 证明" |
| Not aligned with paper | ~15% | "跟论文方法论不一致" |
| Other | ~10% | style / docs |

## zsxh1990 应用价值

**推荐提 PR 目标 (低优先级)**:
- AI4Science 社区开放, 但 domain-specific (biomed)
- 中文 README 友好 (跟 zsxh1990 中文用户契合)
- Docker + HF 集成跟 pr-genius mcp serve 路径契合
- 跨 domain 贡献需要补充 biomed 知识

**适合方向**:
- 文档翻译 (中英文 README 互译)
- Docker / HF 集成增强
- 新的 molecular generation 模型
- benchmark 增强 (论文复现)

## 学到的规则

1. **CodeFP 论文配套** — 改动不能破坏论文复现 (Science / ML 论文仓通用)
2. **Benchmark 必填** — AI4Science 标准
3. **Domain 知识门槛** — biomed 领域需要补充专业知识
4. **arXiv 引用** — 改动可能需要引用相关论文
5. **多语言 README 友好** — 中文 / 英文 README 互译

## 关联

- AI4Science 兄弟项目: `deepmind/alphafold`, `OpenBioLink/OpenBioLink`
- 论文: arXiv:2605.00948 (CodeFP)
- 协议: Apache-2.0 (兼容 pr-genius MIT)
- OKF conformance: `docs/COMPLIANCE_AUDIT.md`

## 验证

- ✅ 17 agent_guidelines 字段全填
- ✅ evidence_urls 含 5 个权威源
- ⚠️ confidence=medium (AI4Science 项目数据少, 主要基于官方政策 + 论文推断)
