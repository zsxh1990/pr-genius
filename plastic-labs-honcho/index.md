---
type: Repo Profile
title: plastic-labs/honcho PR 模式分析
description: honcho 仓 AI 友好度 + zsxh1990 PR #801 进展
repo: plastic-labs/honcho
url: https://github.com/plastic-labs/honcho
star: 5665
language: Python
zsxh_pr_count: 1
status: in-flight
data_source: zsxh PR #801
analyzed_at: 2026-07-01
tags:
  - repo-profile
  - ai-memory
  - python
  - fastapi
  - sqlalchemy
related:
  - ./pr-801-queue-purge.md
agent_guidelines:
  allow_unsolicited_pr: true
  require_signed_off: false
  require_cla: false  # 未确认；下次提 PR 前核实
  require_changeset: false
  require_issue_first: false
  ai_policy: welcoming
  ai_assisted_disclosure: false
  human_required_in: []
  maintainer_vibe: friendly
  bot_review: coderabbit
  ci_first_run_needs_approval: false
  default_branch: main
  response_time_h_median: 120  # 3-7 天
  merge_rate_30d: null  # 小型 startup，无统计数据
  close_keywords:
    - "please add tests"
    - "AsyncSession"
  one_pr_friendly: true
misakanet_queries:
  - misakanet/lessons/contrib/default-parameter-trap.md  # honcho #801 db 默认参数陷阱已入 MisakaNet
misakanet_lessons:
  - id: default-parameter-trap
    contributed_via: zsxh1990/honcho#801
    absorbed_at: 2026-06-21
federation_status: declared-2026-07-02
---

# plastic-labs/honcho

> Honcho 是 [Plastic Labs](https://www.plastic-labs.com/) 的 AI agent 记忆/上下文层（FastAPI + SQLAlchemy）。  
> **AI 友好度**：高（无 AI 限制政策，Plastic Labs 自己就是 AI 公司）。  
> **zsxh1990 PR 经验**：1 个 open（#801），CodeRabbit 已审 2 轮。  
> **技术栈**：Python 3.11+ / FastAPI / SQLAlchemy 2.0 async / Pydantic v2。

---

## 1. 友好度画像

- ✅ **无 AI 限制政策**（Plastic Labs 是 AI 公司，欢迎 AI 辅助 PR）
- ✅ CodeRabbit bot 配置（自动 PR review，公开讨论友好）
- ✅ External PR 比例高（小型 startup 风格）
- ⚠️ CLA 可能存在（待确认）
- ⚠️ 维护者响应 3-7 天（小型团队）

---

## 2. zsxh1990 PR 进展

### 🟢 #801 [feat: add queue purge endpoint for stranded work units](https://github.com/plastic-labs/honcho/pull/801)

| 维度 | 数据 |
|---|---|
| 创建 | 2026-06-12 01:44 UTC |
| 最后活动 | 2026-06-28 07:25 UTC（19 天） |
| 状态 | open, draft=False, merged=False |
| +283 / -0 / 3 files | 适中 |
| comments: 4 / review_comments: 3 | 互动良好 |

**关键反馈**：

1. **2026-06-12 CodeRabbit 第 1 轮**：标 2 个 actionable + 1 个 outside-diff
2. **2026-06-20 14:18 zsxh1990 自报**：
   > "Addressed both CodeRabbit findings from the initial review — thanks for the catch, they were real bugs.
   > 
   > **🔴 Critical (DB session injection) — fixed in `7ac3afe`**
   > The default value `db: AsyncSession = db` was picking up the `src.db` *module* (from `from src import db, models`),"
3. **2026-06-20 14:24 CodeRabbit 第 2 轮**：再标 1 个 finding
4. **后续**：zsxh1990 已修但未提交第 3 轮 amend（机会窗口）

### 关键教训（内化为 MEMORY.md §8）

**PR 默认参数陷阱**：`db: AsyncSession = db` 看着对，**实际 import 冲突**
- `from src import db, models` 的 `db` 是 module
- `from src.dependencies import db` 的 `db` 才是 `Depends(get_db)` 代理
- 改前必用 basedpyright 验证 default value 类型匹配

**ORM anti-pattern**：`select(Model).scalars().all() → len()` 应改 `select(func.count())`

详细案例见 [pr-801-queue-purge.md](./pr-801-queue-purge.md)。

---

## 3. 提 PR 方向

### 🥇 bug fix（已知活跃）

- 搜 `is:issue is:open label:bug` 在 honcho
- FastAPI 异步陷阱、SQLAlchemy session leak、Pydantic v2 迁移遗留

### 🥈 docs 改进

- honcho 文档较散，API reference 与 tutorial 不一致
- 加 example：multi-agent memory sharing 场景

### 🥉 enhancement（参考已合并）

- 已 merge #798、#800 等
- 方向：observability（OpenTelemetry）、admin endpoint、metrics

---

## 4. SOP（与 OpenClaw/uv 通用差异）

| 维度 | honcho 特色 |
|---|---|
| CI | 跑 SQLAlchemy 2.0 async 测试 + 基于 pytest-asyncio |
| Type check | 必过 mypy strict |
| Commit msg | Conventional Commits |
| CLA | 需确认（小型 startup 通常无 CLA，但部分会加） |

---

## 5. 反模式

- ❌ FastAPI default value 写 `db: AsyncSession = db`（撞 #801 已修 bug）
- ❌ `.scalars().all() → len()` 模式（CodeRabbit 必抓）
- ❌ 同步 SQLAlchemy（项目全 async）
- ❌ uv sync 后不检查 `uv.lock` 改动（MEMORY.md §10）

---

## 6. 关联文档

- [OKF bundle 根入口](../index.md)
- [PR #801 案例深读](./pr-801-queue-purge.md)