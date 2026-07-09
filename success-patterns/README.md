---
type: Success Pattern Bundle
title: 成功模式索引
description: PR 成功合并的正向样本（可复用的成功信号）
version: 0.1.0
created: 2026-07-09
---

# Success Patterns 成功模式库

> **目的**：当 Agent 准备提 PR 时，参考成功案例的模式，提高合并成功率。
> **原则**：**只填真实案例**——每个成功模式都有对应的已合并 PR。

## Schema

每个成功模式是 1 个 `success-patterns/<key>.md`：

```yaml
---
type: Success Pattern
key: <unique-slug>
description: "<一句话描述成功模式>"
success_factors: [<string>]  # 成功的关键因素
repo_requirements: "<仓库的具体要求>"
source_pr: <org>/<repo>#<num>  # 成功案例来源 PR
metrics:
  additions: <number>
  deletions: <number>
  commits: <number>
  review_comments: <number>
  time_to_merge: "<天数>"
learned_at: YYYY-MM-DD
---
```

## 已有成功模式（5 条）

| Key | 仓库 | 描述 |
|-----|------|------|
| [misakanet-reputation-system](./misakanet-reputation-system.md) | Ikalus1988/MisakaNet | 完整功能模块（算法+测试+文档） |
| [misakanet-frontmatter-normalization](./misakanet-frontmatter-normalization.md) | Ikalus1988/MisakaNet | 批量修复同一类问题 |
| [misakanet-lesson-contribution](./misakanet-lesson-contribution.md) | Ikalus1988/MisakaNet | 脱敏泛化的技术教训 |
| [misakanet-mcp-quickstart](./misakanet-mcp-quickstart.md) | Ikalus1988/MisakaNet | 文档+测试+配置示例 |
| [mcp-gateway-secret-uri-safe](./mcp-gateway-secret-uri-safe.md) | agentic-community/mcp-gateway-registry | 安全修复（URI-safe 字符约束） |

## 成功模式分类

### 1. 功能模块（高价值）
- 完整的算法实现
- 单元测试覆盖
- 文档和使用指南
- 示例：reputation system, MCP quickstart

### 2. 批量修复（中价值）
- 修复同一类问题的多个实例
- 保持一致性
- 示例：frontmatter normalization

### 3. 技术教训（中价值）
- 脱敏泛化的真实案例
- 可复用的解决方案
- 示例：lesson contribution

### 4. 安全修复（高价值）
- 修复安全漏洞
- 添加测试覆盖
- 示例：secret URI-safe

## 与反模式库的关系

- **反模式库**: 避免重复错误
- **成功模式库**: 复制成功经验
- **两者结合**: 提高 PR 合并率
