---
type: Community Resource
description: How to contribute to pr-genius
---
# Contributing to pr-genius

> Welcome! This is an AI-agent-maintained knowledge base of PR patterns in big
> open-source repos (star ≥ 1k). We welcome human and AI-assisted contributions.

## TL;DR

| I want to... | Do this |
|---|---|
| Add a new repo profile | `mkdir <org>-<repo>/ && write <org>-<repo>/index.md` |
| Add a PR case study | `write <org>-<repo>/pr-<num>-<slug>.md` |
| Add an anti-pattern | `write anti-patterns/<slug>.md` |
| Add a lesson (MisakaNet mirror) | `write misakanet-50/lesson-NN-<slug>.md` |
| Update an existing case | Edit the relevant `.md` file |
| Run validation | `python3 validate.py` |
| Suggest a topic | Open a [feature request](../../issues/new?template=feature_request.md) |

---

## What we collect

This repo records:

- **Repo Profiles** (`<org>-<repo>/index.md`) — pattern analysis of a single big
  open-source repo. Includes maintainer vibe, merge rate, AI policy,
  contribution SOP, anti-patterns observed, and links to PR case studies.
- **PR Case Studies** (`<org>-<repo>/pr-<num>-<slug>.md`) — detailed log of a
  single PR including rounds (open → bot review → amend → merge/close),
  blockers, resolutions, and lessons learned.
- **Anti-Patterns** (`anti-patterns/<slug>.md`) — generic patterns that cause
  PRs to be closed or rejected. Each entry includes the trigger phrase and
  fix action.
- **Lessons** (`misakanet-50/lesson-NN-*.md`) — distilled lessons sourced from
  PR experience and external knowledge. Mirrors MisakaNet's lesson format.

We do NOT collect:

- Repos with maintainer hostility to AI-assisted PRs (see [BLACKLIST.md](BLACKLIST.md))
- Single-PR failures with no reusable pattern
- Repos smaller than 1k stars (out of scope for "big repo" focus)

---

## Format contract

Every Markdown file MUST start with YAML frontmatter:

```yaml
---
type: Repo Profile | PR Case Study | Anti-Pattern | Lesson | Knowledge Bundle | Schema Reference | Blacklist Reference | Risk Registry | Research Report
title: "Short title"
description: "One-line description"
---
```

See [AGENT_GUIDELINES_SCHEMA.md](AGENT_GUIDELINES_SCHEMA.md) for the
`agent_guidelines` field schema used in Repo Profiles.

See [ROUNDS_SCHEMA.md](ROUNDS_SCHEMA.md) for the `rounds` + `close_decision`
schema used in PR Case Studies.

---

## Profile / Lesson submission examples

**Repo Profile** (e.g., new dir `acme-corp-widgets/` + `index.md`):

```yaml
---
type: Repo Profile
org: acme-corp
repo: widgets
stars: 1234  # at time of writing
forks: 56
language: Python
conforms_to: OKF v0.1
agent_guidelines:
  pr_welcoming: high  # high | medium | low | none
  preferred_labels: [chore, docs]
  anti_terms: ['vibe coded']
  reviewer_response_median_hours: 24
  close_likelihood_estimate: 0.15
  known_blockers: []
federates_with:
  - target: MisakaNet (Ikalus1988/MisakaNet)
    mode: query-only
---
# acme-corp/widgets
...
```

**PR Case Study** (e.g., `acme-corp-widgets/pr-42-foo.md`):

```yaml
---
type: PR Case Study
pr: 42
target_repo: acme-corp/widgets
schema_version: rounds v0.5.0
rounds:
  - round: 1
    at: 2026-07-04T12:00:00Z
    actor: zsxh1990
    action: open
    delta: { kind: code_change, value: "+12 / -2 / 1 files" }
close_decision:
  status: pending  # pending | merged | closed | superseded | keep_open
---
...
```

Both shapes validated by `python3 validate.py`.

---

## AI-assisted contributions

**AI-assisted PRs are welcomed** (this repo is itself AI-maintained). When
opening a PR generated with AI assistance:

1. **Disclose it in the PR body** — "AI-assisted by [tool name]"
2. **Reference your session / prompts** if asked by maintainers
3. **Confirm understanding** — be ready to explain any file you touched
4. **Run `python3 validate.py`** locally before pushing

We follow the same conventions as [OpenClaw's AI-PR guide](#) — explicit
AI-assisted PRs are first-class citizens.

---

## How to run validation locally

```bash
git clone https://github.com/zsxh1990/pr-genius.git
cd pr-genius
python3 validate.py        # soft checks (warnings OK)
python3 validate.py --strict  # hard checks (warnings become errors)
```

The validator checks:
- ✅ YAML frontmatter + required `type` field
- ✅ Internal `.md` links resolve to existing files
- ✅ Root `index.md` consistency
- ✅ Rounds schema v0.5.0 for PR Case Study files

---

## Commit message convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix | Use for |
|---|---|
| `feat:` | New repo profile / new case study / new schema field |
| `fix:` | Broken links, validate.py errors, schema violations |
| `docs:` | README / CONTRIBUTING / index updates (no content change) |
| `chore:` | Maintenance — gitignore, workflows, dependabot |
| `refactor:` | Reorganize existing content without changing meaning |
| `data:` | New data harvest / refresh existing data |

Example: `feat: add NousResearch/hermes-agent repo profile`

---

## Pull Request process

1. **Fork** the repo to your own account (or branch directly if you have write access).
2. **Create a feature branch** — `git checkout -b feat/<org>-<repo>-profile`
3. **Add or edit files** following the format contract.
4. **Run `python3 validate.py`** — must pass without errors (warnings OK).
5. **Open a PR** with:
   - Clear title (Conventional Commits format)
   - Body explaining what you added and why
   - Reference any related issues with `Fixes #N`
6. **Address review feedback** — typical turnaround 1-3 days.

---

## Issue templates

When opening an issue, please use the appropriate template:

- **Bug Report** — broken links, schema violations, validator false-positive
- **Feature Request** — new repo to track, new schema field, new analysis type
- **Profile Suggestion** — suggest a big repo (≥ 1k★) to add as a profile
- **Lesson Contribution** — propose a new misakanet-50 lesson
- **Discussion** — open-ended question / methodology debate

---

## What we DON'T want

- ❌ **Vibe-coded bulk PRs** — opening 5+ profiles at once with no depth
- ❌ **Speculative data** — claiming a repo has X merge rate without verifying
- ❌ **Copied CONTRIBUTING text** — link to upstream CONTRIBUTING.md instead
- ❌ **Sensitive info** — never include real PATs, emails, or personal data

---

## Community

- **Discussions** — [GitHub Discussions](../../discussions)
- **Code of Conduct** — [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- **License** — [MIT](LICENSE)

---

## Versioning

- v0.5.3 (2026-07-02) — current
- v0.5.0 (2026-07-02) — rounds schema v0.2.0
- v0.1.0 (2026-07-01) — initial release