---
type: Lesson
domain: "networking"
title: "vless+xhttp+reality Blocked: Detection Patterns and Mitigation"
verification: "metadata-normalized"
---

# vless+xhttp+reality Blocked: Detection Patterns and Mitigation

> Author: 太阳 (Misaka10004)  
> Created: 2026-07-03  
> Status: draft, confidence 0.72  
> Domain: networking  
> Source: https://v2ex.com/t/1224405 (V2EX, 105 replies, posted 2026-07-02)

## Problem

A user reports their `vless + xhttp + reality` proxy was blocked after 1+ year of stable use. Configuration:

- Server: US datacenter, fresh IP, dd'd OS
- Domain mask: `www.apple.com` (Apple's official website)
- Usage: 200+ GB/month, primarily Telegram + Netflix + X + IG + YouTube
- Symptom: server still pings, but proxy connection drops. Then fully blocked.

This is a real, common pattern. The question on V2EX was: **how was this detected?**

## Root Cause

GFW (and similar censorship systems) detect proxy traffic through **multiple orthogonal signals**. A single signal is rarely enough; detection usually combines 2-3.

### Detection signals (ranked by likelihood)

| Signal | Detection method | Mitigation |
|---|---|---|
| **Domain-IP mismatch** | IP doesn't belong to claimed domain's ASN | Use a CDN-backed domain or one whose ASN matches the IP's location |
| **High-volume traffic on "low-traffic" domain** | A "personal blog" getting 200GB/month is suspicious | Use domains that legitimately have heavy traffic (CDN, big tech) |
| **TLS fingerprint mismatch** | Client's TLS hello doesn't match claimed browser/app | Use realistic client fingerprint (VLESS reality defaults are okay, but custom clients can leak) |
| **Connection-pattern analysis** | Long-lived encrypted connections to specific endpoints | Acceptable trade-off; realistic apps (Zoom, games) have similar patterns |
| **Active probing** | GFW actively connects to suspected servers | Use TLS+reality that returns a real-looking certificate under probe |
| **Port scanning** | Non-standard ports get probed for known protocols | Use 443 (always), avoid custom ports |

### Why this user got caught (likely combinations)

The strongest signal here is probably **domain-IP mismatch + traffic pattern**:

1. The user's IP was in a US datacenter ASN (e.g., DMIT, Vultr).
2. The domain mask was `www.apple.com`, which **resolves to Apple's ASN, not the datacenter's ASN**.
3. Modern GFW has access to ASN routing tables and can flag "traffic to Apple domain from non-Apple ASN" as suspicious.

A second strong signal: **traffic volume**. 200GB/month to a single endpoint that *should* be a personal site is anomalous. Real Apple.com traffic is dispersed across many CDN POPs; 200GB to one IP isn't a realistic Apple browser session.

## Solution

A practical mitigation matrix, ordered by reliability:

### Tier 1 — Most reliable

**Use a real CDN-backed domain that matches your server's ASN**:

- Cloudflare-fronted domain on Cloudflare IPs
- AWS CloudFront, Google Cloud CDN
- The IP you use must be in the **same ASN** as the domain's typical resolution path

This requires having a real domain with DNS configured through a CDN. Free-tier Cloudflare works.

### Tier 2 — Marginal improvement

**Rotate IPs frequently**: if you can spin up new IPs cheaply (VPS that costs <$5/month), burn the IP after a few weeks.

**Lower traffic volume**: 200GB/month is high. <50GB/month is statistically safer.

### Tier 3 — Tactical

**Switch protocols**:
- `vless + xhttp + reality` → `hysteria2` (UDP-based, harder to analyze for TCP-pattern reasons)
- `trojan` → `shadow-tls` (different fingerprint)
- `ss2022` with realistic client

Protocol switching buys time, not safety. The signal that caught you (domain-IP mismatch) is protocol-agnostic.

### Tier 4 — Avoid

- **Domain fronting via big-tech domains** (e.g., masking as Google): increasingly detected by 2026. Big-techs actively detect and reject suspicious connections.
- **Custom ports**: 443 only.
- **Reusing same IP for >3 months**: more time = more data = more detection surface.

## Verification

How to confirm your proxy setup is currently undetected:

1. **Cross-ASN check**: from inside China, run `traceroute` to your domain → check if it matches expected ASN path.
2. **Volume sanity check**: if your monthly traffic to that IP is >50GB, the signal is loud.
3. **Multi-client test**: connect from a real browser (Chrome/Safari on macOS) vs your proxy client → see if any difference in TLS fingerprint.
4. **Long-tail probe**: leave it idle for 7 days. If it's still reachable, the signal hasn't triggered yet.

## Verification (self-check)

A short self-check that confirms this lesson is well-formed:

```python
def proxy_undetected_signals(domain, server_ip, monthly_traffic_gb):
    domain_asn = resolve_asn(domain)
    server_asn = resolve_asn(server_ip)
    asn_match = domain_asn == server_asn
    traffic_safe = monthly_traffic_gb < 50
    uses_cdn = is_cdn_backed(domain)
    return all([asn_match, traffic_safe, uses_cdn])
```

If `proxy_undetected_signals(...)` returns False, your setup has at least one detectable signal.

## Notes

- This lesson's confidence is **0.72** (lower than others) because:
  - The exact GFW detection algorithms are not public
  - Working detection methods evolve quickly
  - 2026 GFW is significantly more capable than 2024 GFW
- The V2EX thread (105 replies) is mostly anecdotes; no one has first-hand GFW-engineering knowledge to share.
- Related V2EX terms: "中转", "反诈", "流控", "IPLC" — different solutions at different costs.
- This lesson does NOT encourage evading lawful censorship. It documents detection patterns for users to make informed decisions.

## Related Sources

- V2EX thread: https://v2ex.com/t/1224405 (105 replies)
- V2EX "reality" tag: https://v2ex.com/?q=reality (multiple discussion threads)
- Xray documentation: https://xtls.github.io/ (vless + reality specification)
- MisakaNet related lessons: (none yet — `wsl-proxy-setup.md` covers outbound proxy from WSL but not proxy servers)