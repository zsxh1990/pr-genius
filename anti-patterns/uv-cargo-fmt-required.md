---
type: Anti-Pattern
key: uv-cargo-fmt-required
symptom: "CI 报错 Lint check failed / maintainer 评论 cargo fmt / rustfmt"
root_cause: "uv 仓使用 cargo fmt (rustfmt nightly) 作为唯一格式规范，外部工具（dprint、prettier、rustfmt stable）输出与 nightly 不一致"
trigger_keywords:
  - "Please run cargo fmt"
  - "rustfmt"
  - "rustfmt-nightly"
  - "cargo fmt --all"
  - "Lint check failed"
fix_action: "在本地用与 CI 一致的 toolchain 跑 cargo fmt --all，提交 amend"
fix_command: "cargo +nightly fmt --all && git add -u && git commit --amend --no-edit"
source_pr: astral-sh/uv#19685
prevention: "提 PR 前先 cargo +nightly fmt --all；如果本地无 nightly toolchain，先 rustup toolchain install nightly"
learned_at: 2026-07-02
---

# uv-cargo-fmt-required

## 现象

提 PR 到 astral-sh/uv，CI 报 Lint check failed，或 maintainer 评论"Please run cargo fmt before..."。

## 根本原因

uv 仓使用 rustfmt nightly 作为唯一格式规范。rustfmt stable 和 nightly 输出存在差异（主要在 import 排序、链式调用格式化）。本地用 stable rustfmt 跑过不等于 CI 通过。

## 自愈脚本

```bash
# 1. 装 nightly（如果没装）
rustup toolchain install nightly

# 2. 用 nightly 格式化
cargo +nightly fmt --all

# 3. amend 提交（保持 PR 干净）
git add -u
git commit --amend --no-edit
git push --force-with-lease  # 注意：uv 仓允许 amend + force-with-lease
```

## 预防

提 PR 前本地跑：
```bash
cargo +nightly fmt --all -- --check  # 只检查，不改
```

## 教训来源

- [astral-sh/uv#19685 (SARIF audit)](../astral-sh-uv/pr-19685-sarif-audit.md)
- uv 仓 CI: `.github/workflows/ci.yml` lint job 跑 `cargo +nightly fmt --all -- --check`

## 相关反模式

- 无（uv 特定）