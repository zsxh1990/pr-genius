---
type: Lesson
domain: "agent-collaboration"
title: "AI Code Review: When to Skip vs When to Read"
verification: "metadata-normalized"
---

# AI Code Review: When to Skip vs When to Read

> Author: 太阳 (Misaka10004)  
> Created: 2026-07-03  
> Status: draft, confidence 0.82  
> Domain: agent-collaboration  
> Source: https://v2ex.com/t/1224476 (V2EX, 68 replies, posted 2026-07-03)

## Problem

As AI coding assistants (Cursor, Codex, Claude Code) become standard tools, developers split into two camps:

**Camp A — Always read AI-generated diffs**: Strict review of every line. Treats AI output as if it were a junior developer's PR.

**Camp B — Trust AI, skip review**: For personal tools or POCs, skip review and rely on functional testing / TDD / end-to-end tests.

V2EX discussion (68 replies) reveals neither extreme is universal truth. Several concrete patterns from working developers:

| Developer | Pattern | Trade-off |
|---|---|---|
| `connor123` | Always reads, fixes style inconsistencies | Time cost, but project coherence preserved |
| `sentinelK` | Argues "code is to the compiler what keyboard is to typing" | Skip is a personal-efficiency choice, not a quality issue |
| `Sezxy` | Reads work code, skips personal projects | Context-dependent |
| `mht` | Reads diffs of existing code, lets AI run on greenfield | Hybrid: read when modifying, trust when creating |
| `sxyclint` | Hasn't read in 1+ year; relies on TDD + e2e + lint + vuln scan | "AI output bugs are smaller than human output bugs" |
| `SayHelloHi` | Vibe coding folder, no manual code, only UI | Pure prototyping mode |
| `Nasdaq` | "cc writes, cx reviews; cx writes, cc reviews" | Cross-agent self-review |

The lesson: **the answer is not "read everything" or "read nothing" — it's about the production-context boundary**.

## Root Cause

The conflict comes from conflating **three different review purposes**:

### 1. Functional correctness review

> "Does this code do what I asked?"

For AI-generated code with concrete acceptance criteria (tests, fixtures), this is **partially replaceable** by automated checks. TDD + integration tests + linter + vuln scanner can catch a large fraction.

### 2. Architectural coherence review

> "Does this code fit the project's existing design?"

This **cannot** be replaced by automated checks because it requires understanding the project's history, the previous design choices, and the implicit conventions. AI output that satisfies type checks and tests can still violate this.

### 3. Knowledge transfer / ownership review

> "Can I understand, debug, and extend this code 6 months from now?"

This **must** be human-driven. If you can't explain the code at a PR review, you won't be able to fix it during an incident.

### The "Vibe Coding" Trap

When AI writes code that **doesn't** integrate into a long-lived project (personal tools, prototypes, throwaway scripts), the third purpose dissolves — there's no "6 months from now" if the code is throwaway. In that case, review-for-ownership is overhead.

But for shared code, this purpose is essential and unreplaceable.

## Solution

A pragmatic review policy that respects the three review purposes:

### Step 1 — Classify the code by lifecycle

For each AI-generated change, ask:

| Question | Yes → | No → |
|---|---|---|
| Will this code be in production in 3 months? | **Strict review** | **Light review** |
| Will a teammate touch this code? | **Strict review** | **Light review** |
| Is there an incident playbook for this code? | **Strict review** | **Light review** |
| Is this throwaway or personal-tool code? | **Light review** | **Light review** (or skip) |

### Step 2 — Apply the right review checklist

**Strict review (production / shared)**:

```python
def strict_ai_review_checklist(diff):
    assert diff.has_prompt_template_version_bump_if_changed(), \
        "Prompt changes must ship with template version + eval"
    assert diff.has_token_budget_annotation(), \
        "Token cost must be visible at the function level"
    assert diff.has_tool_call_audit(), \
        "Tool calls must be auditable (logs, retries)"
    assert diff.has_rollback_plan(), \
        "AI system changes need documented rollback"
    return True
```

**Light review (personal / throwaway)**:

```python
def light_ai_review_checklist(diff):
    assert diff.runs_locally(), "Functional smoke test must pass"
    assert diff.has_no_obvious_security_issues(), "Quick grep for eval/exec/rm -rf"
    return True
```

### Step 3 — Use AI as the first-pass reviewer

For strict review, use **one AI to review another AI's code** (Nasdaq's pattern: "cc writes, cx reviews; cx writes, cc reviews"). This catches 60-70% of the obvious issues faster than a human reviewer can. The human reviewer's job then becomes the architectural coherence + knowledge transfer checks.

### Step 4 — Document the AI-vs-Human boundary explicitly

Put this in your team's `CONTRIBUTING.md`:

> AI-generated code passes the same review gates as human-written code. **Light review is allowed only for code with documented "throwaway" lifecycle**. Code labeled "production" or "shared" must pass the strict review checklist.

## Verification

How to confirm this policy is working:

1. **Production-incident time-to-diagnose** should not regress when AI assists more. If it does, knowledge transfer is failing.
2. **PR review cycle time** should drop for "light review" code (e.g., from 2 days to 4 hours) and stay similar for "strict review" code.
3. **Onboarding time for new devs**: they should still be able to read and understand production code without asking the AI tool to summarize it. If they cannot, knowledge debt has accumulated.

## Verification (self-check)

A short self-check that confirms this lesson is well-formed:

```python
def ai_review_policy_works(team):
    has_classification = team.has_lifecycle_classification_for_prs()
    has_strict_checklist = team.has_strict_review_checklist_for_ai_code()
    has_light_checklist = team.has_light_review_checklist_for_personal_code()
    has_ai_self_review = team.uses_ai_to_review_ai_code()
    has_documented_boundary = team.has_ai_vs_human_review_in_contributing_md()
    return all([has_classification, has_strict_checklist,
                has_light_checklist, has_ai_self_review,
                has_documented_boundary])
```

If `ai_review_policy_works(your_team)` returns False, the team's review policy is undefined.

## Notes

- The phrase "Vibe Coding" was coined by Karpathy for **solo prototyping**. Misusing it for team-shared production code is the root cause of "AI wrote it but I can't debug it" incidents.
- The V2EX thread had 68 replies; the most liked reply was `wangritian`'s analogy: "you don't read the assembler's output. AI coding is the same level of abstraction."
- This lesson's companion: `lesson-01-vibe-coding-team-out-of-control.md` (organizational, not technical, fix).
- Some teams have a separate review for "AI-flagged PRs" — they look for the wrong things (lines, style) instead of the right things (architectural coherence, knowledge transfer).
- Risk: "AI self-review" can hide real issues if both models share the same blind spots. Always have a human in the loop for production code.

## Related Sources

- V2EX thread: https://v2ex.com/t/1224476 (68 replies)
- V2EX related thread: https://v2ex.com/t/1224558 (vibe coding team out of control, 93 replies)
- Pr-genius zsx PR agent: https://github.com/zsxh1990/pr-genius (each PR carries AI disclosure + human review policy)
- LessWrong / Hacker News threads on "AI-assisted code review" (similar patterns documented in English-language communities)