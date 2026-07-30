---
type: Anti-Pattern
key: nousresearch-sweeper-blast-broad
description: "NousResearch PR 影响范围太广，标记 blast-broad"
symptom: "标签包含 sweeper:blast-broad"
trigger_keywords:
  - "blast-broad"
  - "blast-moderate"
fix_action: "1) 缩小 PR 影响范围; 2) 拆分为多个小 PR; 3) 提供回滚方案"
source_pr: "NousResearch/hermes-agent#52866, NousResearch/hermes-agent#52958"
severity: medium
evidence:
  - "NousResearch #52866: 修改 skill_utils 提取上限，标记 blast-broad"
  - "NousResearch #52958: 修改 signal 格式化，标记 blast-moderate"
learned_at: 2026-07-15
---

## 反模式说明

PR 改动影响范围太广，可能引入回归风险。

### 触发条件
- 修改核心模块
- 改动影响多个组件
- 缺少充分测试

### 如何避免
1. 保持 PR 小而聚焦
2. 拆分为多个独立 PR
3. 提供回滚方案
