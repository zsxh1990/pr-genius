---
type: Anti-Pattern
key: generic-no-debug-logging
description: "MCP/API servers without debug logging make auth failures opaque"
tags: [debug, logging, mcp, auth, troubleshooting]
created: 2026-08-23
source_url: https://github.com/Ikalus1988/MisakaNet/pull/1230
updated: 2026-08-23
confidence: high
trigger_keywords:
  - "auth failure"
  - "unauthorized"
  - "debug"
  - "opaque error"
severity: medium
---

# No Debug Logging for Auth Failures

## Pattern

API/MCP servers that return generic "Unauthorized" errors without debug context make troubleshooting impossible.

## Symptom

Users report "Unauthorized" but cannot diagnose:
- Is the token valid?
- Is the token format correct?
- Which auth step failed?
- What was the expected vs provided value?

## Solution

Add `MISAKA_DEBUG` env var with levels:
- Level 0: No debug (default, production)
- Level 1: Auth failures with context (step, reason, token prefix)
- Level 2: Full request/response logging

## Evidence

- MisakaNet#1230: Added debug logging for Remote MCP endpoint
- Level 1 logs: step, reason, masked token prefix
- Level 2 logs: full request/response

## How to Avoid

1. Always include debug mode for auth systems
2. Log auth failure context (step, reason)
3. Mask sensitive data (token prefix only)
4. Use env var to control verbosity

## Applicability

Any API/MCP server with authentication.
