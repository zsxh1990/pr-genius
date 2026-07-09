---
type: Success Pattern
key: misakanet-reputation-system
description: "完整功能模块：算法实现 + 单元测试 + 文档"
success_factors:
  - "解决 Issue #356 中明确的需求"
  - "完整的算法实现（sigmoid cap + time decay）"
  - "14 个单元测试覆盖边界情况"
  - "详细的文档（公式 + 使用指南）"
  - "单一 commit，干净的 PR"
repo_requirements:
  - "DCO sign-off (git commit -s)"
  - "YAML frontmatter"
  - "质量检查通过"
source_pr: Ikalus1988/MisakaNet#413
metrics:
  additions: 572
  deletions: 0
  commits: 1
  review_comments: 0
  time_to_merge: "1天"
learned_at: 2026-07-09
---

## 成功案例

### PR #413: reputation system with reuse signals and anti-gaming

**背景**: Issue #356 要求建立贡献者声誉系统，基于课程复用而非 PR 数量。

**成功因素**:

1. **解决明确需求**: Issue #356 详细描述了需求和验收标准
2. **完整实现**:
   - `scripts/reputation.py` — 评分引擎（sigmoid cap + time decay）
   - `tests/test_reputation.py` — 14 个单元测试
   - `docs/reputation.md` — 公式文档和使用指南
3. **单一 commit**: 一个干净的 commit，包含所有相关文件
4. **测试覆盖**: 测试了边界情况（新贡献者、老贡献者、批量提交）

**关键代码**:
```python
# Anti-gaming: sigmoid cap
def sigmoid_cap(x, k=0.5, midpoint=10):
    return 1.0 / (1.0 + math.exp(-k * (x - midpoint)))

# Time decay: 90-day half-life
def time_decay(created, now=None):
    days = max((now - dt).days, 0)
    return math.pow(0.5, days / HALF_LIFE_DAYS)
```

**验收标准**:
- [x] 每个贡献者的声誉分数可见
- [x] 更高的声誉 = 搜索质量提升（sigmoid 封顶）
- [x] 反游戏：sigmoid 限制每个 PR 的权重
- [x] 时间衰减：近期贡献权重更高
- [x] 文档化公式
- [x] 测试覆盖：新贡献者、长期衰减、单个大 PR

## 可复用模式

1. **Issue 驱动**: 先找到明确的 Issue，再实现
2. **完整交付**: 代码 + 测试 + 文档
3. **单一 commit**: 保持 PR 干净
4. **测试覆盖**: 覆盖边界情况
