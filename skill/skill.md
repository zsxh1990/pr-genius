---
type: Skill
name: pr-genius
description: PR 评估和建议工具 — 基于历史反模式和成功模式
version: 1.1.0
author: zsxh1990
---

# PR Genius Skill

一键评估 PR 的成功率，提供改进建议。

## 使用方法

### 评估 PR

```
/pr-genius eval "feat: add error handler for Vite" --repo vitejs/vite
```

### 获取建议

```
/pr-genius suggest "feat: add error handler for Vite" --repo vitejs/vite
```

### 生成 PR 描述

```
/pr-genius describe "feat: add error handler" --repo vitejs/vite --issue vitejs/vite#1234
```

## 实现

当用户调用 `/pr-genius` 时，执行以下步骤：

1. **解析参数**: 提取 PR 标题、描述、目标仓库
2. **加载知识库**: 加载反模式库和成功模式库
3. **检查反模式**: 检查 PR 是否命中已知反模式
4. **检查成功模式**: 检查 PR 是否符合成功模式
5. **预测成功率**: 基于历史数据预测 PR 被合并的概率
6. **生成建议**: 基于反模式和成功模式生成改进建议

## 示例

### 评估一个 PR

```
$ /pr-genius eval "feat: add error handler for Vite" --repo vitejs/vite

## PR 评估结果

### 成功率预测: 15% (低)

### 反模式命中
- ⚠️ **cosmetic-no-user-pain**: "I don't think this is useful"
  - 建议: 先在 Issue 中确认维护者认为这是个问题
  - 历史案例: vitejs/vite#22701

### 成功模式匹配
- ❌ 未匹配任何成功模式

### 改进建议
### 避免 cosmetic-no-user-pain 反模式

**问题**: 提交了美化/格式化/输出改进，但没有解决真实用户痛点。

**建议**: 先在 Issue 或 Discussion 中确认维护者认为这是一个需要解决的问题。

### 参考成功模式

- **misakanet-reputation-system**: 完整功能模块（算法+测试+文档）
  - 成功因素:
    - 解决 Issue 中明确的需求
    - 完整的实现（代码 + 测试 + 文档）
    - 单一 commit，干净的 PR

### 通用建议

1. **先 Issue 后 PR**: 先在 Issue 中讨论方案
2. **完整交付**: 代码 + 测试 + 文档
3. **单一 commit**: 保持 PR 干净
4. **DCO sign-off**: 使用 `git commit -s`
```

## 数据来源

- **反模式库**: 11 个反模式，来自 18 个被拒 PR
- **成功模式库**: 10 个成功模式，来自 21 个已合并 PR
- **仓库配置**: 各仓库的具体要求
- **经验文档**: 复盘和方法论文档
