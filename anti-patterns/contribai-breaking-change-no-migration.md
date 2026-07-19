---
type: Anti-Pattern
key: contribai-breaking-change-no-migration
symptom: |
  提交了 breaking change 但没提供 migration path / feature flag / 讨论。Close 关键词: "breaking change", "compatibility issues", "would need a deprecation cycle"
root_cause: 改了现有 API 行为但没考虑现有用户, 也没在 issue 讨论。
trigger_keywords:
  - "breaking change"
  - "compatibility issues"
  - "would need a deprecation cycle"
  - "this changes existing behavior"
  - "users will need to migrate"
fix_action: |
  1) 改动如果破坏 BC, 必须:
     - 提供 migration path (codemod / doc)
     - 用 feature flag 默认关
     - 加 deprecation warning
  2) 在 issue 先讨论 deprecation 周期
  3) 至少 2 release 周期才移除旧 API
source_pr: "pandas-dev/pandas ~10% close 是 breaking change"
prevention: |
  提 PR 前:
  - 改动是否改变现有 API 行为?
  - 现有用户代码是否需要修改?
  - 能否用 feature flag 默认关?
  - 有没有 migration 路径?
  - 至少 2 release 周期才移除旧 API
learned_at: 2026-07-19
---

## ContribAI 实证 close 数据

- pandas-dev/pandas: ~10% close 是 breaking change (BC 不收)
- pallets/flask: ~5% close 是 breaking change
- 大型 framework: 5-10% close 是 breaking change
- microG / systemd: breaking change 几乎必 close (产品决策)

## 反模式特征

1. **改默认行为** — 现有用户依赖旧行为
2. **移除 API 不弃用** — 没 deprecation warning
3. **没 codemod** — 用户手动迁移痛苦
4. **没 feature flag** — 不能 opt-in
5. **没 release cycle** — 立刻移除旧 API

## 自检清单

提 PR 前:
- [ ] 改动是否改变现有 API 行为?
- [ ] 现有用户代码是否需要修改?
- [ ] feature flag 默认关, 用户 opt-in?
- [ ] codemod 自动迁移?
- [ ] 至少 2 release 周期 deprecation?
- [ ] 在 issue 讨论过 BC 策略?

## 关联

- 已有: `anti-patterns/breaking-change-no-compat.md` (honcho#798)
