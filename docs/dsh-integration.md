# DSH Integration Guide

[![DSH Plugin](https://img.shields.io/badge/DSH-Plugin-blue?style=flat-square&logo=deepseek)](https://github.com/topics/dsh-plugin)
[![MCP](https://img.shields.io/badge/MCP-Server-green?style=flat-square)](https://github.com/modelcontextprotocol)

> Use [pr-genius](https://github.com/zsxh1990/pr-genius) as an MCP skill inside [DeepSeek Harness (DSH)](https://github.com/deepseek-ai/dsh) for AI-powered PR submission review, coach guidance, and anti-pattern detection.

## What is DSH?

DeepSeek Harness (DSH, ⭐108k+) is an open-source AI coding agent built on the Cordis framework. It supports plugins, MCP servers, and web UI extensions.

## Why pr-genius + DSH?

| DSH Native | pr-genius adds |
|-----------|----------------|
| Code generation, refactoring | Pre-submit PR review & anti-pattern detection |
| Task planning, testing | Coach mode for iterative PR improvement |
| File search, linting | Harvest mode to extract reusable lessons |
| — | Profile-driven context (project-specific rules) |
| — | 346+ anti-pattern rules, 62+ lessons |

## Setup

### Method 1: MCP Skill Mode (Recommended)

In DSH settings or `~/.dsh/settings.json`, add:

```json
{
  "mcpServers": {
    "pr-genius": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/zsxh1990/pr-genius@main", "pr-genius", "--stdio"],
      "env": {
        "GITHUB_TOKEN": "<your-token>"
      }
    }
  }
}
```

### Method 2: Local Development

```bash
git clone https://github.com/zsxh1990/pr-genius.git
cd pr-genius
pip install -e .
```

Then configure DSH to use the local install:

```json
{
  "mcpServers": {
    "pr-genius": {
      "command": "pr-genius",
      "args": ["--stdio"],
      "env": {
        "GITHUB_TOKEN": "<your-token>"
      }
    }
  }
}
```

### Method 3: Docker (Standalone)

```bash
docker pull ghcr.io/zsxh1990/pr-genius:latest
docker run -d --name pr-genius -p 8000:8000 ghcr.io/zsxh1990/pr-genius:latest
```

## Usage Scenarios in DSH

### 1. Pre-submit Review (in DSH conversation)

> "Review my staged changes before I push"

pr-genius will scan your diff, flag anti-patterns, suggest improvements, and rate PR readiness.

### 2. Coach Mode

> "Coach me on improving this PR"

Iterative guidance: fix issues → re-review → learn patterns specific to your project.

### 3. Harvest Mode

> "Extract lessons from this codebase"

Analyze git history to generate reusable lessons for future PRs in this project.

### 4. Standalone CLI

```bash
# Review a PR diff
pr-genius review --diff-file changes.diff

# Coach mode
pr-genius coach --repo owner/repo --number 123

# Harvest lessons
pr-genius harvest --repo owner/repo

# Check anti-patterns
pr-genius check --diff-file changes.diff
```

## Example Workflow in DSH

```
You: "I've been working on adding OAuth support to the auth module.
      Help me review and polish the PR before submission."

DSH + pr-genius:
1. pr-genius reviews your diff → flags 3 anti-patterns
2. You fix them with DSH's code editing
3. pr-genius coach mode → confirms fixes + 2 more suggestions
4. Final check passes → ready to submit
```

## Architecture

```
┌─────────────┐     MCP stdio      ┌─────────────┐
│     DSH     │ ◄──────────────────►│  pr-genius   │
│  (DeepSeek) │                     │  (Python)    │
└─────────────┘                     └──────┬──────┘
                                           │
                              ┌────────────┼────────────┐
                              │            │            │
                         ┌────▼───┐  ┌─────▼────┐  ┌───▼────┐
                         │ Review │  │  Coach   │  │Harvest │
                         └────────┘  └──────────┘  └────────┘
```

## Links

- [pr-genius GitHub](https://github.com/zsxh1990/pr-genius)
- [DSH GitHub](https://github.com/deepseek-ai/dsh)
- [DSH Plugins Topic](https://github.com/topics/dsh-plugin)
- [awesome-dsh-plugin](https://github.com/awesome-dsh-plugin/awesome-dsh-plugin)
