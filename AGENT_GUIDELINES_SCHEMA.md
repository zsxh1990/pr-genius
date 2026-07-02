---
type: Schema Reference
title: agent_guidelines 字段 schema
description: Repo Profile frontmatter 中 agent_guidelines 字段的定义（Agent-first 设计）
version: 0.1.0
created: 2026-07-02
---

# agent_guidelines Schema v0.1

> 目标：让调用知识库的 Agent 在 **1 ms 内** 读 yaml 字段做出决策（vs 读 5k 散文）。
> 适用于 `*-<repo>/index.md` 的 YAML frontmatter。

## 字段定义

| 字段 | 类型 | 含义 | 默认值 |
|---|---|---|---|
| `allow_unsolicited_pr` | bool | 是否接受未开 Issue 直接提的 PR | `false` |
| `require_signed_off` | bool | 是否需要 DCO/GPG 签名 | `false` |
| `require_cla` | bool | 是否需要 CLA（Contributor License Agreement） | `false` |
| `require_changeset` | bool | 是否需要 changeset 文件 | `false` |
| `require_issue_first` | bool | 是否要求 PR 前先有 Issue 讨论 | `false` |
| `ai_policy` | enum | `welcoming` / `conditional` / `restrictive` / `hostile` | — |
| `ai_assisted_disclosure` | bool | 是否必须显式标 AI-assisted | — |
| `human_required_in` | enum[] | 强制人类参与的环节（`pr_body` / `comments` / `commits`） | — |
| `human_required_in` | bool | 是否**禁止** autonomous agent（必须 human in loop） | — |
| `maintainer_vibe` | enum | `friendly` / `strict` / `responsive` / `slow` / `hostile` | — |
| `bot_review` | enum | `none` / `coderabbit` / `devin` / `entelligence` / `sweep` | — |
| `ci_first_run_needs_approval` | bool | 首次外部贡献 CI 是否需要 maintainer 触发 | `false` |
| `default_branch` | string | 主分支名（`main` / `master`） | `main` |
| `response_time_h_median` | int | 维护者响应时间中位数（小时） | — |
| `merge_rate_30d` | float | 30 天合并率（0-1） | — |
| `close_keywords` | string[] | 维护者拒绝语关键词（用于秒级自愈匹配） | — |
| `one_pr_friendly` | bool | 是否适合"单 PR 小步快跑" | — |

## ai_policy 取值规则

- `welcoming`：维护者主动鼓励 AI 辅助（OpenClaw / uv）
- `conditional`：欢迎但有规则（uv 要 human in loop）
- `restrictive`：可以但要严格披露（E2B / honcho）
- `hostile`：明确敌视（microG / OpenBSD / Linux kernel）
- `unknown`：还没调研

## maintainer_vibe 取值规则

- `friendly`：对外部 PR 主动协助
- `strict`：要求严格（CLA / CI / 格式），但给反馈
- `responsive`：响应快（< 24h）
- `slow`：响应慢（> 7d）
- `hostile`：直接 close 无理由（Vite sapphi-red 风格）

## ai_assisted_disclosure 触发条件

- `true`：必须在 PR body / commit 显式标 AI-assisted
- `false`：可不标（默认）
- 隐含语义：标了不被惩罚，不标可能撞 bot 抓取

## human_required_in 枚举值

- `pr_body`：PR body 人类手写
- `comments`：回复评论人类手写
- `commits`：commit message 人类手写
- `code_review_response`：code review 回复人类手写
- `all_autonomous_forbidden`：禁止完全自主的 agent 行为

## 完整示例

```yaml
agent_guidelines:
  allow_unsolicited_pr: true
  require_signed_off: false
  require_cla: true
  require_changeset: true
  require_issue_first: false
  ai_policy: restrictive
  ai_assisted_disclosure: true
  human_required_in: [pr_body, comments]
  maintainer_vibe: strict
  bot_review: coderabbit
  ci_first_run_needs_approval: false
  default_branch: main
  response_time_h_median: 24
  merge_rate_30d: 0.65
  close_keywords:
    - "we're not adding this feature"
    - "not seeing major user pain"
  one_pr_friendly: true
```

## 调用约定

Agent 拿到一个目标仓时：

```python
# 1. 读 yaml
guidelines = load_frontmatter(f"research/big-repo-pr-knowledge/{org}-{repo}/index.md")["agent_guidelines"]

# 2. 决策树
if not guidelines["allow_unsolicited_pr"]:
    return "先开 issue 讨论"

if guidelines["require_cla"] and not user_signed_cla:
    return "先签 CLA"

if guidelines["ai_policy"] == "hostile":
    return "不投此仓"

if guidelines["maintainer_vibe"] == "slow":
    return "PR 提早 + 后续 ping"

# 3. 提 PR
if guidelines["human_required_in"]:
    print(f"以下环节需人类手写: {guidelines['human_required_in']}")
```

## 版本

- v0.1.0 (2026-07-02)：初版（8 仓实证数据）