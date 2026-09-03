---
type: Anti-Pattern
key: generic-breaking-change-no-compat
tags: [cron, scheduling, reliability]
description: "Breaking changes without backward compatibility"
symptom: "Maintainer comments: 'This breaks existing users'"
trigger_keywords:
  - "breaking change"
  - "backward incompatible"
fix_action: "1) Add deprecation warnings; 2) Provide migration path"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-breaking-change-no-compat.md
updated: 2026-08-01
confidence: medium

---

# Breaking Change Without Compatibility

## Pattern

Breaking changes without backward compatibility get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add deprecation warnings
2. Provide migration path
3. Update changelog
