---
type: Repo Profile
title: Ikalus1988/MisakaNet PR 模式分析
description: MisakaNet — 热心市民的御坂网络知识库，pr-genius 的 federation peer
repo: Ikalus1988/MisakaNet
url: https://github.com/Ikalus1988/MisakaNet
star: 0
language: Python
license: MIT
default_branch: main
zsxh_pr_count: 10
status: active
analyzed_at: 2026-07-09
data_source: 内部项目，直接访问
agent_guidelines:
  allow_unsolicited_pr: true
  require_signed_off: false
  require_cla: false
  require_issue_first: true
  ai_policy: welcoming
  ai_assisted_disclosure: false
  maintainer_vibe: responsive
  bot_review: false
  ci_first_run_needs_approval: false
  default_branch: main
  response_time_h_median: 24
  external_merge_rate_30: 0.30
  close_keywords: ["already merged", "duplicate", "superceded"]
  one_pr_friendly: true
federation_status: declared-2026-07-09
tags:
  - repo-profile
  - misakanet
  - python
  - knowledge-base
  - agent-platform
agent_guidelines_evidence:
  allow_unsolicited_pr: https://github.com/Ikalus1988/MisakaNet/blob/main/CONTRIBUTING.md
  require_issue_first: https://github.com/Ikalus1988/MisakaNet/blob/main/CONTRIBUTING.md
  ai_policy: https://github.com/Ikalus1988/MisakaNet/blob/main/CONTRIBUTING.md
  maintainer_vibe: https://github.com/Ikalus1988/MisakaNet/pulls?q=is%3Apr+is%3Aclosed
  external_merge_rate_30: https://github.com/Ikalus1988/MisakaNet/pulls?q=is%3Apr+is%3Aclosed
  close_keywords: https://github.com/Ikalus1988/MisakaNet/pulls?q=is%3Apr+is%3Aclosed
---

## PR 文化

- **合并率**: 外部贡献者 ~30%（竞争激烈，Agent 竞赛模式）
- **响应时间**: 中位数 ~24h（维护者活跃）
- **审查风格**: 维护者亲自审查，关注 frontmatter 规范 + 内容质量
- **常见拒绝原因**: 重复修复（already merged）、frontmatter 不合规、内容质量不足

## 反模式（已观察到）

1. **Duplicate fix**: 多个 Agent 同时修同一个 Issue，先 merge 的赢
2. **Frontmatter drift**: YAML frontmatter 不符合 validate_lessons.py 规范
3. **AI-generated low quality**: Agent 竞赛产出的 PR 质量参差不齐

## 建议

1. 提 PR 前先检查 Issue 是否已有 open PR
2. 使用 `validate_lessons.py` 验证 frontmatter
3. 确保 lesson 内容有完整的 Problem → Root Cause → Solution 结构
4. 使用 `coach` 命令预检: `python3 -m prgenius coach "title" --repo Ikalus1988/MisakaNet --body "..."`

## 关联

- pr-genius 作为 MisakaNet 的 Contributor Quality Sidecar
- 被拒 PR 通过 `harvest` 命令沉淀为 lesson/anti-pattern

## PR Case Studies（本仓 5 项）

- [pr-439-pep668-lesson.md](./pr-439-pep668-lesson.md) — MisakaNet #439 — PEP 668 lesson
- [pr-440-frontmatter-tests.md](./pr-440-frontmatter-tests.md) — MisakaNet #440 — frontmatter 边界测试
- [pr-441-smart-fallback.md](./pr-441-smart-fallback.md) — MisakaNet #441 — smart fallback with telemetry
- [pr-452-frontmatter-batch.md](./pr-452-frontmatter-batch.md) — MisakaNet #452 — 20 bare JSON → YAML
- [pr-474-fanuc-lessons.md](./pr-474-fanuc-lessons.md) — MisakaNet #474 — 7 FANUC 机器人课程
