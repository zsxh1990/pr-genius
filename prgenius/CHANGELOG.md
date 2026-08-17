# Changelog

All notable changes to PR Genius will be documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.2.0] - 2026-08-17

### Added
- **Issue Evaluator** (`prgenius issue`): automated issue quality review
  - Quality scoring: 0–100 scale, 5 dimensions (title/body/labels/structure/secrets)
  - Tier classification: low_risk / medium_risk / high_risk
  - Signals output: positive / negative / neutral (aligned with PR Coach)
  - Checklist output: actionable items with priority and done status
  - Spam detection with context window (short body + keyword = higher confidence)
  - Secret detection: 9 regex patterns (AWS, GitHub, GitLab, Slack, Bearer Token, etc.)
  - Crawler-friendly label detection (≥3 labels required)
- **Batch review** (`prgenius issue-batch`): scan issues by label with statistics
- **285 tests** across 21 test classes:
  - Adversarial spam tests (Unicode homoglyphs, ZWS, leet speak)
  - Performance: 1000 issues <1s, 10k <5s
  - Real issue validation: 15 repos, stratified sampling
  - MisakaNet 20% sample: 40 issues

### Changed
- Output structure aligned with PR Coach (`analyze_pr()`):
  - `risk` → `tier` (low_risk / medium_risk / high_risk)
  - `issues[]` → `signals.negative[]` (key, description, severity)
  - `suggestions[]` → `checklist[]` (action, priority, done, hint)
- `_calculate_risk()` replaced by `_calculate_tier(signals_neg, signals_pos, score)`
- `_generate_suggestions()` removed, replaced by inline checklist generation

## [1.1.0] - 2026-08-10

### Fixed
- JSON anti-pattern false positives in coach
- Merge rate offset for big repos (accuracy 79% → 87%)

## [1.0.0] - 2026-08-04

### Added
- PR Coach: automated PR quality review with signals/checklist/tier
- Maintainer View: 5-action routing + review queue digest
- Positive confirmation summary (borrowed from Cubic AI)
- Installation guide for new contributors
