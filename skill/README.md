---
type: Skill
name: pr-genius
description: PR 评估和建议工具 — 基于历史反模式和成功模式
version: 1.0.0
author: zsxh1990
---

# PR Genius Skill

一键评估 PR 的成功率，提供改进建议。

## 安装

### Claude Code

```bash
# 方式 1: 全局安装
claude skill install github:zsxh1990/pr-genius/skill

# 方式 2: 项目内安装
cd your-project
claude skill add github:zsxh1990/pr-genius/skill
```

### 手动安装

```bash
# 克隆仓库
git clone https://github.com/zsxh1990/pr-genius.git

# 复制 skill 文件到你的项目
cp -r pr-genius/skill ~/.claude/skills/pr-genius
```

## 使用

### 评估 PR

```bash
# 评估一个 PR
/pr-genius eval "feat: add error handler for Vite" --repo vitejs/vite

# 评估当前分支的改动
/pr-genius eval --branch

# 评估已提交的 PR
/pr-genius eval --pr vitejs/vite#22701
```

### 获取建议

```bash
# 获取改进建议
/pr-genius suggest "feat: add error handler for Vite" --repo vitejs/vite

# 获取成功模式参考
/pr-genius suggest --type success --repo Ikalus1988/MisakaNet

# 获取反模式警告
/pr-genius suggest --type anti-pattern --repo vitejs/vite
```

### 生成 PR 描述

```bash
# 根据改动生成 PR 描述
/pr-genius describe --branch

# 根据 Issue 生成 PR 描述
/pr-genius describe --issue Ikalus1988/MisakaNet#356
```

## 功能

### 1. PR 评估

- **成功率预测**: 基于历史数据预测 PR 被合并的概率
- **反模式检查**: 检查 PR 是否命中已知反模式
- **成功模式匹配**: 检查 PR 是否符合成功模式
- **仓库适配**: 检查 PR 是否符合目标仓库的要求

### 2. 改进建议

- **反模式规避**: 如果命中反模式，提供规避建议
- **成功模式参考**: 提供类似的成功案例参考
- **仓库要求**: 列出目标仓库的具体要求
- **测试建议**: 建议需要添加的测试

### 3. PR 描述生成

- **自动结构化**: 根据改动自动生成结构化的 PR 描述
- **Issue 关联**: 自动关联相关的 Issue
- **验收标准**: 自动生成验收标准 checklist
- **测试说明**: 自动生成测试说明

## 数据来源

- **反模式库**: `anti-patterns/` — 11 个反模式
- **成功模式库**: `success-patterns/` — 10 个成功模式
- **仓库配置**: `{org}-{repo}/` — 各仓库的具体要求
- **经验文档**: `docs/` — 复盘和方法论文档

## 示例

### 评估一个 PR

```
$ /pr-genius eval "feat: add error handler for Vite" --repo vitejs/vite

## PR 评估结果

### 成功率预测: 15% (低)

### 反模式命中
- ⚠️ cosmetic-no-user-pain: "I don't think this is useful" 
  - 历史案例: vitejs/vite#22701
  - 建议: 先在 Issue 中确认维护者认为这是个问题

### 成功模式匹配
- ❌ 未匹配任何成功模式

### 改进建议
1. 先在 Issue 中讨论方案
2. 确认维护者认为这是个需要解决的问题
3. 添加用户痛点的描述
4. 考虑是否是 cosmetic 改动
```

### 获取建议

```
$ /pr-genius suggest "feat: add error handler for Vite" --repo vitejs/vite

## 改进建议

### 1. 避免 cosmetic-no-user-pain 反模式

**问题**: 提交了美化/格式化/输出改进，但没有解决真实用户痛点。

**建议**:
- 先在 Issue 或 Discussion 中确认维护者认为这是一个需要解决的问题
- 不要自己假设"这个改进有价值"
- 检查：有没有用户报过这个痛点？

### 2. 参考成功模式

**推荐模式**: misakanet-reputation-system
- 完整功能模块（算法+测试+文档）
- 解决 Issue 中明确的需求
- 单一 commit，干净的 PR

### 3. 目标仓库要求

**vitejs/vite**:
- DCO sign-off
- CI 通过
- 维护者 review
```

## 更新

```bash
# 更新 skill
claude skill update pr-genius

# 或手动更新
cd pr-genius && git pull
```
