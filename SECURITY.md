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
