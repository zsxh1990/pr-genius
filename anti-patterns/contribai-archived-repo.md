---
type: Anti-Pattern
key: contribai-archived-repo
symptom: |
  PR 提到 archived repo (维护者标记 archived = 不再维护). Close 关键词: "repo archived", "no longer maintained", "use <new> instead"
root_cause: 提 PR 前没查 repo 状态 (gh repo view --json isArchived), 不知道 archived 仓不接受 PR。
trigger_keywords:
  - "repo archived"
  - "no longer maintained"
  - "use <new> instead"
  - "this repo is read-only"
  - "consider <successor> project"
fix_action: |
  1) gh repo view org/repo --json isArchived,isDisabled
  2) 如果 archived, 转去 successor project
  3) 或 fork 出来自己维护 (但失去 upstream sync)
source_pr: "ContribAI 14 closed PR 中 ~10% 是 archived repo"
prevention: |
  提 PR 前必查:
  - gh repo view org/repo --json isArchived,isDisabled
  - 看 README 顶部是否有 "This project is no longer maintained" 横幅
learned_at: 2026-07-19
---

## ContribAI 实证 close 数据

- 通用比例: ~10% close 提到 archived
- 常见 successor: moment/moment → date-fns, request/request → axios/ky, node-inspect/node-inspect → 内置 util.inspect
- 大仓 archived 通常有 README 顶部横幅明确说明

## 反模式特征

1. **未查 repo 状态** — 直接提 PR, 不知道 archived
2. **fork 出来还 @upstream** — archived 仓不接受
3. **不看 README 横幅** — 顶部就有 "no longer maintained"
4. **AI 不查 archived** — LLM 默认 repo 可贡献

## 自检清单

提 PR 前:
- [ ] gh repo view org/repo --json isArchived,isDisabled
- [ ] 读 README 顶部找 archived 横幅
- [ ] 找 successor project
- [ ] fork 出来自己维护 (明确说 fork-only)

## 关联

- needs_preflight check: docs/policies/ 模板可加 "check archived status"
