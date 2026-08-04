---
type: Success Pattern
key: punkpeye-follow-up-strategy
description: "When and how to ping punkpeye on stale PRs"
tags: [follow-up, ping, stale, maintainer-engagement, punkpeye]
created: 2026-07-29
source_url: https://github.com/zsxh1990/pr-genius/tree/main/success-patterns/punkpeye-follow-up-strategy.md
updated: 2026-08-01
confidence: medium
---

# punkpeye Follow-Up Strategy

## Maintainer Profile

- **Maintainer**: punkpeye (personal)
- **Repos**: awesome-mcp-servers (91k), awesome-mcp-devtools (473), fastmcp (3.2k), mcp-proxy (272)
- **Response time**: < 24h for listing PRs, 1-7 days for code PRs
- **Merge style**: Direct merge for listings, review+merge for code

## When to Ping

| Repo Type | Days Before Ping | Ping Method |
|-----------|-----------------|-------------|
| awesome-list PRs | 3 | Reply to own PR |
| fastmcp code PRs | 7 | Reply to own PR |
| mcp-proxy PRs | 7 | Reply to own PR |

## Ping Templates

**Listing PR (awesome-mcp-servers/devtools):**
```
Hi! Friendly ping — this adds [tool] to the list. Glama badge is included. Let me know if anything needs adjusting.
```

**Code PR (fastmcp/mcp-proxy):**
```
Hi! Friendly ping on this PR. CI is green and I'm happy to address any feedback. Is there anything I can improve?
```

## Evidence

- awesome-mcp-servers #10393: No ping needed, merged in < 24h
- awesome-mcp-servers #11128: No ping needed, merged in < 24h
- fastmcp #282: No ping, closed after 4 weeks without review (lesson: PR too large)
- awesome-mcp-devtools #248: Submitted, waiting for response
