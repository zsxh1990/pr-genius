---
type: Anti-Pattern
key: generic-acid-properties
description: "PR忽视ACID属性"
symptom: "Maintainer comments: 'ACID properties'"
trigger_keywords:
  - "acid properties"
  - "atomicity consistency isolation durability"
fix_action: "1) Ensure ACID; 2) Get approval"
created: 2026-07-29
severity: high
---

# ACID Properties

## Pattern

PRs忽视ACID属性 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Ensure ACID
2. Get approval
