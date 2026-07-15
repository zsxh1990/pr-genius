---
type: Anti-Pattern
key: superseded-by-maintainer
description: "PR 被 maintainer 的并行 PR 取代"
symptom: "maintainer 评论: Superseded by #NNN, merged on main"
trigger_keywords:
  - "superseded by"
  - "merged on main"
  - "already fixed"
fix_action: "1) 检查取代 PR 的实现方式; 2) 学习 maintainer 的代码风格; 3) 下次提 PR 前先在 Issue 中确认是否有人在做"
source_pr: "openclaw/openclaw#104514"
severity: low
evidence:
  - "openclaw #104514: 被 #104516 取代，maintainer 自己实现了相同功能"
learned_at: 2026-07-15
---

## 反模式说明

贡献者的 PR 被 maintainer 的并行 PR 取代。通常发生在：
- Issue 被多人同时认领
- Maintainer 对实现方式有不同偏好
- 贡献者实现太慢，maintainer 自己动手

### 触发条件
- Issue 无明确 assignee
- 贡献者实现时间过长
- Maintainer 有自己的实现偏好

### 如何避免
1. 认领 Issue 后尽快提交
2. 提 PR 前在 Issue 中确认是否有人在做
3. 保持与 maintainer 的沟通
