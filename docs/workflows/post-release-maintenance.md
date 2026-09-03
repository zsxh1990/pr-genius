# Post-Release Maintenance Workflow

每次发版后执行的标准化维护流程。

## Trigger

- 新 tag 推送（如 `v1.8.0`）
- 或手动触发

## Phase 1: 发版验证 (5 min)

```bash
# 1. 确认 PyPI 发布
pip3 index versions prgenius-core | head -1

# 2. 确认 Docker image
gh run list --limit 3 --json name,conclusion

# 3. 确认 v1 tag 更新
gh api repos/zsxh1990/pr-genius/git/ref/tags/v1 --jq '.object.sha'
git rev-parse v1.8.0  # 应该一致

# 4. 本地版本验证
python3 -m prgenius --version
```

**如果 v1 tag 失败**：检查 workflow `permissions: contents: write` 是否配置。

## Phase 2: Smoke Test (10 min)

```bash
# 1. 20 样本渲染测试
python3 - << 'PYEOF'
import subprocess, json, importlib.util
spec = importlib.util.spec_from_file_location('pc', '.github/actions/pr-genius-check/post_comment.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
# ... run 20 samples through coach + render_comment
PYEOF

# 2. Post_comment marker 去重测试
# 推送两次到同一 PR，确认 comment 更新而非新建

# 3. 验证 validator
python3 validate.py 2>&1 | tail -5
```

**关键检查**：
- render_comment 无 AttributeError
- marker comment `updated_at` > `created_at`
- 无新增 validator error

## Phase 3: PR 清理 (5 min)

```bash
# 1. 关闭测试 PR
gh pr close <test-pr> --comment "Smoke test — closing."

# 2. 删除测试分支
git push origin --delete test/<branch>

# 3. 合并 Dependabot PR
gh pr list --search "author:app/dependabot" --state open
gh pr merge <pr> --squash --auto

# 4. Rebase 落后的 PR
gh pr list --state open --json number,title,headRefName
git fetch origin
# 检查每个 PR 是否 behind main
```

## Phase 4: 内容审计 (10 min)

```bash
# 1. 孤立 anti-pattern 统计
python3 validate.py 2>&1 | grep -c 'orphan anti-pattern'

# 2. Profile 缺失字段
python3 validate.py 2>&1 | grep '缺 evidence_url'

# 3. harvest.py TODO 检查
grep -n 'TODO' scripts/harvest.py

# 4. Case study 覆盖率
echo "anti-patterns: $(ls anti-patterns/*.md 2>/dev/null | wc -l)"
echo "referenced: $(python3 validate.py 2>&1 | grep 'referenced:' | grep -oP '\d+(?=,)')
echo "case studies: $(ls review-cases/*.json 2>/dev/null | wc -l)"
```

**决策点**：
- 孤立 anti-pattern > 500 → 批量归档到 `archive/anti-patterns/`
- Profile 缺 evidence → 提 Issue 跟踪
- harvest.py TODO → 下次 harvest 时补全

## Phase 5: 依赖更新 (5 min)

```bash
# 1. 检查 Dependabot PR
gh pr list --search "author:app/dependabot" --state open

# 2. 用户侧更新提醒
# 如果有使用 pr-genius action 的仓库，确认 Dependabot 已配置
# 示例：MisakaNet .github/dependabot.yml
```

## Checklist Template

```markdown
## Post-Release v1.X.0

### Phase 1: 发版验证
- [ ] PyPI prgenius-core X.Y.Z 可用
- [ ] Docker image ghcr.io 构建成功
- [ ] v1 tag 指向正确 commit
- [ ] 本地 `prgenius --version` 正确

### Phase 2: Smoke Test
- [ ] 20 样本 render_comment 通过
- [ ] marker 去重生效
- [ ] validator 无新增 error

### Phase 3: PR 清理
- [ ] 测试 PR 已关闭
- [ ] 测试分支已删除
- [ ] Dependabot PR 已合并
- [ ] 落后 PR 已 rebase

### Phase 4: 内容审计
- [ ] 孤立 anti-pattern 统计
- [ ] Profile 缺失字段记录
- [ ] harvest.py TODO 状态

### Phase 5: 依赖更新
- [ ] Dependabot PR 处理
- [ ] 用户侧更新确认
```

## Automation Opportunities

| 步骤 | 当前方式 | 可自动化 |
|------|----------|----------|
| PyPI 版本检查 | 手动 `pip index` | ✅ CI step |
| Smoke test | 手动跑脚本 | ✅ GitHub Action |
| PR 清理 | 手动 gh 命令 | ⚠️ 半自动（需确认） |
| 内容审计 | 手动 grep | ✅ CI step |
| v1 tag 更新 | 手动或 workflow | ✅ 已有 workflow |
