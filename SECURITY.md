---
type: Community Resource
title: Security & Coordinated Disclosure
description: How to report security issues in pr-genius content / schemas / docs.
version: 1.0.0
created: 2026-07-04
---

# Security Policy

pr-genius is a knowledge repo: plain Markdown files, OKF v0.1 YAML frontmatter,
and a Python validator (`validate.py`). It runs **no server, no network, no
untrusted code execution** — so the attack surface is small. This page
documents what to report anyway.

## What to Report

| Layer | Risk vector | Worth reporting? |
|---|---|---|
| **Repo content** (`.md`, `.yaml` frontmatter) | XSS via misrendering if a viewer renders raw HTML / `javascript:` URLs | Yes |
| **`scripts/heartbeat.py` / `scripts/fix_lesson_yaml*.py`** | If a malicious PR introduces `subprocess` / `eval` calls | **Yes (high)** |
| **`validate.py`** | Same as above | **Yes (high)** |
| **GitHub Action `.github/workflows/validate.yml`** | Supply chain on `actions/checkout` / similar | **Yes (medium)** |
| **OKF schema fields** (`conforms_to`, `agent_guidelines`, `rounds`) | If a malicious profile teaches dangerous agent behavior | Yes |
| **`federates_with` claims** | Cross-repo claim that misleads agents about provenance | Yes |
| **READMEs and contributor guidance** | Social-engineering wording that misleads contributors | Yes |

## Reporting Channel

**Please do NOT open a public GitHub issue for security issues.**

Reach the maintainer via one of:

- **GitHub private advisory**: https://github.com/zsxh1990/pr-genius/security/advisories/new
- **Direct email**: see the commit author email on the latest commit (`git log -1 --format='%ae'`)

We aim to acknowledge within 72 hours and triage within 7 days.

## Scope / Out of Scope

- **Out of scope**: CVEs in third-party dependencies we cite (we have no deps; the repo runs on plain Python 3.9+ stdlib).
- **Out of scope**: vulnerabilities in upstream open-source projects profiled
  in `*-<repo>/index.md`. Report those to the upstream project, not here.
- **In scope**: content of this repo only.

## Privacy: what leaves your machine

**Nothing during analysis, by default.** `analyze_pr`, `coach_pr`,
`triage_pr`, `contributor_view` and `maintainer_view` read the local knowledge
bundle and return a verdict. No LLM call, no API key, no outbound request.

Commands that do talk to GitHub (`status`, `auto-ping`, `auto-rebase`,
`update-issue`, `harvest`) fetch PR **metadata** through the API using a token
you supply. They are not part of analysis.

### Adoption counters (added 2026-10-26 — this reverses a documented trade)

This section previously ended with **"There is no adoption telemetry"** and a
promise that any future telemetry would be off by default, announced in
`CHANGELOG.md`, and documented here first. #127 risk 5 reversed that decision.
All three of those conditions are met, and the reversal is stated rather than
slipped in.

**Layer 1 — local counters, on by default, never transmitted.**

| | |
|---|---|
| What | Invocation counts per tool (`cli.analyze`, `mcp.coach_pr`, …) and per anti-pattern **family** that fired (`install_surface`, `secret_shaped`, …) |
| Where | `~/.config/prgenius/telemetry.json`, or `PRGENIUS_TELEMETRY_DIR` |
| Leaves the machine | **Never.** |
| Inspect / delete | `prgenius telemetry` / `prgenius telemetry reset` |

Not recorded, in any form, hashed or not: PR title, body, repo name, author,
diff, issue number, labels, or any stable identifier. There is no install id,
no machine id, no UUID. `telemetry.record()` takes no free-form payload — the
TypeError is the guard, and a test asserts the state file carries no PR
identifiers.

**Layer 2 — network sink, off by default.**

Active only when `PRGENIUS_TELEMETRY_URL` is set. It POSTs the counter file and
nothing else:

```json
{"schema": 1, "client_version": "2.2.5", "events": {"mcp.coach_pr": 12}}
```

Setting that variable **is** the act that gives up "nothing leaves your machine
during analysis". `prgenius telemetry status` tells you which layer you are on.

The GitHub Action never sets it. It runs on third-party repositories whose
users have not consented (#110).

### What this deliberately cannot measure

An **adoption rate** — whether a suggestion was taken. That needs per-PR
correlation, which needs a stable identifier, which is the thing being
protected. #110 proposed SHA-1 of the input arguments for exactly this and this
implementation does not do it: a stable hash of someone's PR text is still a
fingerprint of their work. The counters answer "is this tool used" and "has
this pattern ever fired"; they cannot answer "did the advice help".

Report a leak: if you ever observe PR content in a payload or in
`telemetry.json`, that is a security bug — report it through the channel above.

## Dependency pinning

`action.yml` installs `prgenius-core` with an explicit upper bound
(`>=2.0,<2.99`) rather than an open range. The bound is a **tripwire, not a
semver boundary**: crossing it requires a deliberate edit to `action.yml`, so a
breaking release cannot reach Action consumers on publish day without someone
looking at it. Bumping the bound is part of the release checklist, not
something dependabot does.

## Disclosure Timeline

1. **T+0** — private report received
2. **T+72h** — ack + severity triage
3. **T+7d** — fix proposed or "won't fix, here's why"
4. **T+14d** — public disclosure (after fix lands or waiver negotiated)

We follow a "coordinated disclosure" model. Reporters who follow this policy
will be credited in the fix commit unless they ask otherwise.

## Friendly Notes

pr-genius content is meant for **AI agents to ingest**. If you find wording
that, when ingested by an LLM, makes the agent perform an unsafe action —
that is a *content* vulnerability. Please report it.

Thanks for keeping agent-readable knowledge bases honest.
