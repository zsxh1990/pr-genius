---
type: Anti-Pattern
key: upstream-already-implementing
symptom: "官方自己做了" / "upstream implemented" / "we're already working on this"
root_cause: 维护者已经在内部实现或计划实现相同功能，外部 PR 被拒绝是因为重复劳动。**注意：这是最有价值的反模式，因为它证明你的方向是正确的！**
trigger_keywords:
  - "already working on this"
  - "upstream implemented"
  - "we're planning to"
  - "duplicate effort"
  - "官方自己做了"
fix_action: 这不是失败，而是验证！下一步：(1) 等待维护者实现完成 (2) 协助测试或文档 (3) 寻找下一个类似需求
source_pr: astral-sh/uv#19685
prevention: "提 PR 前检查：(1) 维护者的 roadmap/TODO (2) 最近 30 天的 commit 历史 (3) 是否有相关 Issue 被 assign 给维护者。如果发现维护者已在做，不要沮丧——你的方向是对的！"
learned_at: 2026-07-08
value: HIGH  # 最有价值的反模式，证明方向正确
---

## 案例

### astral-sh/uv #19685 — SARIF output
- **提交内容**: 为 uv 添加 SARIF 格式输出
- **拒绝原因**: 维护者自己实现了相同功能 (#19872)，我们的 PR 被关闭
- **教训**: 大型项目维护者可能已经在内部实现某些功能，外部 PR 会变成重复劳动

## 反模式特征

1. **功能在 roadmap 中**: 维护者已经计划实现这个功能
2. **最近有相关 commit**: 维护者最近的 commit 涉及相同功能
3. **Issue 被 assign**: 相关 Issue 已经被 assign 给维护者团队
4. **没有先沟通**: 直接提 PR，没有先问维护者是否已经在做

## 自检清单

提 PR 前检查：
- [ ] 维护者的 roadmap/TODO 中是否有这个功能？
- [ ] 最近 30 天的 commit 历史是否涉及这个功能？
- [ ] 是否有相关 Issue 被 assign 给维护者？
- [ ] 有没有先在 Issue 中问"是否已经在做"？
