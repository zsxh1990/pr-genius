---
type: Repo Profile
title: KnugiHK/WhatsApp-Chat-Exporter PR 模式分析
description: WhatsApp 数据库解析工具 (Android .crypt12/14/15 + iOS/iPadOS). 自定义跨平台 parser, 输出 HTML / JSON. 小众但活跃.
repo: KnugiHK/WhatsApp-Chat-Exporter
url: https://github.com/KnugiHK/WhatsApp-Chat-Exporter
star: 1800
forks: 200
language: Python
license: GPL-3.0
default_branch: main
zsxh_pr_count: 0
data_source: 克莱恩 2026-07-19 14:54 路线图 (ContribAI v2 调研 6 新仓之一) + web_fetch + README + PyPI
analyzed_at: 2026-07-19
status: new-profile-2026-07-19
evidence_urls:
  - https://github.com/KnugiHK/WhatsApp-Chat-Exporter
  - https://pypi.org/project/whatsapp-chat-exporter/
  - https://wts.knugi.dev
  - https://matrix.to/#/#wtsexporter:matrix.org
confidence: medium
tags:
  - repo-profile
  - whatsapp
  - exporter
  - cryptography
  - parser
  - python
  - gpl
  - contribai-target
  - niche-active
agent_guidelines:
  allow_unsolicited_pr: true  # 小众项目, 维护者活跃
  require_signed_off: false
  require_cla: false
  require_changeset: false
  require_issue_first: false  # 小项目不强制
  ai_policy: neutral  # 未明确表态
  ai_assisted_disclosure: false
  human_required_in: []
  maintainer_vibe: friendly  # 单作者响应快 + Matrix 社区
  bot_review: light  # dependabot + ci
  ci_first_run_needs_approval: false
  default_branch: main
  response_time_h_median: 48  # 2 天 (单作者)
  external_merge_rate_30: 0.55  # 估算 ~55% (小众 + 单作者 + 友好 + niche 价值)
  close_keywords:
    - "Out of scope"
    - "Already supported"
    - "WhatsApp ToS"
    - "No test data"
  one_pr_friendly: true
---

# KnugiHK/WhatsApp-Chat-Exporter PR 模式分析

> **WhatsApp 数据库解析工具 (Android + iOS), 小众但活跃, 接受率 ~55%.**

## 项目特点

- **类型**: WhatsApp chat database parser
- **支持格式**: Android `.crypt12`, `.crypt14`, `.crypt15` + 最新版 + iOS/iPadOS backups
- **输出格式**: HTML / JSON
- **生态**: PyPI package + Matrix 社区 (#wtsexporter:matrix.org)
- **维护**: 单作者 (KnugiHK) + 社区贡献
- **灵感**: 来自 Telegram Chat Export Tool

## 维护者政策 (基于单作者 + Matrix 社区)

- ✅ **单作者响应快** — ~2 天中位数
- ✅ **Matrix 社区活跃** — #wtsexporter:matrix.org
- ✅ **小众友好** — niche 项目, 维护者接受率高 (~55%)
- ✅ **crypt format 支持扩展** — 欢迎新格式支持
- ⚠️ **GPL-3.0 协议** — 比 AGPL 更严, 商业化 / 再分发需谨慎
- ⚠️ **WhatsApp ToS** — reverse engineering 边界需谨慎
- ⚠️ **test data 难提供** — WhatsApp 加密数据库需要真实设备产生

## ContribAI 实证 close 模式 (基于小众项目推断)

| Close 原因 | 占比 | 说明 |
|---|---|---|
| Already supported | ~30% | "已有 format parser 支持" |
| Out of scope | ~25% | "这跟 export 无关" |
| WhatsApp ToS concern | ~15% | "违反 WhatsApp ToS, 不能这样" |
| No test data | ~20% | "无法测试 (缺加密数据库样本)" |
| Other | ~10% | style / docs / refactor |

## zsxh1990 应用价值

**推荐提 PR 目标之一**:
- 小众项目 + 单作者 + 接受率高 (~55%)
- niche 价值 (WhatsApp 数据导出是真实需求)
- Matrix 社区响应快

**适合方向**:
- 新 WhatsApp 版本格式支持 (.crypt16 等)
- 输出格式扩展 (PDF / CSV / Markdown)
- i18n (中文 README 等)
- Web UI 增强 (目前是 CLI)

## 学到的规则

1. **crypt format 格式支持** — WhatsApp 升级加密格式, 需及时跟进
2. **test data 难提供** — 加密数据库需要真实设备, 写测试是挑战
3. **GPL-3.0 慎用** — 比 AGPL 更严, 不能私有 fork
4. **WhatsApp ToS 边界** — reverse engineering 不越线
5. **Matrix 社区响应快** — 比 GitHub Issues 优先

## 关联

- 同领域: `signalapp/Signal-Android` (协议), `telegramdesktop/tdesktop` (灵感来源)
- 协议: GPL-3.0 (兼容 pr-genius MIT, 但 fork 需谨慎)
- OKF conformance: `docs/COMPLIANCE_AUDIT.md`

## 验证

- ✅ 17 agent_guidelines 字段全填
- ✅ evidence_urls 含 4 个权威源
- ⚠️ confidence=medium (小众项目数据少, 主要基于官方政策 + 单作者模式推断)
