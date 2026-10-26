---
type: Documentation
description: What PR Genius measures, what it does not, and why there is no adoption telemetry
---

# Adoption data: what we know and what we deliberately do not collect

**Short answer: PR Genius has no adoption telemetry. The product cannot tell
you how many people use it — and neither can we, from inside.**

What we *do* have is testimony and solicited evidence: adopters who tell us,
in issues. See [EVIDENCE_BOUNTIES.md](EVIDENCE_BOUNTIES.md) for how that works
and why it is the only mechanism consistent with the privacy promise.

> **A correction.** An earlier version of this page said "we do not know how
> many people use it." That was wrong, and it is exactly the kind of claim this
> page exists to prevent. The truth is narrower and more useful: **the product
> cannot measure adoption, and public code search cannot see our adopters
> either.** Adoption still exists; it is recorded by people, not by software.

This page exists because the README's corpus counts ("N loaded patterns across
M repos") can read like a usage claim. It is not one. It is an inventory of
files in this repository.

## What the visibility measurement says

Run `python3 scripts/discover_action_users.py`. Measured 2026-10-17:

| Channel | Found |
|---|---|
| `uses: zsxh1990/pr-genius` | **0** — real Action users are not indexed, or not public |
| `zsxh1990/pr-genius filename:yml` | 5 raw, 0 adopters |
| broad search | 50 raw, 14 non-adopter mentions (awesome-lists, doc mirrors) |

Known adopters we **cannot** see: **5**.

That number is the important one. Public search is not a usage count, and this
project will never present it as one.

## Telemetry: what ships, and what gave

PR Genius's positioning is that analysis is **local, reproducible and
network-free** — no LLM, no API key, no outbound request while analyzing. That
is not a footnote; it is the reason to choose this over an LLM review bot.

**This page used to say a usage-ping channel would contradict that, "even a
hashed and opt-in one", and that the trade was made deliberately.** That was
the position. #127 risk 5 reversed it, and the sentence you are reading is the
change of mind — not a quiet edit.

What ships is deliberately asymmetric, so that only one of the two halves can
give anything up:

| Layer | Default | Leaves the machine? | What it answers |
|---|---|---|---|
| **Local counters** | **on** | **never** | Which tool ran; which anti-pattern families fired |
| **Network sink** | **off** | only if `PRGENIUS_TELEMETRY_URL` is set | The same counts, aggregated across installs |

The guarantee still holds by default. `PRGENIUS_TELEMETRY_URL` is the switch,
and setting it is the act that gives up "nothing leaves your machine during
analysis". The GitHub Action never sets it (#110 was explicit: the Action runs
on third-party repos where the user has not consented).

`prgenius telemetry status` says which of the two you are on.

### What #110 proposed that this does not do

#110 suggested SHA-1 of `(title || body || repo)[:64]` for dedup. **This does
not do that.** A stable hash of someone's PR text is still a fingerprint of
their work — it correlates the same contribution across time, which is the
identifying power this page exists to withhold. There is no install id, no
machine id, and no other stable token.

The consequence is honest and worth stating plainly: **this cannot measure an
adoption rate.** It can say "coach_pr ran 30 times here" and "tests_in_diff has
never fired". It cannot say whether a suggestion was taken, because that needs
per-PR correlation, which needs identity, which is what is being protected.

### The conditions this page set, kept

This page previously said: *"If it is ever shipped, it will be announced in
`CHANGELOG.md`, documented in `SECURITY.md`, and **off by default
everywhere**."* Those three are done: the CHANGELOG entry calls this a
reversal, [SECURITY.md](../SECURITY.md) has the data-flow description, and the
network sink has no default-on path anywhere — including the Action.

## What we *do* measure

Everything below is measured **inside this repository**, on data we already
own, and published as artifacts anyone can re-run. None of it observes users.

| What | Where it is measured | What it is not |
|---|---|---|
| Tests pass | `pytest prgenius/tests/` in CI (`validate.yml`) | Not "users are happy" |
| Doc claims match the tree | `scripts/verify_claims.py` (release gate) | Not "the docs are useful" |
| Knowledge-bundle integrity | `validate.py`, `--strict`, `--enforce-evidence` | Not "the patterns are right" |
| Pattern trigger coverage on a real PR corpus | `scripts/measure_pattern_coverage.py` over `review-cases/*.json` | Not "patterns fire in production" |
| Evidence debt on case studies | `validate_checks/review_case_evidence.py` + `validate_checks/evidence_debt_baseline.json` | Not "the evidence is true" |
| Profile / policy freshness | `validate_checks/policy_freshness.py` (90-day threshold) | Not "advice is current" |
| Offline accuracy against public PRs | `scripts/cross_validate.py`, `scripts/score_merge.py` → `predictions/` | Not "our advice helps real contributors" |
| MCP tool surface | `verify_claims.py` counts `@mcp.tool` registrations | Not "these tools are called" |

Third-party badges in the README (PyPI version, Glama score, GitHub
Marketplace) are **their** measurements of us, fetched when you load the page.
They are not a channel we open.

## What we still do not know

- Install counts for `prgenius-core` or the GitHub Action
- Whether any suggestion was adopted, or which ones
- Anything at all about the title, body or diff of a PR you analyze

What changed is middle item of the old list. **How often each tool is invoked is
now counted on your machine** — read it with `prgenius telemetry`. That is not
an aggregate and it is not shared unless you turn the sink on.

The last one is the important one, and it is unchanged: **`analyze_pr` /
`coach_pr` / `triage_pr` do not send your PR anywhere.** They read the local
knowledge bundle and return a verdict. The commands that *do* talk to GitHub
(`status`, `auto-ping`, `auto-rebase`, `update-issue`, `harvest`) fetch PR
*metadata* through the API; they are not part of analysis.

If you turn the network sink on, what crosses the wire is the counter file and
nothing else — three keys: `schema`, `client_version`, `events`. No PR data of
any kind, in any form, hashed or not.

## How the corpus numbers should be read

`README.md` opens with a pattern/repo count. That is a file inventory verified
by `scripts/verify_claims.py` against the live tree on every release build. It
says how large the knowledge bundle is. It says nothing about whether anyone
has read it.

If you want evidence that the bundle is *used*, the honest answer is: we do not
have it, and we chose not to build the instrument that would produce it.
