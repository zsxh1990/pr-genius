---
type: Repo Profile
title: e2b-dev/E2B PR 模式分析
description: E2B cloud sandbox CLI PR 模式 + zsxh1990 PR 经验（含永久归档教训）
repo: e2b-dev/E2B
url: https://github.com/e2b-dev/E2B
star: 12783
language: Python
zsxh_pr_count: 2
status: archived-pitfall
analyzed_at: 2026-07-01
tags:
  - repo-profile
  - cloud-sandbox
  - python
  - cli
  - error-handler-archived
related:
  - ./pr-1413-rich-to-ansi.md
agent_guidelines:
  allow_unsolicited_pr: true
  require_signed_off: false
  require_cla: true  # @cla-bot 强制
  require_changeset: true  # @changeset-bot 强制
  require_issue_first: false
  ai_policy: restrictive
  ai_assisted_disclosure: true
  human_required_in: [comments]  # 推断：mishushakov 互动礼貌 = 人类在 loop
  maintainer_vibe: strict
  bot_review: none
  ci_first_run_needs_approval: false
  default_branch: main
  response_time_h_median: 9  # 9h 考虑后拒 (PR #1458 验证)
  merge_rate_30d: null
  close_keywords:
    - "we're not adding this feature"
    - "not seeing major user pain"
    - "appreciate the initiative"
  one_pr_friendly: false  # CLA + changeset 流程重
---

# e2b-dev/E2B

> E2B 是 cloud sandbox（AI 代码执行环境）CLI。  
> **AI 友好度**：**高但严格**（CLA 必须签 + 不接受 _ERROR_HANDLER 类）。  
> **zsxh1990 PR 经验**：2 个 closed（1413 merged + 1458 closed-not-merged）。  
> **关键教训**：E2B 礼貌但坚定地拒绝"通用基础设施"类 PR。

---

## 1. 友好度画像

- ✅ 大型 startup（12.7k star，AI 公司）
- ✅ 外部 PR 接受率中（中等严格）
- ⚠️ **CLA 必须签**（@cla-bot 强制）
- ⚠️ **changeset 必填**（@changeset-bot 强制）
- ⚠️ mishushakov（maintainer）"not seeing major user pain" 就 close

---

## 2. zsxh1990 PR 历史

| PR | 标题 | 状态 | 关键反馈 |
|---|---|---|---|
| [#1413](https://github.com/e2b-dev/E2B/pull/1413) | refactor: replace rich with stdlib ANSI for template logger | ✅ merged (2026-06-09) | — |
| [#1458](https://github.com/e2b-dev/E2B/pull/1458) | feat(cli): add E2B_ERROR_HANDLER for unhandled rejection and exit routing | ❌ closed (2026-06-18) | mishushakov "we're not adding this feature to our CLI" |

详细案例见 [pr-1413-rich-to-ansi.md](./pr-1413-rich-to-ansi.md)。

---

## 3. _ERROR_HANDLER 方向（永久归档）

**2026-06-18 22:11 GMT+8 克莱恩拍板 C**：

- PR #1458 (E2B_ERROR_HANDLER) 被 mishushakov 在 2026-06-18 12:37 礼貌关闭
- 评论："appreciate the initiative... we're not adding this feature to our CLI."
- **不拉黑但本 feature 关闭**
- **未来可尝试 E2B 别的方向**（bug fix / doc 改进 / 别的 feature）
- **_ERROR_HANDLER 这个方向永久归档**

E2B 跟 Vite 不同：
- Vite：~1h 考虑后秒拒（sapphi-red）→ 永久拉黑
- E2B：~9h 考虑后拒（mishushakov）→ 礼貌 close，可继续合作

---

## 4. 提 PR 方向（避开 _ERROR_HANDLER）

### 🥇 bug fix

- 搜 `is:issue is:open label:bug` 在 E2B
- CLI 异常处理、sandbox lifecycle、auth flow

### 🥈 refactor（1413 已验证成功）

- 把外部重依赖换 stdlib（rich → ANSI 模式已成功）
- 类似：typer → argparse（如必要）/ pydantic v1 → v2

### 🥉 docs 改进

- E2B cookbook 案例补充
- 多语言 sandbox 启动模板

---

## 5. CLA 流程

E2B **必须**签 CLA 才能合并：

1. 访问 https://e2b.dev/docs/cla
2. 签完后**回 PR 评论 "@cla-bot check"**
3. cla-bot 自动 verify

**⚠️ 教训**：CLA 没签 = 物理不可合（参考 openlegion-ai/openlegion#1026 同模式）。

---

## 6. 关联文档

- [OKF bundle 根入口](../index.md)
- [PR #1413 案例深读](./pr-1413-rich-to-ansi.md)
- [MEMORY.md §7 E2B 不拉黑但本 feature 关闭](../../../MEMORY.md)