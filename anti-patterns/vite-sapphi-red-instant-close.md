---
type: Anti-Pattern
key: vite-sapphi-red-instant-close
symptom: "PR 被 maintainer 在 <2h 内 close + 拒绝语不含具体技术理由"
root_cause: "Vite 仓 sapphi-red（核心 maintainer）主观拒绝通用基础设施类 PR（如 ERROR_HANDLER / 内部重构），无修复路径"
trigger_keywords:
  - "I don't think this is useful"
  - "All information in the new output can easily known without the new output"
  - "new output can easily known"
  - "doesn't fit the direction"
fix_action: "立即停止此方向；本仓永久归档，不再尝试"
fix_command: "gh pr close <PR_NUM> --comment 'Closing per maintainer feedback. Archiving this direction.'"
source_pr: vitejs/vite#22710
prevention: "提 PR 前查 BLACKLIST.md（Vite 已在永久拉黑清单）"
learned_at: 2026-07-02
---

# vite-sapphi-red-instant-close

## 现象

提 PR 到 vitejs/vite，1-2 小时内被 sapphi-red 直接 close + 简短拒绝语。

## 根本原因

Vite 巨型仓 + sapphi-red（核心 maintainer）对**通用基础设施类 PR**（错误处理 / 全局 hooks / 配置抽象）持强烈主观拒绝态度。即使技术正确、CI 通过、维护者也不接受。**没有修复路径**——他不会告诉你怎么改，只会 close。

## 拒绝语样本

> "I don't think this is useful. All information in the new output can easily known without the new output."

**特征**：
- 时长：< 2h（秒拒）
- 措辞：直接否定，无具体技术理由
- 不可挽回

## 自愈脚本

**不要尝试修复**。立即归档此方向：

```bash
# 1. Close PR（保持友好 comment）
gh pr close <PR_NUM> --comment "Closing per maintainer feedback. Archiving this direction — Vite is on the BLACKLIST."

# 2. 把方向记入 MEMORY.md
echo "## $(date +%Y-%m-%d) - vitejs/vite archived" >> MEMORY.md

# 3. 转友好仓（astral-sh/uv / tauri / continue）
```

## 预防

**唯一有效预防 = 根本不投**。

Vite 在 `BLACKLIST.md` 永久拉黑清单中。任何 Agent 在自动扫描时应**先查这张表**。

## 教训来源

- [vitejs/vite#22710 (VITE_ERROR_HANDLER)](https://github.com/vitejs/vite/pull/22710) — sapphi-red 2026-06-18 13:54 close
- 克莱恩 2026-06-18 20:08 GMT+8 拍板：Vite 永久拉黑

## 相关反模式

- [e2b-feature-not-adding-canned-response](./e2b-feature-not-adding-canned-response.md) — 类似拒绝模式但礼貌且可换方向