---
type: Anti-Pattern
key: e2b-feature-not-adding-canned-response
symptom: "PR 被 mishushakov 礼貌 close + 评论含 'we're not adding' / 'not seeing major user pain' / 'appreciate the initiative'"
root_cause: "E2B 仓对'通用基础设施'类 feature PR（无用户痛点驱动）持坚定拒绝态度。措辞礼貌 = 留合作空间，但本方向永久归档"
trigger_keywords:
  - "we're not adding this feature"
  - "not seeing major user pain"
  - "appreciate the initiative"
  - "we don't want to add"
  - "out of scope for the CLI"
fix_action: "礼貌 close + 留下 friendly comment；本方向归档，换 bug fix / doc 改进 / 别的 feature 方向"
fix_command: "gh pr close <PR_NUM> --comment 'Thanks @mishushakov — appreciate the thoughtful review. Closing per maintainer decision. Will explore bug fix / doc improvement directions instead.'"
source_pr: e2b-dev/E2B#1458
prevention: "提 PR 前必读 e2b-dev-e2b/index.md §3 '_ERROR_HANDLER 方向永久归档'；新方向前先在 issue 区观察 maintainer 关注点"
learned_at: 2026-07-02
---

# e2b-feature-not-adding-canned-response

## 现象

提 PR 到 e2b-dev/E2B（CLI 类 feature），约 9h 后被 mishushakov（核心 maintainer）礼貌关闭：

> "Hi, appreciate the initiative — but we're not adding this feature to our CLI. We don't see major user pain that would justify the additional code path."

## 根本原因

E2B 仓对**通用基础设施类 feature PR**（无明确用户痛点驱动）持坚定拒绝态度：

- 拒绝时长：~9h（不是秒拒，但也不留余地）
- 措辞：礼貌 + 不给具体技术理由 = **产品决策**而非技术问题
- 不可挽回：但**留合作空间**

## 拒绝语样本（mishushakov 风格）

| 拒绝语 | 含义 |
|---|---|
| "we're not adding this feature to our CLI" | 仓不想要这个方向 |
| "not seeing major user pain" | 缺用户痛点驱动 |
| "appreciate the initiative" | 礼貌起点 |
| "out of scope" | 范围外 |

## 与 vite-sapphi-red 的关键区别

| 维度 | Vite (sapphi-red) | E2B (mishushakov) |
|---|---|---|
| 拒绝时长 | < 2h（秒拒） | ~9h（考虑后拒） |
| 措辞 | 直接否定 | 礼貌 + 留余地 |
| 原因 | 主观 | 产品决策 |
| 可挽回 | ❌ 永远 close | ✅ 可换方向 |
| **仓是否拉黑** | ✅ **整仓拉黑** | ⚠️ **方向归档，仓仍开放** |

## 自愈脚本

```bash
# 1. 礼貌 close（不是 abandon，留 comment）
gh pr close <PR_NUM> --comment "Thanks @mishushakov — appreciate the thoughtful review. Closing per maintainer decision. Will explore bug fix / doc improvement directions instead."

# 2. 把方向记入 anti-patterns 索引（方向归档）
echo "$(date +%Y-%m-%d) - e2b-dev/E2B _ERROR_HANDLER 方向归档" >> archive.md

# 3. 转 E2B 其他方向（bug fix / doc / 别的 feature）
```

## 预防

**提 PR 前必做**：
1. 读 `e2b-dev-e2b/index.md` §3（已归档方向）
2. 观察 issue 区看 maintainer 在关注什么
3. **避开通用基础设施**（_ERROR_HANDLER / _GLOBAL_CONFIG / _METRICS 类）
4. **优先 bug fix / doc 改进**（CLA + changeset 流程虽重，但方向对就过）

## 教训来源

- [e2b-dev/E2B#1458 (E2B_ERROR_HANDLER)](../e2b-dev-e2b/pr-1413-rich-to-ansi.md)
- mishushakov 2026-06-18 12:37 close
- 克莱恩 2026-06-18 22:11 GMT+8 拍板 C：不拉黑 E2B，本 feature 关闭

## 相关反模式

- [vite-sapphi-red-instant-close](./vite-sapphi-red-instant-close.md) — 类似但秒拒 + 不可挽回