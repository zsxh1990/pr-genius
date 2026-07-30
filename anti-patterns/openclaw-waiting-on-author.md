---
type: Anti-Pattern
key: openclaw-waiting-on-author
description: "OpenClaw PR 等待作者响应"
symptom: "状态变为 waiting on author"
trigger_keywords:
  - "waiting on author"
  - "needs author response"
fix_action: "1) 及时回复 maintainer 评论; 2) 更新代码; 3) 提供补充信息"
source_pr: "openclaw/openclaw#90421, openclaw/openclaw#87304"
severity: medium
evidence:
  - "openclaw #90421: 等待作者响应"
  - "openclaw #87304: 等待作者响应"
learned_at: 2026-07-15
---

## 反模式说明

PR 等待作者响应 maintainer 的评论或要求。

### 触发条件
- 未及时回复 maintainer 评论
- 未按要求修改代码
- 未提供补充信息

### 如何避免
1. 及时回复 maintainer 评论
2. 按要求修改代码
3. 提供补充信息
