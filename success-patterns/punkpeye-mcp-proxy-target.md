---
type: Target Pattern
repo: punkpeye/mcp-proxy
created: 2026-07-29
tags: [target, mcp-proxy, typescript]
source_url: https://github.com/zsxh1990/pr-genius/tree/main/success-patterns/punkpeye-mcp-proxy-target.md
updated: 2026-08-01
confidence: medium
---

# mcp-proxy: Contribution Target

## Open Issues

| Issue | Title | Difficulty | Priority |
|-------|-------|------------|----------|
| #71 | Tunnel: 404 | Medium | Medium |
| #20 | Support SSE to streamable HTTP | Medium | High |
| #19 | Allow to proxy HTTP stream servers | Medium | High |

## Recommended First PR

**#20 — SSE to streamable HTTP**: MCP protocol is moving to streamable HTTP. Adding this support to mcp-proxy would be high-value and demonstrates understanding of the MCP transport layer.

## Entry Strategy

1. Open issue comment first: "I'd like to work on #20 — SSE to streamable HTTP support. My approach: ..."
2. Wait for punkpeye's response before implementing
3. Keep PR < 200 lines
4. Include tests

## Risk Assessment

- punkpeye is responsive (< 24h for listings, 1-7 days for code)
- TypeScript codebase — need to match existing style
- No existing contribution from zsxh1990 — first PR matters
