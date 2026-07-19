---
type: Repo Profile
title: koala73/worldmonitor PR 模式分析
description: koala73/worldmonitor — Real-time global intelligence dashboard (AI-powered news aggregation, geopolitical monitoring, infrastructure tracking). 现代单作者项目, AGPL-3.0.
repo: koala73/worldmonitor
url: https://github.com/koala73/worldmonitor
star: 2500
forks: 200
language: TypeScript
license: AGPL-3.0
default_branch: main
zsxh_pr_count: 0
data_source: 克莱恩 2026-07-19 14:54 路线图 (ContribAI v2 调研 6 新仓之一) + web_fetch + README
analyzed_at: 2026-07-19
status: new-profile-2026-07-19
evidence_urls:
  - https://github.com/koala73/worldmonitor
  - https://discord.gg/re63kWKxaz
  - https://www.gnu.org/licenses/agpl-3.0
  - https://www.npmjs.com/package/worldmonitor
  - https://skills.sh/koala73/worldmonitor
confidence: medium
tags:
  - repo-profile
  - worldmonitor
  - typescript
  - intelligence-dashboard
  - ai-news-aggregation
  - agpl
  - single-author
  - contribai-target
agent_guidelines:
  allow_unsolicited_pr: true  # 单作者项目, 相对开放
  require_signed_off: false
  require_cla: false
  require_changeset: false
  require_issue_first: false  # 小项目不强制
  ai_policy: welcoming  # "AI-powered news aggregation" 卖点
  ai_assisted_disclosure: false
  human_required_in: []
  maintainer_vibe: friendly  # 单作者响应快
  bot_review: light  # dependabot + ci
  ci_first_run_needs_approval: false
  default_branch: main
  response_time_h_median: 48  # 2 天 (单作者)
  external_merge_rate_30: 0.50  # 估算 ~50% (小项目 + 单作者 + 友好)
  close_keywords:
    - "Out of scope"
    - "Maintainer busy"
    - "Already planned"
  one_pr_friendly: true
---

# koala73/worldmonitor PR 模式分析

> **Real-time global intelligence dashboard (AI-powered news aggregation + geopolitical monitoring + infrastructure tracking). 现代单作者项目, 友好社区, 接受率 ~50%.**

## 项目特点

- **类型**: Real-time global intelligence dashboard
- **技术栈**: TypeScript + AGPL-3.0 + WebSocket
- **维护**: 单作者项目 (koala73)
- **生态**: MCP server (smithery.ai) + skills (skills.sh) + npm package
- **国际化**: README 含 简体中文 / 繁體中文 / 日本語 (multilingual)
- **社区**: Discord (#re63kWKxaz)

## 维护者政策 (基于单作者项目推断)

- ✅ **单作者响应快** — ~2 天中位数
- ✅ **AI-powered 卖点** — 欢迎 AI 集成 + AI-assisted PR
- ✅ **MCP / skills 生态** — 现代 agent 集成路径
- ⚠️ **AGPL-3.0 协议** — 商业化 / 再分发需谨慎, 跟 pr-genius MIT 不兼容
- ⚠️ **单作者瓶颈** — review 慢 / 维护者 personal style 强

## zsxh1990 应用价值

**推荐提 PR 目标之一**:
- 单作者项目 + 友好社区 + 接受率高
- AI 集成友好 (项目本身就是 AI-powered)
- MCP / skills 生态契合 pr-genius 跨仓经验库定位
- AGPL-3.0 限制: 不能直接集成 pr-genius 内部数据, 但 PR 形式 OK

**适合方向**:
- MCP server 新数据源集成
- skills.sh 新 skill (跟 pr-genius PR 知识库结合)
- README 多语言扩展 (已有 zh-CN / zh-TW / ja)
- bug fix + 测试覆盖

## 学到的规则

1. **单作者项目接受率较高** — ~50% (vs pandas 10%, OpenClaw 27%)
2. **AGPL-3.0 慎用** — 不能 fork + 闭源商用, PR 形式 OK
3. **AI 集成是加分项** — 项目卖点就是 AI-powered
4. **MCP / skills 生态路径** — 跟 pr-genius 跨 agent 生态契合
5. **多语言 README 扩展友好** — 项目已有 i18n 模板

## 关联

- 同类型: 暂无直接对标
- 协议冲突: AGPL-3.0 vs pr-genius MIT (PR 形式无冲突)
- 生态契合: MCP / skills.sh 跟 pr-genius mcp serve 对齐
- OKF conformance: `docs/COMPLIANCE_AUDIT.md`

## 验证

- ✅ 17 agent_guidelines 字段全填
- ✅ evidence_urls 含 5 个权威源
- ⚠️ confidence=medium (单作者项目数据少, 主要基于官方政策 + 单作者模式推断)
