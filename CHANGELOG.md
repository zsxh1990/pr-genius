---
type: Community Resource
description: Changelog following Keep a Changelog format + GitHub compare links
---

# Changelog

All notable changes to pr-genius are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this repo uses
GitHub tag/release compare links per Keep a Changelog guidance.

## [Unreleased]

### Added
- 🆕 `SECURITY.md` — coordinated disclosure policy (private advisory + email)
- 🆕 `DISCUSSIONS.md` — placeholder for GitHub Discussions until enabled
- 🆕 `.github/ISSUE_TEMPLATE/config.yml` — chooser config linking to Discussions/Security/MisakaNet
- 🆕 `.github/CODEOWNERS` — singleton maintainer marker
- 🆕 `.github/FUNDING.yml` — sponsors entry
- 🆕 `.github/social-preview.svg` — repo social preview source (requires manual upload via Settings → Social preview)
- 🆕 `docs/INDEX.md` — agent-readable file map (P3 stub, expanded below)
- Topics (10) on GitHub repo settings + extended description + homepage link

## [0.6.0] - 2026-07-03

### Added
- Community surface: README badges/Quick Start, CONTRIBUTING, CODE_OF_CONDUCT, LICENSE (MIT), CHANGELOG, .github/ (5 issue templates + PR template + dependabot + CI validate workflow)
- `scripts/heartbeat.py` + `validate.py --heartbeat` for daily validator snapshots
- `scripts/fix_lesson_yaml{,_v2}.py` repair tools for `last-updated` field
- `NousResearch-hermes-agent/index.md` (16KB profile)

### Stats
- 11 profiles / 11 case studies / 10 lessons / 4 anti-patterns

Compare: [0.5.3...0.6.0](https://github.com/zsxh1990/pr-genius/compare/v0.5.3...v0.6.0)

## [0.5.3] - 2026-07-02

### Added
- `misakanet-50/SCORING.md` — source credibility scoring system (4-dimension)
- `misakanet-50/score_source.py` — scoring automation tool

### Fixed
- `chore: ignore __pycache__ in misakanet-50/` (commit 2aa4468)

Compare: [0.5.2...0.5.3](https://github.com/zsxh1990/pr-genius/compare/v0.5.2...v0.5.3)

## [0.5.2] - 2026-07-02

### Added
- 5 real-failure lessons in `misakanet-50/lesson-06` through `lesson-10`
- Archive flag on 5 news-style lessons (lessons not suitable for distillation)

Compare: [0.5.1...0.5.2](https://github.com/zsxh1990/pr-genius/compare/v0.5.1...v0.5.2)

## [0.5.1] - 2026-07-02

### Added
- 5 misakanet-style lessons (avg 91/100, all A-grade)
- `misakanet-50/lesson-01` through `lesson-05`

Compare: [0.5.0...0.5.1](https://github.com/zsxh1990/pr-genius/compare/v0.5.0...v0.5.1)

## [0.5.0] - 2026-07-02

### Changed (BREAKING)
- Rounds schema upgrade: `action` enum (9 values) + `delta` object + `close_decision` case-level field
- See [ROUNDS_SCHEMA.md](ROUNDS_SCHEMA.md) v0.2.0 for migration guide

### Added
- `mongodb-js-mongodb-mcp-server/pr-1309-azure-readme-version.md` (1 PR case study)
- Updated `README.md` and `KNOWN_ISSUES.md` for v0.5.0

Compare: [0.4.2...0.5.0](https://github.com/zsxh1990/pr-genius/compare/v0.4.2...v0.5.0)

## [0.4.2] - 2026-07-01

### Added
- Real PR loop #2 on `qdrant/mcp-server-qdrant#143` — stale + close-decision sample

Compare: [0.4.1...0.4.2](https://github.com/zsxh1990/pr-genius/compare/v0.4.1...v0.4.2)

## [0.4.1] - 2026-07-01

### Added
- Real PR decision loop on `plastic-labs/honcho#801` — validates rounds field

Compare: [0.4.0...0.4.1](https://github.com/zsxh1990/pr-genius/compare/v0.4.0...v0.4.1)

## [0.4.0] - 2026-07-01

### Changed
- Review: track 4 known data issues + verification plan

Compare: [0.3.0...0.4.0](https://github.com/zsxh1990/pr-genius/compare/v0.3.0...v0.4.0)

## [0.3.0] - 2026-07-01

### Added
- OKF v0.1 federation declaration (`federates_with` field)
- `misakanet_queries` + `misakanet_lessons` fields in 8 repo profiles

Compare: [0.2.0...0.3.0](https://github.com/zsxh1990/pr-genius/compare/v0.2.0...v0.3.0)

## [0.2.0] - 2026-07-01

### Added
- Agent-first upgrade: agent_guidelines field schema (17 keys)
- Blacklist schema + 6 initially-blacklisted repos

Compare: [0.1.0...0.2.0](https://github.com/zsxh1990/pr-genius/compare/v0.1.0...v0.2.0)

## [0.1.0] - 2026-07-01

### Added
- Initial release
- 8 repo profiles (uv / honcho / harbor / fastmcp / sourcebot / future-agi / qdrant / e2b)
- 4 anti-patterns (e2b / honcho / uv / vite)
- OKF v0.1 compliance

[0.1.0]: https://github.com/zsxh1990/pr-genius/releases/tag/v0.1.0
