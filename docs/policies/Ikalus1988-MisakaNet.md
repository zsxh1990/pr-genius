---
type: Maintainer Policy
repo: Ikalus1988/MisakaNet
created: 2026-07-18
updated: 2026-07-18
anchors: [491, 492, 493, 494, 495, 496, 497]
---

# Ikalus1988/MisakaNet Maintainer Policy

> 基于真实 PR 拒绝记录提炼的维护者政策。
> 每条规则附带锚点 PR，可追溯验证。

## Hard Rejections（直接关闭）

### 1. 不接受破坏性 README 重写

**规则：** PR 不应整体替换 README.md。增量修改可以，全文替换不行。

**锚点：**
- #491: Fix #285 — 替换大量 README 内容
- #496: Fix #300 — 同上

**原因：** 外部贡献者不了解 README 的完整上下文，全文替换会丢失维护者精心组织的结构。

**正确做法：** 用 `Edit` 做增量修改，不要用 `Write` 覆盖整个文件。

---

### 2. 不接受生成器残留文件

**规则：** PR 不应创建 `README.md ---`、`search_knowledge.py ---` 这类文件名。

**锚点：**
- #492: Fix #290 — 创建了 `README.md ---`
- #494: Fix #285 — 同上
- #495: Fix #285 — 同上

**原因：** 这是工具生成 diff 时的产物，不是真正的源码文件。

**正确做法：** 检查 `git diff --stat` 确认没有异常文件名。

---

### 3. 不接受粘贴 patch 到源码

**规则：** PR 不应把 markdown diff 或 patch 内容直接粘贴到 Python 源码文件中。

**锚点：**
- #493: Fix #429 — 把 patch 粘进了 `search_knowledge.py`

**原因：** 这会导致语法错误，CI 无法通过。

**正确做法：** 用 `Edit` 做精确字符串替换，不要粘贴整个 diff。

---

### 4. 不接受核心文件大删

**规则：** PR 不应大幅删除 `search_knowledge.py`、`misakanet/` 等核心文件的内容。

**锚点：**
- #497: Fix #429 — 破坏性重写 search_knowledge.py

**原因：** 核心文件承载了大量测试通过的行为，大删会破坏功能。

**正确做法：** 增量修改，每次改一个函数或一个逻辑块。

---

## Soft Warnings（review 时关注）

### 5. docs-only PR 不应改代码

**规则：** 标题含 "docs" 的 PR 不应该修改 `.py` 文件。

**原因：** 文档和代码修改混在一起增加 review 难度。

---

### 6. Worker/API PR 需要设计审查

**规则：** 修改 `workers/` 或 API 端点的 PR 需要先在 Issue 中讨论设计方案。

**原因：** 这些模块涉及安全和部署，不能随意改动。

---

### 7. 不用 star/fork/clone 证明价值

**规则：** PR 描述中不应使用 "X stars"、"Y forks" 作为 lesson 有用性的证明。

**原因：** Star 数不等于内容质量，维护者关注的是技术准确性。

---

### 8. helpful=0 时不能宣称 adoption

**规则：** 如果 lesson 的 helpful button 点击数为 0，不应在 PR 中宣称 "已被社区采用"。

**原因：** 没有实际使用证据的宣称会降低可信度。

---

### 9. bounty contributor ≠ 真实用户

**规则：** 参与 bounty 任务的贡献者不应被当作真实用户来引用。

**原因：** bounty 是激励驱动，不代表自然采用。

---

## Triage 指南

收到外部 PR 时，按以下顺序检查：

1. **文件名检查** — 有没有 `---` 后缀的异常文件？
2. **diff 大小** — README/search_knowledge.py 的修改是否超过 50%？
3. **代码 vs 文档** — docs-only PR 是否改了 .py 文件？
4. **核心文件** — 是否大幅删除了 misakanet/ 下的文件？
5. **生成器残留** — 是否有 markdown 语法混入 Python 源码？

命中任何一条 → 直接关闭，引用本政策对应条目。
