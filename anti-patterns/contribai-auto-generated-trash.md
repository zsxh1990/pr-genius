---
type: Anti-Pattern
key: contribai-auto-generated-trash
symptom: |
  PR 含 AI agent 自动生成残留文件 (README.md --- / search_knowledge.py --- 这类奇怪文件名), 或 markdown patch 粘进源码。Close 关键词: "contains generated files", "diff artifacts", "please remove generated files"
root_cause: AI agent 生成 diff 时没清理, 把工具产物当成源码提交。
trigger_keywords:
  - "contains generated files"
  - "diff artifacts"
  - "please remove generated files"
  - "what is README.md ---?"
  - "this is a patch file"
fix_action: |
  1) 提 PR 前必跑 git diff --stat 确认没奇怪文件
  2) 检查 filenames 含 --- / patch / diff 的
  3) 提 PR 前清理 .gitignore 应该忽略的临时文件
source_pr: "MisakaNet 自身教训 (fix #429 patch 粘进源码)"
prevention: |
  提 PR 前:
  - git diff --stat 看新增文件
  - 检查文件名是否正常 (.py / .md / .ts 等)
  - 清理临时文件 (output.txt / patch.diff 等)
  - 不用 Write 工具覆盖整个 README (用 Edit 增量)
learned_at: 2026-07-19
---

## ContribAI 实证 close 数据

- MisakaNet 自身 fix #429: patch 粘进源码
- AI agent PRs: ~5-10% 有类似残留
- Claude Code / Codex agent: 默认会清, 但 prompt 不到位会留

## 反模式特征

1. **README.md --- 文件** — 工具把 diff 输出当文件名
2. **search_knowledge.py --- 同样问题
3. **patch 内容粘进源码** — 把 markdown diff 当 python
4. **Write 工具覆盖文件** — 全文替换丢失结构
5. **未清理临时文件** — .bak / .tmp / .patch 提交

## 自检清单

提 PR 前:
- [ ] git diff --stat 看新增文件
- [ ] 文件名正常 (.py / .md / .ts)
- [ ] 清理临时文件 (.bak / .tmp / .patch)
- [ ] 不用 Write 覆盖, 用 Edit 增量
- [ ] diff 不含 patch 内容粘进源码

## 关联

- MisakaNet maintainer policy: `docs/policies/Ikalus1988-MisakaNet.md` (rule 2: 不接受生成器残留文件)
