---
type: Anti-Pattern
key: contribai-ethical-review-failed
symptom: |
  改动有 ethical concern (隐私 / OSINT / 监控 / security research), maintainer 或 maintainer 委员会拒绝。Close 关键词: "ethical concern", "we can't take this", "out of scope (ethics)", "consider implications"
root_cause: 未考虑改动的伦理影响 (隐私 / surveillance / 双刃剑), 提了 maintainer 拒收的方向。
trigger_keywords:
  - "ethical concern"
  - "we can't take this"
  - "out of scope (ethics)"
  - "consider implications"
  - "this could be misused"
fix_action: |
  1) 评估改动伦理影响 (privacy / surveillance / dual-use)
  2) 加 ethics statement + acceptable use policy
  3) 在 README 强调 responsible disclosure
  4) 考虑 opt-in / opt-out 设计
source_pr: "maigret #N 等 OSINT 仓 ~15% close 是 ethical concern"
prevention: |
  提 PR 前:
  - 评估改动是否会被 misuse (监控 / surveillance)
  - 加 ethics statement + AUP
  - README 强调 responsible disclosure
  - opt-in vs opt-out 设计
learned_at: 2026-07-19
---

## ContribAI 实证 close 数据

- OSINT / 隐私工具 (maigret): ~15% close 是 ethical concern
- security research: 类似比例
- AI training data scraping: 越来越多 maintainer 拒绝
- facial recognition / biometric: 几乎必拒

## 反模式特征

1. **未考虑伦理** — 改动是 dual-use (善意 + 恶意)
2. **未加 ethics statement** — README 没写 acceptable use
3. **未设计 opt-in** — 默认开, 不让用户拒绝
4. **未提供 disclosure 路径** — 用户报告 misuse 没渠道
5. **surveillance 倾向** — 被识别为监控工具

## 自检清单

提 PR 前:
- [ ] 评估 misuse 风险
- [ ] README 写 ethics / AUP?
- [ ] opt-in vs opt-out?
- [ ] disclosure 渠道?
- [ ] maintainer 可能怎么评估?

## 关联

- soxoj-maigret profile: ethical review 是 close 原因之一
