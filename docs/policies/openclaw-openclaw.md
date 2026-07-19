---
type: Maintainer Policy
repo: openclaw/openclaw
created: 2026-07-19
updated: 2026-07-19
anchors: [93310, 92872, 96797]
---

# openclaw/openclaw Maintainer Policy

> 基于 3 个真实 PR 拒绝记录提炼 (zsxh1990 #93310 + zhangguiping-xydt #92872 + ductapecode #96797). 三种 close 模式对比: 作者 11d / maintainer 11d / ClawSweeper 1.4h.

## Hard Rejections (直接关闭)

### 1. 不接受 `feat(infra)` 类扩展 OPENCLAW_ERROR_HANDLER 等核心路径

**规则:** PR 不应引入"让 OpenClaw 执行外部命令"的扩展点 (OPENCLAW_ERROR_HANDLER / OPENCLAW_EXEC / 类似), 即使 wrapping 安全 (`shell: false` + argv + opt-in flag) 仍 close.

**锚点:**
- #93310: feat(infra): OPENCLAW_ERROR_HANDLER — "merge-risk: 🚨 security-boundary 永久标签"
- #92872: fix(qqbot): allow scoped sandbox media sends — "merge-risk: 🚨 security-boundary"

**原因:** OpenClaw 把"core 是否执行外部命令"当作**产品决策**, 不接受通过 PR 形式扩展. security-boundary 标签不可 amend 解除.

**正确做法:** 走 plugin/community path (ClawHub) 而不是 core PR.

---

### 2. 不接受 channel-specific 沙箱扩展走 core PR

**规则:** PR 不应在 core 修改 channel-specific 沙箱实现 (qqbot / telegram / discord 等), 即使证明充分也 close.

**锚点:**
- #92872: fix(qqbot): allow scoped sandbox media sends — "Platinum hermit, proof: sufficient, but maintainer policy route to ClawHub"

**原因:** OpenClaw 团队政策: channel-specific 沙箱扩展走 ClawHub/plugin path, 不动 core. 即使 code 正确也撞产品边界.

**正确做法:** 写 plugin / ClawHub extension, 不动 core.

---

### 3. ClawSweeper 主动 close scope 不匹配 (1.4h 典型延迟)

**规则:** PR scope 不匹配已有 Gateway/plugin seams 时, ClawSweeper 主动 close (延迟 ~1.4h, 比 maintainer close 11d 快 200x).

**锚点:**
- #96797: feat(examples): safeTok ↔ OpenClaw DM bridge — "Close as ClawHub/plugin scope. Current OpenClaw already has Gateway and plugin seams."

**原因:** ClawSweeper bot 已被授权做 scope routing 决策. 撞 scope mismatch → 自动 close, 不等 maintainer.

**正确做法:** 提 PR 前查 OpenClaw 已有 Gateway/plugin seams — 有就直接用, 没有才考虑加 core.

---

## Soft Warnings (review 时关注)

### 1. `feat` prefix 比 `fix` prefix close 率高

**警告:** `feat` prefix 在 OpenClaw 偏好 `fix` prefix (merged 79% 用 `fix`).

**触发:** title 以 `feat(` 开头但用 `fix(` 更准确表达 bug 修复.

---

### 2. Amend > 3 次评分降级

**警告:** 反复 amend 让 ClawSweeper 把评分从初始评级往下降 (信号 = "作者没想清楚").

**触发:** commits > 3 + 评分降级 (gold shrimp → unranked krab).

---

### 3. `merge-risk: 🚨 security-boundary` 不可 amend

**警告:** 该标签是产品决策, 改代码也不能解除. 提 PR 前先确认改动不在此标签内.

---

## Notes

- ClawSweeper bot 是 OpenClaw 维护者优先级 (评分 + 部分 close 决策).
- OpenClaw 几乎日更 release (6/3-6/24 共 20 release, 间隔 1-3 天), 每个 release 是评审窗口.
- `fix` 占 merged 79% (107/136), 但 `fix` 不是门票 (54 个失败 PR 也用 `fix`).
