---
type: PR Case Study
title: "mcphub #987 — sanitize proxychains4 command args to prevent RCE"
pr_number: 987
pr_url: https://github.com/samanhappy/mcphub/pull/987
repo: samanhappy/mcphub
author: zsxh1990
status: closed-merged
opened_at: "2026-07-12"
merged_at: "2026-07-13"
schema_version: rounds v0.5.0
verified_at: "2026-07-17T19:18:00Z"
evidence_urls:
  - https://github.com/samanhappy/mcphub/pull/987
  - https://api.github.com/repos/samanhappy/mcphub/pulls/987
  - https://api.github.com/repos/samanhappy/mcphub/pulls/987/files
  - https://api.github.com/repos/samanhappy/mcphub/issues/987/comments
  - https://api.github.com/repos/samanhappy/mcphub/pulls/987/reviews
  - https://api.github.com/repos/samanhappy/mcphub/pulls/987/commits
confidence: high
rounds:
  - round: 1
    action: open
    delta:
      kind: code_change
      value: "+54 / -1 (1 file: src/services/mcpService.ts)"
    resolution: merged
    timestamp: "2026-07-12"
  - round: 2
    action: amend
    delta:
      kind: code_change
      value: "Block unsafe commands entirely (throw Error), expand sanitization regex"
    resolution: merged
    timestamp: "2026-07-13"
---

## PR #987: RCE security fix

**Issue**: #911 — Critical RCE vulnerability in proxychains4 command wrapping

**Approach**: 
1. Add `isSafeCommand()` — block shell builtins (sh, bash, cmd, etc.)
2. Add `sanitizeArgs()` — remove shell metacharacters
3. Throw Error instead of passing through unsafe commands

**Outcome**: Merged after addressing Gemini Code Review feedback.

**Key Learning**: Security PRs get fast-tracked. Always throw on unsafe input, don't silently pass through.

**Anti-pattern**: Initially passed through unsafe commands without proxy wrapping (still executed, just not proxied).

**Success Factor**: Clear vulnerability description, PoC, fix with tests, quick response to review.
