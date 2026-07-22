---
type: Anti-Pattern
key: maintainer-internal-handling
symptom: |
  维护者明确表示会内部处理某个 issue，外部 PR 被关闭。Close 关键词: "handle internally", "we'll handle this", "keep in sync", "internal process"
root_cause: |
  某些类型的改动（依赖版本、安全补丁、核心配置）维护者有特定的内部流程，不希望外部贡献者介入。这类 issue 虽然是 open 状态，但不接受外部 PR。
trigger_keywords:
  - "handle internally"
  - "we'll handle this"
  - "keep in sync"
  - "internal process"
  - "we'll take care of it"
  - "managed internally"
fix_action: |
  1) 提 PR 前先在 issue 评论询问是否接受外部贡献
  2) 如果维护者说 "we'll handle internally"，不要提 PR
  3) 转向其他 issue
source_pr: "huggingface/transformers#47434 (tokenizers 版本约束)"
prevention: |
  提 PR 前必做:
  - 检查 issue 评论，看维护者是否已表态
  - 如果是依赖/安全相关，先问 "Is this open for external contribution?"
  - 不要假设 open issue = 接受外部 PR
learned_at: 2026-07-22
---

## 详细说明

### 场景

贡献者发现一个 open issue（如依赖版本约束问题），认为修复简单，直接提了 PR。但维护者在 issue 评论中明确表示会内部处理，导致 PR 被关闭。

### 真实案例

**huggingface/transformers #47429** — tokenizers 版本约束

- Issue: `tokenizers<=0.23.0` 阻塞了 `0.23.1`（包含 XSS 安全修复）
- 修复: 改 `<=0.23.0` 为 `<0.24.0`（2 行改动）
- 维护者 Rocketknight1: "We'll handle tokenizers version bumps internally! They need to be kept in sync"
- 结果: PR #47434 被关闭，另一个 PR #47456 也会被关

### 为什么维护者要内部处理

1. **依赖同步**: tokenizers 版本需要与 transformers 内部逻辑同步
2. **安全流程**: 安全相关改动有内部审批流程
3. **发布节奏**: 依赖更新需要配合发布计划
4. **测试矩阵**: 内部有更全面的测试环境

### 如何识别

- Issue 评论中有维护者说 "I'll handle this" 或 "We'll handle internally"
- Issue 标签有 "internal" 或 "maintainer-only"
- Issue 是关于依赖/安全/核心配置的
- Issue 已经有人评论 "I'd like to work on this" 但维护者没有 assign

### 预防措施

1. **提 PR 前先评论**: "Is this open for external contribution?"
2. **检查评论**: 看维护者是否已表态
3. **识别模式**: 依赖/安全/核心配置类 issue 通常不接受外部 PR
4. **转向其他**: 如果维护者说内部处理，找其他 issue
