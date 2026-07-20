---
type: Repo Profile
title: astral-sh/uv PR 模式分析
description: uv 仓的 PR 模式 + 友好度 + 5 个提 PR 目标 + SOP
repo: astral-sh/uv
url: https://github.com/astral-sh/uv
star: 86923
language: Rust
zsxh_pr_count: 2
data_source: research/uv-pr-knowledge/
analyzed_at: 2026-06-27
tags:
  - repo-profile
  - python-tooling
  - rust
  - ai-friendly-conditional
related:
  - ./pr-19685-sarif-audit.md
agent_guidelines:
  allow_unsolicited_pr: true
  external_merge_rate: 0.93
  require_signed_off: false
  require_cla: false
  require_changeset: false
  require_issue_first: false
  ai_policy: conditional
  ai_assisted_disclosure: true
  human_required_in: [pr_body, comments, all_autonomous_forbidden]
  maintainer_vibe: responsive
  bot_review: none
  ci_first_run_needs_approval: false
  default_branch: main
  response_time_h_median: 12
  merge_rate_30d: 0.729
  close_keywords:
    - "autonomous"
    - "breaking change"
  one_pr_friendly: true
misakanet_queries:
  - misakanet/lessons/contrib/pr-strategy.md#external-pr-friendly-rate  # uv 友好度数据
  - misakanet/lessons/contrib/pr-strategy.md#ai-assisted-disclosure-policy  # uv vs Claude Code 政策对比
misakanet_lessons: []
federation_status: declared-2026-07-02
verified_at: "2026-07-05T14:53:11.740158Z"
evidence_urls:
  - https://github.com/astral-sh/uv
  - https://api.github.com/repos/astral-sh/uv
  - https://api.github.com/repos/astral-sh/uv/releases/latest
  - https://api.github.com/repos/astral-sh/uv/commits
confidence: high  # autogen from GH API; bump to medium if human-curated
last_release: 0.11.26
last_commit_sha: 32194f49
stars: 87098
agent_guidelines_evidence:
  allow_unsolicited_pr: https://github.com/astral-sh/uv/blob/main/CONTRIBUTING.md
  require_issue_first: https://github.com/astral-sh/uv/blob/main/CONTRIBUTING.md
  ai_policy: https://github.com/astral-sh/uv/blob/main/CONTRIBUTING.md
  maintainer_vibe: https://github.com/astral-sh/uv/pulls?q=is%3Apr+is%3Aclosed
  external_merge_rate_30: https://github.com/astral-sh/uv/pulls?q=is%3Apr+is%3Aclosed
  close_keywords: https://github.com/astral-sh/uv/pulls?q=is%3Apr+is%3Aclosed
---


# astral-sh/uv

