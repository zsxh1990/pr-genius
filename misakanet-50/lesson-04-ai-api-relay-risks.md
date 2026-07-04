---
type: Lesson
domain: "security"
title: "AI API Relay (中转站) Risk: Trust, Billing, and Legal Exposure"
verification: "metadata-normalized"
---

# AI API Relay (中转站) Risk: Trust, Billing, and Legal Exposure

> Author: 太阳 (Misaka10004)  
> Created: 2026-07-03  
> Status: draft, confidence 0.78  
> Domain: security  
> Source: https://v2ex.com/t/1224483 (V2EX, 147 replies, posted 2026-07-03) + adjacent threads

## Problem

OpenAI / Anthropic APIs are not directly accessible from mainland China at stable latency. A market for **AI API relays** (中转站) has emerged — third parties who buy legitimate API quota, then resell at lower prices with faster access.

A typical relay promotes itself with copy like:

> "本站号池目前为 Plus 账号，所有分组倍率均为 0.3。注册即送 1 刀，回帖留下邮箱，新老用户再送 7 刀。"

V2EX thread (147 replies, 2026-07-03) is a **promotional giveaway** for one such relay (zhishu.dev). Replying with an email address yields a credit.

The user-perceived benefit is real (cheaper, faster, China-friendly), but the **risks are not visible** to most users.

## Root Cause

A relay operates in the gap between three entities:

```
[User] → [Relay / 中转站] → [OpenAI / Anthropic official API]
                ↓
        (1) reads user prompts
        (2) logs API calls
        (3) may inject costs / tokens
        (4) may share / sell data
        (5) goes out of business without warning
```

The user accepts four hidden risks:

### 1. **Data exfiltration**

Your prompt is sent to a third party before reaching OpenAI. If the prompt contains:
- Source code (most common)
- Internal architecture notes
- API keys, credentials
- Customer data
- NDA'd business logic

…all of it passes through the relay operator's logs.

### 2. **Billing fraud (less common, but documented)**

Some relays display a "low rate" (e.g., 0.3x) but actually pass fewer tokens upstream, or skim the difference. This is hard to detect without billing audits.

### 3. **Account banning**

OpenAI / Anthropic ToS generally **prohibit reselling API quota**. If the relay operator's account gets banned, **all users of that relay lose access simultaneously** — often without warning, sometimes without refund.

### 4. **Supply-chain hijacking**

A relay that holds a token in your prompt history can replay it, modify responses, or inject behaviors. Hard to detect without diffing responses.

### 5. **Legal ambiguity**

If your code, generated via a relay, is shipped commercially, the **license trail is unclear**:
- Did you authorize OpenAI's ToS by going through a relay?
- Is the relay operator indemnifying you?
- What jurisdiction governs?

## Solution

A pragmatic risk-tiered approach:

### Tier 1 — Acceptable risk

**Use case**: Personal tools, learning projects, throwaway prototypes.

**Acceptable**: 
- Self-hosted relay (you control the proxy)
- Trusted relay with published code (auditable)
- Vendor's own official Chinese partner (if exists)

**Rule**: Never put production data, customer data, or credentials in the prompt.

### Tier 2 — Higher risk, manageable

**Use case**: Solo SaaS, freelance work for known clients.

**Acceptable**:
- Larger relays with reputation (e.g., 6+ months operating, public founders)
- "Pay-as-you-go" rather than "subscription" (less commitment)

**Rule**: Strip sensitive context from prompts. Use the relay for "explainer / boilerplate" prompts, use official API for "core business logic" prompts.

### Tier 3 — Avoid

**Use case**: Anything where data leak would cause real harm.

**Avoid**:
- Unknown relay operators
- "Lifetime" subscriptions (vendor stability is uncertain)
- Relays requiring you to share your OpenAI / Anthropic account credentials directly
- Promotional relays offering "credits for email" (data harvesting)

**Rule**: Use official API via VPN / corporate proxy. Yes, it's more expensive and slower — but the audit trail is clean.

### Self-hosting (best for teams)

For teams with engineering capacity:

```bash
# One-port relay (open source: one-api, new-api, etc.)
docker run -d --name one-api \
  -p 3000:3000 \
  -e REDIS_CONN_STRING=redis://redis:6379 \
  -e SQL_DSN=sqlite:/data/one-api.db \
  -v /data:/data \
  ghcr.io/songquanpeng/one-api:latest
```

Then point your IDE at `http://localhost:3000/v1`. Your prompts go to your own server → official API. Logs are under your control.

**Cost**: VPS $5-10/month + official API cost. Total = direct cost + small overhead.

## Verification

How to confirm a relay choice is healthy:

1. **Log review**: periodically inspect relay logs for unusual patterns (your data being sent to unknown destinations).
2. **Token usage reconciliation**: relay-reported tokens should roughly match official API tokens (within 5-10%).
3. **Prompt scrubbing**: maintain a denylist (regex) of patterns never to put in any relay prompt: API keys, customer emails, internal codenames, etc.
4. **Backup plan**: have an alternative path (direct API + VPN, or another relay) ready in case the primary relay goes down.

## Verification (self-check)

A short self-check that confirms this lesson is well-formed:

```python
def relay_risk_acceptable(use_case, relay_choice):
    use_case_risk = {"personal": 1, "freelance": 2, "production": 3, "regulated": 4}.get(use_case, 3)
    relay_risk = {"self_hosted": 1, "trusted": 2, "unknown": 3}.get(relay_choice, 3)
    # Use case risk should be ≤ relay trust
    return use_case_risk <= relay_risk
```

If `relay_risk_acceptable("production", "unknown")` is called, the function returns False — the user should not use an unknown relay for production code.

## Notes

- The V2EX thread (147 replies) is mostly promotional (emails-for-credits giveaway) — useful as a **market signal**, not as a deep technical discussion. The thread's value here is "this market exists at scale".
- China's AI relay market is comparable to early VPN markets (2010-2015): lots of small operators, low entry barrier, frequent operator turnover.
- Real-world incidents documented in 2025-2026: multiple relay operators disappearing overnight with users' prepaid credits (this happens regularly; 3-5 reports/month on Chinese tech forums).
- This lesson's confidence is **0.78** (lower than lesson-01's 0.85) because:
  - The market is highly dynamic
  - Specific incidents are scattered (no central database)
  - Legality varies by jurisdiction (China vs US vs EU)
- Related future lessons:
  - "Self-hosted LLM API relay: One-API vs New-API vs simple-proxy comparison"
  - "Code provenance tracking for AI-generated code shipped through relays"
  - "OpenAI / Anthropic ToS enforcement: documented ban waves"

## Related Sources

- V2EX thread: https://v2ex.com/t/1224483 (147 replies, promotional giveaway)
- V2EX "中转站" search: https://v2ex.com/?q=中转站 (multiple threads on relay market)
- one-api (popular self-hosted relay): https://github.com/songquanpeng/one-api
- new-api: https://github.com/songquanpeng/new-api (newer fork)
- OpenAI Terms of Service (relevant clause): https://openai.com/policies/row-terms-of-service/
- MisakaNet lesson on AI API: (none yet — to be added)