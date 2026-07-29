---
type: Anti-Pattern
key: generic-ai-generated-content
description: "AI-generated content without human review"
symptom: "Maintainer comments: 'This looks AI-generated'"
trigger_keywords:
  - "AI-generated"
  - "ChatGPT"
  - "copilot"
fix_action: "1) Add human review; 2) Verify accuracy; 3) Add personal touches"
severity: critical
---

# AI-Generated Content

## Pattern

PRs with obviously AI-generated content without human review get rejected.

## How to Avoid

1. Review all AI-generated content
2. Verify accuracy
3. Add personal touches and context
