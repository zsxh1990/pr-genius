---
type: Anti-Pattern
key: openclaw-refactor-risk
description: "OpenClaw 重构 PR 风险较高"
symptom: "标签包含 size: L/XL"
trigger_keywords:
  - "size: L"
  - "size: XL"
  - "refactor"
fix_action: "1) 拆分为多个小 PR; 2) 提供详细测试; 3) 提供回滚方案"
source_pr: "openclaw/openclaw#108026"
severity: medium
evidence:
  - "openclaw #108026: 重构 telegram 插件，size: XL"
learned_at: 2026-07-15
---

## 反模式说明

大型重构 PR 风险较高，可能引入回归问题。

### 触发条件
- 修改多个文件
- 修改核心逻辑
- 缺少充分测试

### 如何避免
1. 拆分为多个小 PR
2. 提供详细测试
3. 提供回滚方案
