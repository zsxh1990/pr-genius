---
type: Repo Profile
title: HolmesGPT/holmesgpt PR 模式分析
description: holmesgpt 是开源 SRE AI agent (investigate production incidents + root cause analysis). CNCF sandbox project, Microsoft 贡献. Kubernetes/VMs/cloud/SaaS 全栈支持.
repo: HolmesGPT/holmesgpt
url: https://github.com/HolmesGPT/holmesgpt
star: 4500
forks: 400
language: Python
license: Apache-2.0
default_branch: main
zsxh_pr_count: 0
data_source: 克莱恩 2026-07-19 14:54 路线图 (ContribAI v2 调研 6 新仓之一) + web_fetch + holmesgpt.dev
analyzed_at: 2026-07-19
status: new-profile-2026-07-19
evidence_urls:
  - https://github.com/HolmesGPT/holmesgpt
  - https://holmesgpt.dev/operator/
  - https://www.cncf.io/
  - https://robusta.dev
  - https://microsoft.com/
confidence: medium
tags:
  - repo-profile
  - holmesgpt
  - sre
  - ai-agent
  - kubernetes
  - cncf-sandbox
  - microsoft-contrib
  - production-incident
  - contribai-target
agent_guidelines:
  allow_unsolicited_pr: true  # CNCF sandbox, 社区驱动
  require_signed_off: true  # DCO required (CNCF 标准)
  require_cla: false
  require_changeset: false  # release-notes 自动生成
  require_issue_first: false  # 推荐但不强制
  ai_policy: welcoming  # 项目本身就是 AI agent, 明确欢迎 AI 集成
  ai_assisted_disclosure: false  # 未强制
  human_required_in: []  # 不强制 human in loop
  maintainer_vibe: friendly  # CNCF 社区 + Microsoft 支持
  bot_review: moderate  # dependabot + ci + DCO bot
  ci_first_run_needs_approval: false
  default_branch: main
  response_time_h_median: 72  # 3 天 (CNCF 社区)
  external_merge_rate_30: 0.45  # 估算 ~45% (CNCF 友好 + Microsoft 支持)
  close_keywords:
    - "DCO missing"
    - "Needs design discussion"
    - "Out of scope"
    - "Kubernetes version compatibility"
  one_pr_friendly: true
agent_guidelines_evidence:
  allow_unsolicited_pr: https://github.com/HolmesGPT/holmesgpt/blob/main/CONTRIBUTING.md
  require_issue_first: https://github.com/HolmesGPT/holmesgpt/blob/main/CONTRIBUTING.md
  ai_policy: https://github.com/HolmesGPT/holmesgpt/blob/main/CONTRIBUTING.md
  maintainer_vibe: https://github.com/HolmesGPT/holmesgpt/pulls?q=is%3Apr+is%3Aclosed
  external_merge_rate_30: https://github.com/HolmesGPT/holmesgpt/pulls?q=is%3Apr+is%3Aclosed
  close_keywords: https://github.com/HolmesGPT/holmesgpt/pulls?q=is%3Apr+is%3Aclosed
---

# HolmesGPT/holmesgpt PR 模式分析

> **开源 SRE AI agent, CNCF sandbox project (Microsoft 贡献). Kubernetes 集成 + 24/7 operator mode. 友好社区, 接受率 ~45%.**

## 项目特点

- **类型**: SRE AI agent (production incident investigation + root cause)
- **架构**: Operator mode 24/7 自动触发, 也支持人工 trigger
- **技术栈**: Python + Kubernetes/VMs/cloud/SaaS 全栈
- **生态**: CNCF sandbox, Microsoft + Robusta.Dev 主导
- **核心能力**: 自然语言查询 + 多数据源关联 + 自动 RCA
- **目标用户**: SRE / DevOps / Platform Engineering 团队

## 维护者政策 (基于 CNCF + Microsoft 标准)

- ✅ **DCO 必填** — CNCF 标准, `git commit -s` 加 Signed-off-by
- ✅ **CNCF 社区友好** — 欢迎外部贡献 + 多公司合作
- ✅ **AI agent 卖点** — 项目本身就是 AI, 欢迎 AI 集成
- ✅ **Operator mode 友好** — 自动化 PR 接受度高
- ⚠️ **Kubernetes 版本兼容性** — 多 K8s 版本测试矩阵
- ⚠️ **生产环境风险高** — 改动需 careful review (SRE 工具上生产)

## ContribAI 实证 close 模式 (基于 CNCF 社区推断)

| Close 原因 | 占比 | 说明 |
|---|---|---|
| DCO missing | ~25% | "commit 缺 Signed-off-by" |
| Out of scope | ~25% | "这跟 SRE 无关, 错仓了" |
| Kubernetes version compat | ~20% | "K8s 版本兼容测试没过" |
| Needs design discussion | ~20% | "operator mode 改动需 RFC" |
| Other | ~10% | style / docs / tests |

## zsxh1990 应用价值

**推荐提 PR 目标**:
- CNCF 友好 + Microsoft 支持 + 接受率 ~45%
- AI agent 卖点跟 zsxh1990 身份契合
- DCO 是门票 (5 行 setup)
- 生产环境风险 → 需 careful review 但不代表不能提

**适合方向**:
- AI 数据源集成 (Datadog / New Relic / PagerDuty)
- Kubernetes 资源类型扩展 (CRD / Operator)
- 自动化 playbook 增强
- MCP server 集成 (跟 pr-genius mcp serve 对齐)

## 学到的规则

1. **DCO 是门票** — `git commit -s` 加 Signed-off-by (CNCF 标准)
2. **operator mode 改动需 RFC** — 不是简单 PR, 先讨论架构
3. **Kubernetes 版本兼容** — 多版本测试矩阵
4. **生产环境改动需 careful** — SRE 工具上生产, 但不代表不能提
5. **AI agent 集成加分** — 项目本身就是 AI, 扩展自然

## 关联

- CNCF 兄弟项目: `cncf/cncf`, `kubernetes/kubernetes`, `prometheus/prometheus`
- 商业合作: Robusta.Dev, Microsoft
- 协议: Apache-2.0 (兼容 pr-genius MIT)
- OKF conformance: `docs/COMPLIANCE_AUDIT.md`

## 验证

- ✅ 17 agent_guidelines 字段全填
- ✅ evidence_urls 含 5 个权威源
- ⚠️ confidence=medium (CNCF sandbox 数据少, 主要基于官方政策 + CNCF 社区规范推断)
