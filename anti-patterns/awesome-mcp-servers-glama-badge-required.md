---
type: Anti-Pattern
repo: punkpeye/awesome-mcp-servers
created: 2026-07-18
anchors: [10044]
tags: [glama-badge, mcp-server, listing-requirement, bot-gate]
---

# awesome-mcp-servers: Glama Badge Required

## Pattern

All entries in awesome-mcp-servers require a Glama score badge. PRs without the badge get auto-flagged by `github-actions` bot and cannot merge until the badge is added.

## Evidence

**PR #10044** — Added MisakaNet to Knowledge & Memory section without Glama badge. Bot immediately commented:

> Please complete the following steps:
> 1. Ensure your server is listed on Glama.
> 2. Update your PR by adding a Glama score badge.

All 7 recently merged PRs have the badge inline:
```
- [owner/repo](url) [![name MCP server](https://glama.ai/mcp/servers/owner/repo/badges/score.svg)](https://glama.ai/mcp/servers/owner/repo) emoji - description
```

## Root Cause

Glama is the MCP ecosystem's quality gate (56k+ servers). The badge proves the server can start and respond to introspection. Without it, there's no proof the server works.

## Fix Action

1. **Add Dockerfile to your repo** — Glama needs to build and run the server
2. **Submit to Glama** — https://glama.ai/mcp/servers
3. **Wait for Glama checks to pass**
4. **Add badge to PR diff** — copy format from merged PRs
5. **Keep body concise** — 1-3 sentences, no arguments about category

## Prevention

- Before submitting to awesome-mcp-servers, verify your server is on Glama
- If your server is stdio-based Python, you need a Dockerfile
- Study 5+ merged PRs to match exact format