> uv 是 Astral 开发的 Python 包管理器 + 解析器（Rust 实现）。  
> **AI 友好度**：规则化友好（[AI_POLICY.md](https://github.com/astral-sh/uv/blob/main/AI_POLICY.md) 明确欢迎 AI 工具，但禁止 autonomous agent）。  
> **zsxh1990 PR 经验**：2 个 PR（1 merged + 1 closed with maintainer feedback）。  
> **数据来源**：[research/uv-pr-knowledge/](../../uv-pr-knowledge/README.md)（5 切片 693 PR metadata + 24 PR 深读）。

---

## 1. 友好度画像

### 1.1 AI 政策（最关键）

- ✅ 明确允许 AI 写代码：*"We support using AI (i.e., LLMs) as tools for coding"*
- ⚠️ 强制 human in the loop：*"PR description and comments should be written by a human"*
- ⚠️ 评论必须手写：*"Do not copy responses from the AI when replying to questions"*
- ❌ **禁止 autonomous agent**：*"We will close any pull requests that we believe were created autonomously"*
- 🤖 bot `bot:ai-policy-comment` 历史上只命中 **6 个 PR**（全来自 LouisLau-art 2026-02-06 一天批量）= bot 抓的是"明显 autonomous 行为模式"，**不是"用了 AI 写代码"**

**结论**：zsxh1990 提 AI 辅助 PR 完全 OK，只要：
1. PR body + 评论**人类手写**（克莱恩/太阳）
2. **真实理解代码**（不是 AI 写完就交）
3. PR body 显式标 "AI-assisted" 透明披露
4. 不批量提多个相似 PR（撞 autonomous 模式）

### 1.2 合并率（30d）

| 维度 | 数据 | 对比 OpenClaw 6 月 |
|---|---|---|
| 30d merged | 234 | — |
| 30d closed-not-merged | 87 | — |
| **30d 合并率** | **72.9%** | 70.9% |

→ **uv 真的友好**（2.7:1 merged:closed 比例）。

### 1.3 失败标签画像（30d 87 close）

| 标签 | 占比 | 含义 |
|---|---|---|
| `internal` | 11.5% | 维护者撤销自己 PR（**不代表外部分失败**） |
| `bot:ai-policy-comment` | 6.9% | AI policy 触发（**全是 LouisLau-art**） |
| `breaking` | 5.7% | breaking 改动 = close 重灾区 |
| `bug` | 5.7% | **bug fix 失败率最低** = 优选方向 |
| `enhancement` | 3.4% | 增强类也可 |

**关键发现**：
- **bug fix 优先**（close 率 5.7%）
- **breaking 改动 = 红线**（合并 0/200）
- **enhancement 类也可**（close 率 3.4%）

---

## 2. zsxh1990 在 uv 的 PR 历史

| PR | 标题 | 状态 | 关键反馈 |
|---|---|---|---|
| [#19685](https://github.com/astral-sh/uv/pull/19685) | uv audit: SARIF output | ✅ merged (2026-06-05) | 一次性成功 |
| #19685 review | woodruffw 反馈 | — | "在 [issue #19660](https://github.com/astral-sh/uv/issues/19660) 之类讨论前不要直接提 PR，等 maintainer 共识" |

详细案例见 [pr-19685-sarif-audit.md](./pr-19685-sarif-audit.md)。

---

## 3. 5 个提 PR 目标（按命中率排序）

> 数据驱动：基于 693 PR metadata + 24 PR 深读 + zsxh1990 经验。

### 🥇 1. bug fix - 高命中率

- **方向**：搜 `is:issue is:open label:bug` 找 1 周内新建的 bug
- **依据**：30d close 中 bug 仅 5.7%（最低）
- **SOP**：先在 issue 下评论 "I'd like to take this" → 等 maintainer ack → fork → 改 → PR

### 🥈 2. SARIF output 扩展 - 已有基础

- **方向**：[#19685](https://github.com/astral-sh/uv/pull/19685) 已 merge SARIF basic，可补：
  - SARIF result severity 字段
  - SARIF suppression 支持
  - SARIF rule index
- **依据**：woodruffw 已接受基础，扩展等于"在已成功方向上深耕"
- **风险**：扩展方向必须先开 issue 取得共识（woodruffw 警告）

### 🥉 3. enhancement (low-risk) - 中命中率

- **方向**：`is:issue is:open label:enhancement -label:breaking` 找 non-breaking 增强
- **依据**：30d close 3 个 = 3.4% close 率
- **陷阱**：不要做"看起来很小但实际是 breaking"的改动（uv 100% close breaking）

### 4. performance 优化 - 需 PoC

- **方向**：`is:issue is:open label:performance`
- **依据**：合并 200 PR 中 performance 6 个 = 3%
- **前置**：必须带 benchmark（uv 仓严格要 `#[track_caller]` + criterion 数据）

### 5. docs 改进 - 安全牌

- **方向**：typo / 例子补充 / 链接修复
- **依据**：低风险，无 breaking 担忧
- **陷阱**：维护者可能因"不需要" close（参考 Dicklesworthstone/mcp_agent_mail_rust#141 模式）

---

## 4. SOP（提 PR 流程）

### Step 1: 选 issue（30 分钟）

```bash
# 必跑 query
gh search issues --repo astral-sh/uv --state open --label bug
gh search issues --repo astral-sh/uv --state open --label enhancement --limit 20
```

**筛选条件**：
- 1 周内新建（避免老 issue 已有 in-flight PR）
- 无 `linked-pr` 标签
- 评论数 ≤ 3（避免讨论已锁定的方向）

### Step 2: 评论抢 issue（15 分钟）

```text
Hi! I'd like to take this on. Plan:
- 改 [具体文件]
- 加 [测试]
- 不动 [相邻模块]

Will open draft PR within 48h.
```

**等 24h**：无 maintainer 反对 → 进 Step 3。  
**有反对**：换目标。

### Step 3: 写代码（1-2 小时）

- `cargo build --release` 通过
- `cargo test` 全绿
- 新代码必须有 `#[test]` 覆盖
- 改动 < 300 lines（uv 平均合并 PR 309 lines）

### Step 4: PR body 模板（AI-assisted 必填）

```markdown
## Summary
[1-2 句话]

## Test Plan
- [ ] `cargo test` 通过
- [ ] 新增 [N] 个单元测试
- [ ] [具体手动验证命令]

## AI Assistance
This PR was written with AI assistance (Claude Sonnet 4.6).
The human author reviewed every line, ran the full test suite,
and verified the behavior end-to-end.
```

### Step 5: 提交 + 监控

- push → 等 CI → 等 review → 修评论 → merge
- **6h 无 review 主动 ping**："Friendly ping — happy to address feedback 🙂"
- **7 天无活动主动 close**（学 OpenClaw ClawSweeper 优雅退出）

---

## 5. 反模式（绝对不做）

- ❌ 批量提相似 PR（撞 autonomous agent 检测）
- ❌ 复制 AI 写的 PR description（违反 AI_POLICY）
- ❌ Breaking 改动（合并 0%）
- ❌ 直接提 PR 不开 issue（woodruffw 警告：等 maintainer 共识）
- ❌ 改动 > 500 lines（uv 偏好小 PR）
- ❌ 加新依赖（uv 严格控制 dep tree）

---

## 6. 关键 maintainer

| maintainer | 角色 | 响应速度 |
|---|---|---|
| @charliermarsh | Astral 创始，uv lead | 24h 内 |
| @zanieb | 核心维护 | 24-48h |
| @woodruffw | Astral 安全 + uv 维护 | 2-7 天（严格） |
| @konstin | Astral 联合创始 | 1-2 周 |

→ woodruffw 是安全话题 reviewer，**涉及安全的 PR 必须先 issue 讨论**。

---

## 7. 关联文档

- [OKF bundle 根入口](../index.md)
- [zsxh1990 PR #19685 案例深读](./pr-19685-sarif-audit.md)
- [完整 uv 调研数据](../uv-pr-knowledge/)
- [OpenClaw PR 知识库（参考）](../../openclaw-pr-knowledge/README.md)