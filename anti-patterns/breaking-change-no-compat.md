---
type: Anti-Pattern
key: breaking-change-no-compat
symptom: "pretty big breaking change" / "has its own set of compatibility issues" / "unnecessary at the moment"
root_cause: 提交了破坏性变更（breaking change）但没有考虑向后兼容性。维护者担心这会影响现有用户，即使改动本身是合理的。
trigger_keywords:
  - "breaking change"
  - "compatibility issues"
  - "unnecessary at the moment"
  - "would visit this in the future"
  - "closing this"
fix_action: 如果改动是 breaking change，必须：(1) 提供迁移路径 (2) 保持向后兼容 (3) 在 Issue 中先讨论方案 (4) 考虑 feature flag
source_pr: plastic-labs/honcho#798
prevention: "提 PR 前检查：(1) 改动是否改变现有 API 行为？(2) 现有用户代码是否需要修改？(3) 能否通过 feature flag 保持兼容？"
learned_at: 2026-07-08
---

## 案例

### plastic-labs/honcho #798 — json_object fallback
- **提交内容**: 为 JSON 解析添加 fallback 处理
- **拒绝原因**: akattelu: "The way this is written right now, it is a pretty big breaking change that also has its own set of compatibility issues. This seems unnecessary at the moment but would visit this in the future if it becomes an issue. Closing this."
- **教训**: 即使改动是"修复"，如果改变了现有行为，也会被认为是 breaking change

## 反模式特征

1. **改变现有 API 行为**: 函数返回值、参数、异常类型发生变化
2. **没有迁移路径**: 现有用户代码会因为升级而崩溃
3. **没有 feature flag**: 无法让现有用户选择是否启用新行为
4. **没有讨论方案**: 直接提 PR，没有先在 Issue 中讨论

## 自检清单

提 PR 前检查：
- [ ] 改动是否改变现有 API 行为？
- [ ] 现有用户代码是否需要修改？
- [ ] 能否通过 feature flag 保持兼容？
- [ ] 有没有在 Issue 中先讨论方案？
- [ ] 有没有提供迁移文档？
