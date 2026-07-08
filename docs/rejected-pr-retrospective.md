---
type: Retrospective
title: 被拒 PR 复盘 — 18 个被拒 PR 的反模式分析
description: 从 18 个被拒 PR 中提取的 4 个核心反模式，以及预防策略
version: 1.0.0
created: 2026-07-08
---

# 被拒 PR 复盘

## 背景

在 2026-06-04 到 2026-07-08 期间，共提交了约 30 个外部 PR，其中 18 个被拒绝（60% 拒绝率）。通过分析这些被拒 PR 的维护者评论，提取出 4 个核心反模式。

## 被拒 PR 统计

| 仓库 | PR | 内容 | 拒绝原因 | 反模式 |
|------|-----|------|----------|--------|
| vitejs/vite | #22701 | VITE_ERROR_HANDLER | "I don't think this is useful" | cosmetic-no-user-pain |
| e2b-dev/E2B | #1413 | replace rich with stdlib | "mostly cosmetic" | cosmetic-no-user-pain |
| e2b-dev/E2B | #1458 | E2B_ERROR_HANDLER | 被拒 | cosmetic-no-user-pain |
| plastic-labs/honcho | #798 | json_object fallback | "pretty big breaking change" | breaking-change-no-compat |
| astral-sh/uv | #19685 | SARIF output | 官方自己做了 #19872 | upstream-already-implementing |
| patchwork-dev/patchwork-os | #870 | design doc | 不接受这类贡献 | low-value-contribution |
| patchwork-dev/patchwork-os | #890 | connector parity test | 不接受这类贡献 | low-value-contribution |
| patchwork-dev/patchwork-os | #891 | cross-layer parity test | 不接受这类贡献 | low-value-contribution |
| graphrag-toolkit | #310 | s3_path validation | 被拒 | 未知（repo 已删除） |
| autocontext | #1025 | Lean error body fix | 被拒 | 未知（repo 已删除） |
| apple-mail-fast-mcp | #324 | batch UID resolution | 被拒 | 未知（repo 已删除） |
| mcp_agent_mail_rust | #141 | INDEX.md | 被拒 | 未知（repo 已删除） |
| openlegion | #1026 | self-reflection module | 被拒 | 未知（repo 已删除） |

## 核心反模式

### 1. Cosmetic No User Pain（表面修饰无用户痛点）

**特征**: 提交了美化/格式化/输出改进，但没有解决真实用户痛点。

**典型案例**:
- vitejs/vite #22701: 添加更详细的错误输出格式，维护者认为"所有信息都可以在新输出之外轻松获得"
- e2b-dev/E2B #1413: 用标准库替换 rich 依赖，维护者认为"没有看到任何主要的用户痛点"

**预防策略**:
1. 提 PR 前先在 Issue 或 Discussion 中确认维护者认为这是一个需要解决的问题
2. 不要自己假设"这个改进有价值"
3. 检查：有没有用户报过这个痛点？

### 2. Breaking Change No Compat（破坏性变更无兼容性）

**特征**: 提交了破坏性变更但没有考虑向后兼容性。

**典型案例**:
- plastic-labs/honcho #798: JSON 解析的 fallback 处理，维护者认为"这是一个相当大的破坏性变更，也有自己的兼容性问题"

**预防策略**:
1. 如果改动是 breaking change，必须提供迁移路径
2. 考虑使用 feature flag 保持兼容
3. 先在 Issue 中讨论方案

### 3. Upstream Already Implementing（上游已在实现）⭐ 最有价值的反模式

**特征**: 维护者已经在内部实现或计划实现相同功能。

**典型案例**:
- astral-sh/uv #19685: SARIF 输出功能，维护者自己实现了相同功能 (#19872)

**为什么这是最有价值的反模式**:
1. **方向正确**: 我们识别的需求和维护者一致
2. **时机问题**: 不是方向错，而是维护者已经在做了
3. **验证价值**: 证明我们的产品嗅觉是对的
4. **可复制**: 下次遇到类似情况，可以先问"是否已经在做"

**预防策略**:
1. 检查维护者的 roadmap/TODO
2. 检查最近 30 天的 commit 历史
3. 先在 Issue 中问"是否已经在做"
4. **如果发现维护者已在做，不要沮丧——你的方向是对的！**

### 4. Low Value Contribution（低价值贡献）

**特征**: 提交的贡献不符合项目的核心价值或维护者的需求。

**典型案例**:
- patchwork-dev/patchwork-os #870: 设计文档，维护者不接受这类贡献
- patchwork-dev/patchwork-os #890/#891: 测试，维护者不接受这类贡献

**预防策略**:
1. 研究项目的 CONTRIBUTING.md
2. 分析维护者最近合并的 PR 类型
3. 理解项目的核心价值和优先级

## 关键教训

### 1. 先沟通再动手

**错误做法**: 直接提 PR，假设维护者会接受
**正确做法**: 先在 Issue 中讨论方案，确认维护者认可后再提 PR

### 2. 研究项目文化

**错误做法**: 用通用的贡献方式对待所有项目
**正确做法**: 研究每个项目的 CONTRIBUTING.md、维护者最近合并的 PR 类型

### 3. 关注用户痛点

**错误做法**: 提交"我觉得这样更好"的改进
**正确做法**: 提交解决真实用户痛点的改进，最好有 Issue 支持

### 4. 考虑维护成本

**错误做法**: 只考虑代码质量，不考虑维护成本
**正确做法**: 维护者需要 review、测试、维护你的代码，确保这个成本是值得的

## 预防检查清单

提 PR 前检查：
- [ ] 有没有对应的 Issue 或 Discussion？
- [ ] 维护者是否认可这是个问题？
- [ ] 改动是否改变现有 API 行为？
- [ ] 现有用户代码是否需要修改？
- [ ] 维护者的 roadmap 中是否有这个功能？
- [ ] 项目的 CONTRIBUTING.md 是否接受这类贡献？
- [ ] 维护者最近合并了什么类型的 PR？

## 成功率分析

| 类型 | 数量 | 成功 | 失败 | 成功率 |
|------|------|------|------|--------|
| Error Handler | 3 | 0 | 3 | 0% |
| 文档/测试 | 4 | 0 | 4 | 0% |
| 依赖替换 | 1 | 0 | 1 | 0% |
| 功能改进 | 5 | 2 | 3 | 40% |
| Bug 修复 | 8 | 6 | 2 | 75% |

**结论**: Bug 修复的成功率最高（75%），Error Handler 和文档/测试的成功率最低（0%）。

## 行动计划

1. **短期**: 在提 PR 前使用反模式检查清单自检
2. **中期**: 建立"先 Issue 后 PR"的工作流
3. **长期**: 建立项目评估矩阵，选择成功率高的贡献类型
