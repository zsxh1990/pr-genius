---
type: Success Pattern
key: agentclaimguard-langchain-middleware
description: "功能贡献：从 Issue 中实现中间件适配器"
success_factors:
  - "解决 Issue #2 中明确的需求"
  - "实现 LangChain middleware 适配器"
  - "完整的文档和示例"
  - "单一 commit，干净的 PR"
repo_requirements:
  - "DCO sign-off (git commit -s)"
  - "CI 通过"
source_pr: konoeph/AgentClaimGuard#8
metrics:
  additions: 246
  deletions: 0
  commits: 1
  review_comments: 0
  time_to_merge: "1天"
learned_at: 2026-07-09
---

## 成功案例

### PR #8: add ClaimGuardMiddleware adapter

**背景**: Issue #2 要求添加 LangChain middleware 适配器，以便在 agent 流程中插入 AgentClaimGuard。

**成功因素**:

1. **解决明确需求**: Issue #2 详细描述了需求
2. **完整实现**:
   - `ClaimGuardMiddleware` 类
   - 支持在 agent 流程的任意位置插入验证
   - 不需要单独包装每个 Runnable
3. **文档和示例**: 完整的使用说明
4. **单一 commit**: 一个干净的 commit

**关键代码**:
```python
class ClaimGuardMiddleware:
    """LangChain middleware for inserting AgentClaimGuard into agent flows."""
    
    def __init__(self, guard):
        self.guard = guard
    
    async def __call__(self, input, **kwargs):
        # Verify input
        await self.guard.verify(input)
        # Process
        result = await self.next(input, **kwargs)
        # Verify output
        await self.guard.verify(result)
        return result
```

## 可复用模式

1. **Issue 驱动**: 先找到明确的 Issue，再实现
2. **完整实现**: 实现核心功能 + 文档 + 示例
3. **单一 commit**: 保持 PR 干净
4. **解决实际问题**: 解决用户在 Issue 中提出的具体问题
