---
type: Success Pattern
key: mcp-gateway-secret-uri-safe
description: "安全修复：URI-safe 字符约束 + 测试覆盖"
success_factors:
  - "修复 Issue #1354 中明确的安全问题"
  - "完整的安全修复（Lambda + Terraform）"
  - "测试覆盖（编译检查 + 字符检查）"
  - "CI 修复迭代（3 次修复后全绿）"
repo_requirements:
  - "DCO sign-off (git commit -s)"
  - "CI 全部通过"
  - "CodeRabbit review"
source_pr: agentic-community/mcp-gateway-registry#1362
metrics:
  additions: 135
  deletions: 12
  commits: 8
  review_comments: 1
  time_to_merge: "1天"
learned_at: 2026-07-09
---

## 成功案例

### PR #1362: constrain secret characters to URI-safe, AWS-safe set

**背景**: Issue #1354 报告 RDS/DocumentDB 密码包含 URI 保留字符，导致认证失败。

**成功因素**:

1. **解决明确需求**: Issue #1354 详细描述了安全问题
2. **完整修复**:
   - `rotate-rds/index.py` — RDS Lambda 修复
   - `rotate-documentdb/index.py` — DocumentDB Lambda 修复
   - `secret-rotation.tf` — Terraform 环境变量
   - `variables.tf` — 密码验证规则
3. **测试覆盖**:
   - `test_secret_rotation_chars.py` — 编译检查 + 字符检查
4. **CI 修复迭代**:
   - 第 1 次：模块名错误 (`rotate_rds_index` → `index`)
   - 第 2 次：boto3 导入问题（删除 Lambda import）
   - 第 3 次：正则转义问题（`.*?` → `(?:[^\\]|\\.)*?`）

**排除字符集**:
```python
EXCLUDE_CHARACTERS = "/@\"'+:?#&!=% "
```

**验收标准**:
- [x] RDS Lambda 默认排除集包含所有必需字符
- [x] DocumentDB Lambda 默认排除集包含所有必需字符
- [x] 两个 Lambda 使用相同的默认值
- [x] 编译检查通过
- [x] CI 全部通过

## 可复用模式

1. **安全优先**: 安全修复是高价值贡献
2. **完整修复**: 修复所有相关文件
3. **测试覆盖**: 验证修复正确性
4. **CI 修复迭代**: 不要放弃，持续修复直到 CI 通过
