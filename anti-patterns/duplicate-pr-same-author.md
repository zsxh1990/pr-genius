---
type: Anti-Pattern
key: duplicate-pr-same-author
description: "同一作者提交多个几乎相同的 PR"
symptom: "duplicate submission"
trigger_keywords:
  - "duplicate"
  - "already submitted"
  - "same changes"
fix_action: "1) 关闭重复的 PR; 2) 在原有 PR 上继续修改; 3) 如果需要重新提交，先关闭旧 PR 并说明原因"
source_pr: "woodruffw/zizmor#2110, woodruffw/zizmor#2104"
severity: high
evidence:
  - "zizmor #2110 和 #2104: 同一作者 Thinking-builder 提交了两个几乎相同的 PR"
  - "两个 PR 都被标记 ai-policy-violation 并关闭"
learned_at: 2026-07-09
---

## 反模式说明

同一作者在短时间内提交多个几乎相同的 PR，通常是因为第一个 PR 没有得到预期的响应，或者作者试图"刷"维护者的注意力。

### 触发条件

- 同一作者在短时间内（如1-2天）提交2+个 PR
- PR 的改动内容高度相似
- 没有在旧 PR 上说明为什么要重新提交

### 为什么这是反模式

1. 维护者会感到被骚扰
2. 分散 review 注意力
3. 显示作者缺乏耐心和社区礼仪

### 如何避免

1. 在原有 PR 上继续修改，而不是创建新 PR
2. 如果确实需要重新提交（如分支问题），先关闭旧 PR 并说明原因
3. 等待维护者响应，不要急于重复提交
