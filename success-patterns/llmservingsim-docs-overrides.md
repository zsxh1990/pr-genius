---
type: Success Pattern
key: llmservingsim-docs-overrides
description: "文档贡献：补充缺失的配置文档 + 示例"
success_factors:
  - "补充 README 中缺失的配置说明"
  - "添加实际可用的示例配置"
  - "解释优先级规则和验证门"
  - "单一 commit，干净的 PR"
repo_requirements:
  - "DCO sign-off (git commit -s)"
  - "CI 通过"
source_pr: casys-kaist/LLMServingSim#38
metrics:
  additions: 95
  deletions: 2
  commits: 1
  review_comments: 0
  time_to_merge: "1天"
learned_at: 2026-07-09
---

## 成功案例

### PR #38: add per-instance runtime overrides section + example config

**背景**: README 中缺少 per-instance runtime overrides 的说明。

**成功因素**:

1. **补充缺失文档**: README 中没有说明 per-instance 配置
2. **详细说明**:
   - 优先级规则：`instance.get(field, args.field)`
   - 无限语义：`0` 表示无限（通过 `_runtime_limit` helper）
   - 验证门：`enable_sub_batch_interleaving: true` 需要 `enable_attn_offloading: true`
3. **示例配置**: 添加了 heterogeneous 示例配置
4. **单一 commit**: 一个干净的 commit

**关键内容**:
```markdown
## Per-instance runtime overrides

Precedence rule: `instance.get(field, args.field)` — per-instance values take precedence over CLI defaults.

Unlimited semantics: `0` means unlimited (via `_runtime_limit` helper).

Validation gates: `enable_sub_batch_interleaving: true` requires `enable_attn_offloading: true`.
```

## 可复用模式

1. **补充缺失文档**: 找到 README 中缺失的说明
2. **详细说明**: 解释配置的语义和规则
3. **添加示例**: 提供实际可用的示例配置
4. **单一 commit**: 保持 PR 干净
