---
type: PR Case Study
title: "jupyter-mcp-server #266 — configurable execution timeout"
pr_number: 266
pr_url: https://github.com/datalayer/jupyter-mcp-server/pull/266
repo: datalayer/jupyter-mcp-server
author: zsxh1990
status: closed-merged
opened_at: "2026-07-12"
merged_at: "2026-07-13"
schema_version: rounds v0.5.0
confidence: high
rounds:
  - round: 1
    action: open
    delta:
      kind: code_change
      value: "+15 / -4 (2 files: config.py, server.py)"
    resolution: merged
    timestamp: "2026-07-12"
  - round: 2
    action: amend
    delta:
      kind: code_change
      value: "Update docs: README + reference/tools/index.mdx"
    resolution: merged
    timestamp: "2026-07-13"
---

## PR #266: configurable execution timeout

**Issue**: #249 — execute_code timeout 120s max is unusable

**Approach**: Add `execution_timeout` and `max_execution_timeout` to JupyterMCPConfig. Default 120s, max 3600s. Support env var `JUPYTER_MCP_EXECUTION_TIMEOUT`.

**Outcome**: Merged after maintainer asked for docs update.

**Key Learning**: 
1. Always update docs when adding config options
2. Maintainer may ask for clarification — respond quickly
3. Similar PR already existed (#257) — explain the difference

**Anti-pattern**: Initially no docs update → maintainer request.

**Success Factor**: Config-based approach (more flexible than hardcoded), env var support, clear docs.
