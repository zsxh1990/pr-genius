---
type: Anti-Pattern
key: cosmetic-no-user-pain
symptom: "we're not seeing any major user pain this PR would solve" / "I don't think this is useful"
root_cause: 提交了美化/格式化/输出改进，但没有解决真实用户痛点。维护者认为这些改动是 cosmetic（表面修饰），不值得 review 和维护成本。
trigger_keywords:
  - "not useful"
  - "cosmetic"
  - "not seeing any major user pain"
  - "easily known without"
  - "unnecessary at the moment"
fix_action: 在提 PR 前，先在 Issue 或 Discussion 中确认维护者认为这是一个需要解决的问题。不要自己假设"这个改进有价值"。
source_pr: vitejs/vite#22701
prevention: "提 PR 前问自己：(1) 有没有用户报过这个痛点？(2) 维护者是否认可这是个问题？(3) 改动是否只影响输出格式而非功能？"
learned_at: 2026-07-08
---

## 案例

### vitejs/vite #22701 — VITE_ERROR_HANDLER
- **提交内容**: 为 Vite 添加更详细的错误输出格式
- **拒绝原因**: sapphi-red: "I don't think this is useful. All information in the new output can easily known without the new output."
- **教训**: 输出格式改进如果没有用户反馈支持，会被认为是 cosmetic

### e2b-dev/E2B #1413 — replace rich with stdlib
- **提交内容**: 用标准库替换 rich 依赖
- **拒绝原因**: mishushakov: "Thanks for opening the PR, but we're not seeing any major user pain this PR would solve, since is mostly cosmetic."
- **教训**: 依赖替换如果没有性能/安全/维护性问题，也会被认为是 cosmetic

## 反模式特征

1. **没有 Issue 背景**: PR 是"我觉得这样更好"，而不是"用户报了这个问题"
2. **只改输出格式**: 不影响功能，只影响显示
3. **依赖替换**: 用"更标准"的库替换现有依赖，但没有性能/安全问题
4. **错误信息美化**: 让错误信息"更好看"，但没有增加有用信息

## 自检清单

提 PR 前检查：
- [ ] 有没有对应的 Issue 或 Discussion？
- [ ] 维护者是否认可这是个问题？
- [ ] 改动是否只影响输出格式？
- [ ] 如果去掉这个改动，用户会受影响吗？
