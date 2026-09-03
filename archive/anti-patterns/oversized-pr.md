---
type: Anti-Pattern
key: oversized-pr
description: "PR 变更行数过多，难以审查"
symptom: "PR 变更 >500 行，维护者要求拆分或拒绝审查"
trigger_keywords:
  - "split"
  - "smaller"
  - "too large"
  - "too big"
  - "break down"
fix_action: "拆分为多个小 PR，每个 PR 只做一件事。建议单个 PR <300 行，最多 5-10 个文件"
source_pr: ""
severity: high
evidence:
  - "多个大仓维护者明确要求 PR <500 行"
  - "React/Kubernetes/Go 等项目 CONTRIBUTING.md 均有 PR 大小限制"
learned_at: 2026-08-11
---

## 反模式说明

**问题**: PR 变更行数过多，超出维护者审查能力

### 关键特征

- 单个 PR 变更 >500 行代码
- 涉及 >10 个文件
- 包含多个不相关的变更
- 缺乏清晰的拆分逻辑

### 为什么被拒绝

1. **审查负担重**: 维护者无法在合理时间内完成审查
2. **容易引入 bug**: 大 PR 更难发现错误
3. **回滚困难**: 出问题时难以定位具体变更
4. **阻塞其他 PR**: 大 PR 占用审查资源

### 如何避免

1. **单个 PR 只做一件事**: 遵循 Single Responsibility Principle
2. **控制 PR 大小**: 
   - 理想: <100 行, 1-3 文件
   - 可接受: <300 行, 5-10 文件
   - 警告: 300-500 行
   - 拒绝: >500 行
3. **拆分策略**:
   - 先提交基础设施/重构
   - 再提交功能实现
   - 最后提交测试和文档
4. **使用 feature flags**: 大功能可以通过 feature flag 分阶段合并

### 参考案例

- React: CONTRIBUTING.md 要求 PR <400 行
- Kubernetes: PR >500 行会被标记 needs-rebase
- Go: 大 PR 会被要求拆分
