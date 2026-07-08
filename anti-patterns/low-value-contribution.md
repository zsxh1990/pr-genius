---
type: Anti-Pattern
key: low-value-contribution
symptom: |
  "we don't accept this type of contribution" / "not aligned with project goals" / "closing"
root_cause: 提交的贡献不符合项目的核心价值或维护者的需求。可能是文档、测试、重构等"外围"贡献，但维护者更关注核心功能。
trigger_keywords:
  - "not aligned"
  - "project goals"
  - "we don't accept"
  - "closing"
  - "won't merge"
fix_action: 在提 PR 前，先研究：(1) 项目的 CONTRIBUTING.md (2) 维护者最近合并的 PR 类型 (3) 项目的核心价值和优先级
source_pr: patchwork-dev/patchwork-os#870
prevention: "提 PR 前检查：(1) 项目的 CONTRIBUTING.md 是否接受这类贡献？(2) 维护者最近合并了什么类型的 PR？(3) 项目的核心价值是什么？"
learned_at: 2026-07-08
---

## 案例

### patchwork-dev/patchwork-os #870 — design doc
- **提交内容**: 添加设计文档
- **拒绝原因**: 维护者不接受这类贡献
- **教训**: 有些项目不接受文档/设计类贡献，只接受代码

### patchwork-dev/patchwork-os #890/#891 — parity tests
- **提交内容**: 添加跨层/连接器的 parity 测试
- **拒绝原因**: 维护者不接受这类测试贡献
- **教训**: 有些项目不接受外部测试贡献，只接受核心功能代码

## 反模式特征

1. **文档/设计类贡献**: 有些项目不接受外部文档贡献
2. **测试类贡献**: 有些项目不接受外部测试贡献
3. **重构类贡献**: 有些项目不接受外部重构贡献
4. **不符合项目优先级**: 贡献的方向不是项目当前关注的

## 自检清单

提 PR 前检查：
- [ ] 项目的 CONTRIBUTING.md 是否接受这类贡献？
- [ ] 维护者最近合并了什么类型的 PR？
- [ ] 项目的核心价值和优先级是什么？
- [ ] 贡献是否符合项目当前的关注点？
