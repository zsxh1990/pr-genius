---
type: Repo Profile
title: e2b-dev/awesome-ai-agents PR 模式分析
description: 29k-star AI agent 精选列表，极低合并率，维护者高度策展
repo: e2b-dev/awesome-ai-agents
url: https://github.com/e2b-dev/awesome-ai-agents
star: 29224
language: Markdown
zsxh_pr_count: 1
status: in-flight-1242
analyzed_at: 2026-08-01
tags:
  - repo-profile
  - awesome-list
  - ai-agents
  - curated
related:
  - ./pr-1242-cross-agent-experience.md
agent_guidelines:
agent_guidelines_evidence: {}
agent_guidelines_evidence:
  allow_unsolicited_pr: true
  require_signed_off: false
  require_cla: true  # CLA-signed check in CI
  require_changeset: false
  require_issue_first: false
  ai_policy: neutral  # 无明确反 AI 政策，但极低合并率暗示高度筛选
  ai_assisted_disclosure: false
  human_required_in: []
  maintainer_vibe: passive  # 不回复 ping，不主动 review
  bot_review: none
  ci_first_run_needs_approval: true  # CLA check 需要 approval
  default_branch: main
  response_time_h_median: null  # 维护者几乎不回复外部 PR
  merge_rate_30d: 0.07  # 2/30 最近 30 closed PR 合并
  close_keywords: []
  one_pr_friendly: false  # 大量 "Add X" PR 被直接关闭
misakanet_queries: []
misakanet_lessons: []
federation_status: declared-2026-08-01
verified_at: "2026-08-01T16:30:00Z"
evidence_urls:
  - https://github.com/e2b-dev/awesome-ai-agents
  - https://api.github.com/repos/e2b-dev/awesome-ai-agents
confidence: high
stars: 29224
---
rejection_patterns:
  - "大量 'Add X' PR 被关闭无 comment"
  - "维护者不回复外部 ping"
  - "新 section/category 极难获批"
  - "只有极简 1-line 加入现有 section 才可能合并"
success_patterns:
  - "#123 PraisonAI: 空 body, 加入现有 section"
  - "#1223 UTM tracking: 内部维护性质 PR"
