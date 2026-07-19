---
type: Anti-Pattern
key: contribai-incomplete-readme-contributing
symptom: |
  提 PR 时没读完整 README / CONTRIBUTING, 漏了关键 setup / testing / commit 规范。Close 关键词: "please read CONTRIBUTING", "missing setup", "wrong commit format", "CI failed because of missing setup"
root_cause: 提 PR 前未读 README / CONTRIBUTING 完整, 漏了项目特定 setup 步骤 (如 DCO / CHANGES / format)。
trigger_keywords:
  - "please read CONTRIBUTING"
  - "missing setup"
  - "wrong commit format"
  - "DCO missing"
  - "missing CHANGES entry"
fix_action: |
  1) 读 README.md 完整
  2) 读 CONTRIBUTING.md 完整
  3) 看最近 10 个 merged PR 的格式
  4) 跑 setup script (如果有)
source_pr: "ContribAI 14 closed PR 中 ~15% 是 incomplete setup"
prevention: |
  提 PR 前:
  - 读 README + CONTRIBUTING 完整
  - 看最近 merged PR 格式
  - 跑项目 setup 脚本
  - DCO / CHANGES / commit format 必查
learned_at: 2026-07-19
---

## ContribAI 实证 close 数据

- pallets/flask: ~5% close 是 missing CHANGES.rst
- HolmesGPT/holmesgpt: ~25% close 是 DCO missing (CNCF 标准)
- 通用: 15-25% close 提到 incomplete setup

## 反模式特征

1. **未读 CONTRIBUTING** — 漏项目特定 setup
2. **缺 CHANGES entry** — 类似 crates.io / flask 要求
3. **缺 DCO sign-off** — CNCF / kernel 标准
4. **commit 格式错** — Conventional Commits / Angular 风格等
5. **CI 失败** — 因为缺 setup

## 自检清单

提 PR 前:
- [ ] 读 README + CONTRIBUTING 完整
- [ ] 看最近 5-10 merged PR 格式
- [ ] CHANGES entry 写了?
- [ ] DCO `git commit -s` 加了?
- [ ] commit 格式符合 CONTRIBUTING 要求?

## 关联

- HolmesGPT: `HolmesGPT-holmesgpt/index.md` (DCO 门票)
- pallets-flask: `pallets-flask/index.md` (CHANGES.rst 门票)
