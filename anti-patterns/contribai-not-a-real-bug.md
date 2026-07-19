---
type: Anti-Pattern
key: contribai-not-a-real-bug
symptom: |
  提交的"bug"实际是设计如此或预期行为。Close 关键词: "not a real bug", "this is by design", "intended behavior", "working as expected"
root_cause: 未读源码 / 未理解设计意图, 把 "看起来不对" 当 bug。
trigger_keywords:
  - "not a real bug"
  - "by design"
  - "intended behavior"
  - "working as expected"
  - "this is how it works"
fix_action: |
  1) 读源码确认行为是设计还是 bug
  2) 找 maintainer 在 issue/邮件列表的官方说明
  3) 写 failing test 复现, 然后跟 maintainer 讨论设计意图
source_pr: "pallets/flask ~35% close 是 Not a real bug (ContribAI v2 调研头号)"
prevention: |
  提 PR 前:
  - 读相关源码理解设计意图
  - 找 maintainer 历史 issue / 邮件列表对该行为的解释
  - 在 issue 区先讨论 "is this a bug or by design?"
  - 写 failing test 复现, 不靠"我觉得"
learned_at: 2026-07-19
---

## ContribAI 实证 close 数据

- pallets/flask: **~35%** close 是 Not a real bug (头号杀手)
- React / Vue / Angular 等 UI 库: 类似比例
- 大型 framework 通用: 20-35% close 是 Not a real bug

## 反模式特征

1. **未读源码** — 直接看 README / 示例推断 "bug"
2. **未理解设计意图** — 框架的 "限制" 是 deliberate 设计
3. **AI agent 幻觉 bug** — LLM 看 README 想象一个 bug, 不验证源码
4. **没复现** — 没 failing test, 直接说 "我觉得是 bug"

## 自检清单

提 PR 前:
- [ ] 读相关源码理解为什么这样实现
- [ ] 搜 maintainer 历史 issue 看有没有解释
- [ ] 写 failing test 复现
- [ ] 在 issue 区先问 "is this intentional?"

## 关联

- pallets profile: `pallets-flask/index.md` (Not a real bug 占 35%)
