---
type: Documentation
title: PR Genius Setup Guide
description: 5-minute guide to add PR Genius to your repository
---

# PR Genius Setup Guide

Add AI-powered PR analysis to your repository in 5 minutes.

## Quick Start

### 1. Copy the workflow file

```bash
# Create the workflow directory
mkdir -p .github/workflows

# Download the workflow
curl -o .github/workflows/pr-genius-check.yml \
  https://raw.githubusercontent.com/zsxh1990/pr-genius/main/.github/workflows/pr-genius-check.yml
```

### 2. Commit and push

```bash
git add .github/workflows/pr-genius-check.yml
git commit -m "ci: add PR Genius auto-check"
git push
```

### 3. Done!

PR Genius will now automatically comment on every new PR with:
- Risk level (🟢 low / 🟡 medium / 🔴 high)
- Blocking signals
- Actionable suggestions

## Configuration

### Repository Variables (optional)

Set these in **Settings > Secrets and variables > Actions > Variables**:

| Variable | Default | Description |
|----------|---------|-------------|
| `PR_GENIUS_URL` | `https://github.com/zsxh1990/pr-genius` | URL shown in bot comments |
| `PR_GENIUS_VERSION` | `prgenius-core` | PyPI package name (for forks) |

### Repository Profile (optional)

Create `.pr-genius/profile.yml` in your repo to customize behavior:

```yaml
repo: org/repo
star: 1000
language: Python
agent_guidelines:
  ai_policy: welcoming
  require_signed_off: true
  require_issue_first: false
  maintainer_vibe: responsive
  external_merge_rate_30: 0.30
```

### Policy File (optional)

Create `.pr-genius/policy.yml` to define hard/soft rules:

```yaml
rules:
  - name: "No direct pushes to main"
    severity: hard
    pattern: "target_branch == 'main'"

  - name: "Require tests for new features"
    severity: soft
    pattern: "title starts with 'feat:' and not body contains 'test'"
```

## What PR Genius Checks

### For Contributors
- **Risk level**: Is this PR safe to submit?
- **Blocking signals**: What needs to be fixed?
- **Suggestions**: How to improve the PR

### For Maintainers
- **Action**: What to do with this PR?
- **Impact**: Files changed, breaking changes, security-sensitive
- **Review complexity**: How long to review?
- **Author info**: First-time contributor?

## Examples

### Low-risk PR
```
## 🟢 PR Genius

🟢 No issues found — 2 positive signal(s), 0 concern(s)

- ✅ Issue linked
- ✅ Returning contributor
```

### High-risk PR
```
## 🔴 PR Genius

🔴 3 blocking issue(s) — fix before submitting

- ❌ Breaking change without migration path
- ❌ Security-sensitive changes
- ❌ No tests added
```

## Troubleshooting

### Bot doesn't comment on PRs
1. Check that the workflow file is in `.github/workflows/`
2. Check that the workflow is enabled in **Actions** tab
3. Check that the repo has **Read and write** permissions for Actions

### Wrong risk level
1. Create a repo profile (see above)
2. Add anti-patterns specific to your repo
3. Open an issue on [pr-genius](https://github.com/zsxh1990/pr-genius/issues)

### Want to customize the bot comment
Edit `.github/workflows/pr-genius-check.yml` and modify the JavaScript in the "Comment on PR" step.

## Advanced Usage

### CLI

```bash
# Install
pip install prgenius-core

# Analyze a PR
python3 -m prgenius coach "feat: new feature" --repo org/repo --body "Description"

# Check PR status
python3 -m prgenius status --author username

# Get maintainer view
python3 -m prgenius maintainer-review "fix: bug" --repo org/repo
```

### MCP Server

Add to your Claude Code settings:

```json
{
  "mcpServers": {
    "pr-genius": {
      "command": "python3",
      "args": ["-m", "prgenius", "mcp", "serve"]
    }
  }
}
```

## Support

- **Issues**: [github.com/zsxh1990/pr-genius/issues](https://github.com/zsxh1990/pr-genius/issues)
- **Discussions**: [github.com/zsxh1990/pr-genius/discussions](https://github.com/zsxh1990/pr-genius/discussions)
