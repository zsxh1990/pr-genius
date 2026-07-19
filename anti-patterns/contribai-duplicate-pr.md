---
type: Anti-Pattern
key: contribai-duplicate-pr
symptom: |
  提交的 PR 跟已有 PR / Issue 重复, 或 main 分支已修复。Close 关键词: "duplicate", "already exists", "implemented in main"
root_cause: 提交前未搜索已有 PR / Issue, 未检查 main 分支最新代码, 不知道问题已被人修。
trigger_keywords:
  - "duplicate"
  - "already exists"
  - "implemented in main"
  - "see PR #N"
  - "fix already in"
fix_action: |
  1) gh search prs --repo org/repo --state all "<keyword>"
  2) gh search issues --repo org/repo --state all "<keyword>"
  3) git fetch origin main && git log origin/main | head -20
  4) Issue 区搜 "in progress" / "wip" / "claimed"
source_pr: "ContribAI pallets/flask + 14 closed, NousResearch/hermes-agent#64639"
prevention: |
  提 PR 前必跑：
  - gh search prs --state all "<keyword>"  (搜 PR)
  - gh search issues --state all "<keyword>"  (搜 Issue)
  - git fetch origin main && git log origin/main  (看 main)
  - 在 Issue 评论问 "is anyone working on this?"  (24h 等回)
learned_at: 2026-07-19
---

## ContribAI 实证 close 数据

- pallets/flask: ~15% close 是 duplicate (ContribAI 14 closed PR 中)
- NousResearch/hermes-agent: ~25% (anti-patterns/nousresearch-duplicate-pr.md 实证)
- Vite / OpenClaw: ~10% close 提到 duplicate

## 反模式特征

1. **未搜已有 PR** — 直接提 PR, 跟别人撞
2. **未查 main 分支** — main 已修, 但 PR 还按旧版修
3. **未看 Issue 状态** — Issue 已 assign 别人, 还在做
4. **AI 批量提交** — AI agent 不检查直接提, 最常见

## 自检清单

提 PR 前:
- [ ] gh search prs --state all "<keyword>"  无重复
- [ ] gh search issues --state all "<keyword>"  无 in-progress
- [ ] git fetch origin main && git log  main 已修
- [ ] 在 Issue 评论问是否有人 work  24h 内有回

## 关联

- NousResearch: `anti-patterns/nousresearch-duplicate-pr.md`
- reaper rule: 必查 search + main + Issue 三件套
