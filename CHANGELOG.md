---
type: Community Resource
description: Changelog following Keep a Changelog format
---
# Changelog

All notable changes to pr-genius are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- 🆕 `NousResearch/hermes-agent/` repo profile (13KB, 300 PR deep research)
- 🆕 `hermes-agent-pr-knowledge/` research bundle (10KB report + 5 raw data files)
- 🆕 7 anti-patterns identified from 300 PR empirical analysis

### Changed
- Updated `NousResearch-hermes-agent/index.md` with corrected external merge rate (13% → 47.3%)
- Cross-linked 11 repo profiles with `federation_mode: query-only` declarations

## [0.5.3] - 2026-07-02

### Added
- `misakanet-50/SCORING.md` — source credibility scoring system (4-dimension)
- `misakanet-50/score_source.py` — scoring automation tool

### Fixed
- `chore: ignore __pycache__ in misakanet-50/` (commit 2aa4468)

## [0.5.2] - 2026-07-02

### Added
- 5 real-failure lessons in `misakanet-50/lesson-06` through `lesson-10`
- Archive flag on 5 news-style lessons (lessons not suitable for distillation)

## [0.5.1] - 2026-07-02

### Added
- 5 misakanet-style lessons (avg 91/100, all A-grade)
- `misakanet-50/lesson-01` through `lesson-05`

## [0.5.0] - 2026-07-02

### Changed (BREAKING)
- Rounds schema upgrade: `action` enum (9 values) + `delta` object + `close_decision` case-level field
- See [ROUNDS_SCHEMA.md](ROUNDS_SCHEMA.md) v0.2.0 for migration guide

### Added
- `mongodb-js-mongodb-mcp-server/pr-1309-azure-readme-version.md` (1 PR case study)
- Updated `README.md` and `KNOWN_ISSUES.md` for v0.5.0

## [0.4.2] - 2026-07-01

### Added
- Real PR loop #2 on `qdrant/mcp-server-qdrant#143` — stale + close-decision sample

## [0.4.1] - 2026-07-01

### Added
- Real PR decision loop on `plastic-labs/honcho#801` — validates rounds field

## [0.4.0] - 2026-07-01

### Changed
- Review: track 4 known data issues + verification plan

## [0.3.0] - 2026-07-01

### Added
- OKF v0.1 federation declaration (`federates_with` field)
- `misakanet_queries` + `misakanet_lessons` fields in 8 repo profiles

## [0.2.0] - 2026-07-01

### Added
- Agent-first upgrade: agent_guidelines field schema (17 keys)
- Blacklist schema + 6 initially-blacklisted repos

## [0.1.0] - 2026-07-01

### Added
- Initial release
- 8 repo profiles (uv / honcho / harbor / fastmcp / sourcebot / future-agi / qdrant / e2b)
- 4 anti-patterns (e2b / honcho / uv / vite)
- OKF v0.1 compliance