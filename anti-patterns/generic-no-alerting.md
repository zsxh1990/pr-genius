---
type: Anti-Pattern
key: generic-no-alerting
description: "Medium repos reject PRs without alerting"
tags: [generic, anti-pattern]
created: 2026-07-29

trigger_keywords:
  - medium---

# Medium repos reject PRs without alerting

## Pattern

PRs that add monitoring/alerting capabilities are welcome in medium repos. Alerting helps detect issues before they become critical.

## Applicability

All repository sizes, especially medium repos (1k-10k stars) where alerting infrastructure is often missing.
