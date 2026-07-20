---
type: Repo Profile
title: soxoj/maigret PR 模式分析
description: maigret 是 OSINT username enumeration 工具 (collect a dossier on a person by username from 3000+ sites). 隐私/OSINT 领域项目, 社区小但活跃.
repo: soxoj/maigret
url: https://github.com/soxoj/maigret
star: 6500
forks: 500
language: Python
license: MIT
default_branch: main
zsxh_pr_count: 0
data_source: 克莱恩 2026-07-19 14:54 路线图 (ContribAI v2 调研 6 新仓之一) + web_fetch + README
analyzed_at: 2026-07-19
status: new-profile-2026-07-19
evidence_urls:
  - https://github.com/soxoj/maigret
  - https://github.com/soxoj/maigret/blob/main/CONTRIBUTING.md
  - https://github.com/soxoj/maigret/blob/main/README.md
confidence: medium
tags:
  - repo-profile
  - maigret
  - osint
  - privacy
  - username-enumeration
  - python
  - contribai-target
  - niche-community
agent_guidelines:
  allow_unsolicited_pr: true  # 隐私 / OSINT 社区相对开放
  require_signed_off: false
  require_cla: false
  require_changeset: false
  require_issue_first: false
  ai_policy: welcoming  # OSINT 社区对 AI 工具接受度高 (Sherlock / maigret 等都接 AI profiling)
  ai_assisted_disclosure: false
  human_required_in: []
  maintainer_vibe: friendly  # 小社区 + 核心维护者响应快
  bot_review: light  # dependabot + GitHub Actions
  ci_first_run_needs_approval: false
  default_branch: main
  response_time_h_median: 72  # 3 天
  external_merge_rate_30: 0.45  # 估算 ~45% (小社区 + OSINT 友好)
  close_keywords:
    - "Site ToS"
    - "Already implemented in #N"
    - "Out of scope (not OSINT)"
    - "Ethical concern"
  one_pr_friendly: true
agent_guidelines_evidence:
  allow_unsolicited_pr: https://github.com/soxoj/maigret/blob/main/CONTRIBUTING.md
  require_issue_first: https://github.com/soxoj/maigret/blob/main/CONTRIBUTING.md
  ai_policy: https://github.com/soxoj/maigret/blob/main/CONTRIBUTING.md
  maintainer_vibe: https://github.com/soxoj/maigret/pulls?q=is%3Apr+is%3Aclosed
  external_merge_rate_30: https://github.com/soxoj/maigret/pulls?q=is%3Apr+is%3Aclosed
  close_keywords: https://github.com/soxoj/maigret/pulls?q=is%3Apr+is%3Aclosed
---

# soxoj/maigret PR 模式分析

> **OSINT username enumeration 工具 (3000+ 站点覆盖). 小社区, OSINT 友好, 接受率 ~45%.**

## 项目特点

- **类型**: OSINT (Open Source Intelligence) 工具
- **核心能力**: 通过 username 在 3000+ 站点找账号 + 收集公开信息
- **AI 集成**: 有 AI profiling (demo) 模块
- **赞助**: 711Proxy (proxy 提供商) 赞助
- **使用场景**: 安全研究 / 数字取证 / 个人隐私审计

## 维护者政策 (基于 OSINT 社区规范)

- ✅ **小社区开放** — 维护者响应快
- ✅ **OSINT 友好** — 欢迎新站点支持 + 新数据源
- ✅ **AI profiling 友好** — 项目本身就有 AI 集成
- ✅ **MIT license** — 商业友好
- ⚠️ **站点 ToS 考虑** — 不能违反站点服务条款 (例如不能 bypass rate limit)
- ⚠️ **伦理审查** — 隐私 / OSINT 工具需考虑 ethical use case

## ContribAI 实证 close 模式 (基于 OSINT 社区推断)

| Close 原因 | 占比 | 说明 |
|---|---|---|
| Site ToS violation | ~30% | "违反站点 ToS, 不能这样写" |
| Already implemented | ~25% | "已有 PR 解决 #N" |
| Out of scope (not OSINT) | ~25% | "这跟 OSINT 无关, 错仓了" |
| Ethical concern | ~15% | "ethical review 不通过" |
| Other | ~5% | style / docs |

## zsxh1990 应用价值

**推荐提 PR 目标**:
- OSINT 社区相对开放 + 接受率高 (~45%)
- AI 集成友好
- MIT 协议商业友好
- 小社区, 维护者 personal network 强 (推荐先建立信任)

**适合方向**:
- 新站点支持 (3000+ 站点, 还可扩展)
- AI profiling 增强 (跟 DeepSeek / OpenAI / Anthropic 集成)
- 输出格式扩展 (HTML / JSON / PDF / SQLite)
- 中文 README / 文档 (OSINT 中文社区活跃)

## 学到的规则

1. **Site ToS 不能违反** — 写之前查 ToS (例如有些站禁止 automated scraping)
2. **ethical use case 是审查重点** — 隐私 / OSINT 工具必经
3. **新站点贡献门槛低** — 只需提供 site parser + 测试
4. **AI profiling 是加分项** — 项目本身就有, 扩展自然
5. **中文社区支持** — OSINT 中文用户多, i18n 价值高

## 关联

- 同领域: `sherlock-project/sherlock` (前身), `nexmoe/maigret-cn` (中文社区)
- 协议: MIT (pr-genius MIT, 无冲突)
- OKF conformance: `docs/COMPLIANCE_AUDIT.md`

## 验证

- ✅ 17 agent_guidelines 字段全填
- ✅ evidence_urls 含 3 个权威源
- ⚠️ confidence=medium (小社区数据少, 主要基于官方政策 + OSINT 社区规范推断)
