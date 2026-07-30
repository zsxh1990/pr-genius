---
type: Anti-Pattern
key: nousresearch-cron-risk
description: "NousResearch PR 涉及定时任务"
symptom: "标签包含 comp/cron"
trigger_keywords:
  - "comp/cron"
  - "cron"
fix_action: "1) 测试定时任务可靠性; 2) 测试边界情况; 3) 提供回滚方案"
source_pr: "NousResearch/hermes-agent#42920"
severity: medium
evidence:
  - "NousResearch #42920: 涉及 cron 定时任务"
learned_at: 2026-07-15
---

## 反模式说明

涉及定时任务的 PR 风险较高，可能导致任务重复执行或遗漏。

### 触发条件
- 修改定时任务调度逻辑
- 修改定时任务执行逻辑
- 修改定时任务错误处理

### 如何避免
1. 测试定时任务可靠性
2. 测试边界情况（时区、夏令时、服务重启）
3. 提供回滚方案
