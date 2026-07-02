---
type: Blacklist Reference
title: 永久拉黑仓排雷指南
description: zsxh1990 永久不再尝试 PR 的仓（节省 token + API 额度）
version: 0.1.0
created: 2026-07-02
---

# 🚫 BLACKLIST — 永久拉黑仓

> **永久拉黑 ≠ 不收录**：
> - **拉黑 = 永久不再尝试 PR**（已 token 验证无解）
> - **不收录 = 还没调研到**（等待期，未来可加）
>
> Agent 在自动扫描/路由时，**先查这张表**，撞上立即跳过。

## 拉黑仓清单

| 仓 | 一句话原因 | 触发场景 |
|---|---|---|
| [vitejs/vite](https://github.com/vitejs/vite) | 巨型仓 + sapphi-red 直接 close 无理由外部 PR | 任何 Vite PR |
| [microG/GmsCore](https://github.com/microg/GmsCore) | 维护者公开反 AI（"this is AI, none of the people who are offering the bounty will pay for vibecoding"） | 任何 microG PR |
| [OpenBSD/src](https://github.com/OpenBSD/src) | 仅邮件列表投递 + 严禁 AI 标签 | 任何 OpenBSD PR |
| [GNOME/*](https://gitlab.gnome.org/) | 维护者公开反 AI + 严要求手工测试 | 任何 GNOME PR |
| [torvalds/linux](https://github.com/torvalds/linux) | 纯邮件列表投递，主流 GitHub Agent 工作流完全无法兼容 | 任何 Linux kernel PR |
| [systemd/systemd](https://github.com/systemd/systemd) | 严格 CI + maintainer 圈外不接受外部 PR | 任何 systemd PR |

## 拉黑历史（含已归档方向）

| 仓 | 方向 | 归档原因 | 状态 |
|---|---|---|---|
| [e2b-dev/E2B](https://github.com/e2b-dev/E2B) | `_ERROR_HANDLER` 类 | mishushakov "we're not adding this feature" | **方向归档，仓仍开放**（详见 e2b-dev-e2b/index.md） |
| vitejs/vite | 任何方向 | sapphi-red "I don't think this is useful" | **整仓拉黑** |

## 拉黑决策规则（Agent 用）

```
if repo in BLACKLIST:
    return "SKIP — 拉黑仓，详见 BLACKLIST.md"

if repo + direction in ARCHIVED_DIRECTIONS:
    return "SKIP — 此方向永久归档，换方向"
```

## 加入新拉黑仓的标准

满足以下**任一**即拉黑：

1. **3 次 PR 全 close-without-merge**（含不同方向）
2. **维护者公开反 AI / 反 AI-agent**（有 issue / PR 评论证据）
3. **工作流完全不兼容 GitHub**（邮件列表投递等）

加入流程：
1. 创建 `blacklist/<org>-<repo>.md`（详细复盘）
2. 更新本文件清单
3. 提交 PR（如果本仓本身在 pr-genius 内）

## 版本

- v0.1.0 (2026-07-02)：初版（6 仓 + 2 归档方向）