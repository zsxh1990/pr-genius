---
type: Anti-Pattern
key: trusted-publisher-oidc-insufficient
symptom: "Trusted publishing exchange failure: OpenID Connect token retrieval failed: GitHub: missing or insufficient OIDC token permissions, the ACTIONS_ID_TOKEN_REQUEST_TOKEN environment variable was unset"
root_cause: "publish-pypi.yml workflow 缺 `permissions: id-token: write`，GH 默认不发 OIDC token 给 workflow。PyPI Trusted Publisher 走 OIDC，token 拿不到 = publish 步骤立即 exit"
trigger_keywords:
  - "Trusted publishing exchange failure"
  - "OpenID Connect token retrieval failed"
  - "ACTIONS_ID_TOKEN_REQUEST_TOKEN"
  - "missing or insufficient OIDC token permissions"
  - "id-token: write"
fix_action: "在 publish-pypi.yml 的 jobs 级别加 `permissions: id-token: write`（与 runs-on 同级），然后 git push + dispatch"
fix_command: "git apply <<'PATCH'\n--- a/.github/workflows/publish-pypi.yml\n+++ b/.github/workflows/publish-pypi.yml\n@@ -9,6 +9,8 @@ jobs:\n     runs-on: ubuntu-latest\n     environment: pypi\n+    permissions:\n+      id-token: write\n \n     steps:\nPATCH\ngit add .github/workflows/publish-pypi.yml\ngit commit -m \"fix(workflow): add OIDC write permission for PyPI Trusted Publisher\"\ngit push origin main\n# POST /actions/workflows/<wf_id>/dispatches then poll"
source_pr: zsxh1990/pr-genius#commit a0c33f9
prevention: "写任何用 Trusted Publisher 的 workflow（PyPI / npm provenance / GH Pages OIDC 等）前，permissions 块必须先写。GitHub UI 在 'Add workflow' 模板里默认不带，需要手动加"
learned_at: 2026-07-09
---

# trusted-publisher-oidc-insufficient

## 现象

首次跑 `pypa/gh-action-pypi-publish@release/v1` 时，step 7（Publish）失败：

```
##[error]Trusted publishing exchange failure: 
OpenID Connect token retrieval failed: GitHub: missing or insufficient 
OIDC token permissions, the ACTIONS_ID_TOKEN_REQUEST_TOKEN environment 
variable was unset

This generally indicates a workflow configuration error, such as insufficient
permissions. Make sure that your workflow has `id-token: write` configured
at the job level, e.g.:

```yaml
permissions:
  id-token: write
```
```

- build / smoke-test 步骤全成功（wheel 干净，metadata 对齐）
- 只有最后 publish 步骤红
- PyPI 端 Trusted Publisher 配置**没问题**
- GH workflow 端**缺 OIDC 权限**——这是 GH Actions 默认行为，权限最小化

## 根本原因

GitHub Actions 默认不给 workflow 发 OIDC token。Trusted Publisher 走 OIDC 拿 PyPI 临时 token，必须显式 `permissions: id-token: write`。两个独立配置：

1. **PyPI 端**（克莱恩手工配）：owner/repo/workflow/env 声明
2. **GH workflow 端**（YAML 文件）：job 级别 id-token: write

**两个都缺一不可**。

## 自愈脚本

### 修复 workflow（1 个 block 加 2 行）

在 `.github/workflows/publish-pypi.yml` 的 `jobs.publish` 块加：

```yaml
jobs:
  publish:
    name: Build & publish prgenius-core to PyPI
    runs-on: ubuntu-latest
    environment: pypi
    permissions:
      id-token: write   # required for PyPI Trusted Publisher OIDC token

    steps:
      ...
```

### 验证

1. commit + push（FF）
2. POST `/repos/<owner>/<repo>/actions/workflows/<wf_id>/dispatches`（HTTP 204）
3. Poll `/actions/runs/<run_id>` 等 `status=completed / conclusion=success`
4. PyPI API: `curl https://pypi.org/pypi/<project>/json` 期待 HTTP 200 + `info.version` 对齐

## 与其他 OIDC 类动作的关联

| 平台 | 必填权限 |
|---|---|
| PyPI Trusted Publisher | `id-token: write` |
| npm provenance (npm publish) | `id-token: write` |
| GitHub Pages OIDC | `id-token: write` |
| AWS / GCP / Azure OIDC federate | `id-token: write` |

**任何用 OIDC 拿外部 token 的 workflow** 都缺这权限——这是 GH 安全模型的统一行为，不是 PyPI 特例。

## 预防

写 workflow YAML 的**第一个 review 项**（**写之前**不是写之后）：

1. 是否用 OIDC？→ 是 → `permissions: id-token: write` 必须先写
2. 是否写 release？→ 是 → `permissions: contents: write`（默认是 read）
3. 是否调 GH API？→ 检查对应 scope

## 教训来源

- zsxh1990/pr-genius workflow 修复 commit `a0c33f9 fix(workflow): add OIDC write permission for PyPI Trusted Publisher`
- 跑过 2 次 failed run 后定位到根因：run 28958085911（push-triggered）+ run 28958395001（workflow_dispatch）
- 修复后 run 28958939714 31 秒内 success → prgenius-core 0.7.8 live on PyPI
- 克莱恩 2026-07-09 00:30 GMT+8 拍板：写 anti-pattern + 写 MEMORY

## 相关反模式

- 无（OIDC 是 workflow YAML 独立 concern，跟 PR review 反模式正交）
- 但跟 "提 PR 前必读 issue" 类反模式**同精神**：写之前先查 Trusted Publisher 文档，不是写完再调试