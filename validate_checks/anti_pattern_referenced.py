"""Check 6: profile guideline evidence drift detection.

v1.5.1 升级 (2026-07-21):
- profile 无 agent_guidelines_evidence dict → error
- 自动衍生 / 元数据字段 (default_branch, bot_review, response_time_h_median,
  external_merge_rate*, ci_first_run_needs_approval, one_pr_friendly, merge_rate_30d)
  不需要外部 evidence_url → 不占 warning (they are measurable from public data
  and the measurement itself is the evidence; flagging them produced 465 false
  warnings that made `validate --strict` unusable).
- Boolean-false / "none" / empty-list 等"否定性策略"字段: 证据就是 CONTRIBUTING
  没有提这件事 (absence of requirement = policy), 允许缺 evidence_url。
- 只有"肯定性策略声明" (true / 字符串 / 非空 list / dict) 才要求 evidence_url。
"""
from __future__ import annotations

import re
from pathlib import Path


# Fields that are auto-derived metadata, measured from public GitHub data,
# or well-known defaults — they don't require a hand-picked evidence URL.
AUTO_DERIVED_FIELDS = {
    "default_branch",
    "bot_review",
    "response_time_h_median",
    "response_time_h",
    "ci_first_run_needs_approval",
    "one_pr_friendly",
    "merge_rate_30d",
    "merge_rate",
    "external_merge_rate",
    "external_merge_rate_30",
    "external_merge_rate_30_initial_estimate",
    "overall_merge_rate_300",
    "external_pr_count",
    "zsxh_pr_count",
    "analyzed_at",
}

# Field-name suffixes/prefixes that mark a value as a quantitative measurement
# derived from public GitHub data (the measurement itself is the evidence; no
# hand-picked URL needed). Matched case-insensitively.
_AUTO_DERIVED_NAME_PATTERNS = (
    "_merge_rate",       # external_merge_rate_30, overall_merge_rate_300, ...
    "_merge_rate_",
    "_pr_count",         # external_pr_count, zsxh_pr_count
    "_response_time",    # response_time_h_median, response_time_h
    "_initial_estimate", # external_merge_rate_30_initial_estimate
)


def _is_auto_derived(name: str) -> bool:
    if name in AUTO_DERIVED_FIELDS:
        return True
    lname = name.lower()
    return any(p in lname for p in _AUTO_DERIVED_NAME_PATTERNS)

# Fields whose "false"/"none"/empty value represents "policy does not require X",
# where the CONTRIBUTING / official docs NOT mentioning X is itself the evidence.
# (If these fields have a positive/non-default value they DO need evidence.)
BOOLEAN_POLICY_FIELDS = {
    "require_signed_off",
    "require_cla",
    "require_changeset",
    "require_issue_first",
    "ai_assisted_disclosure",
    "allow_unsolicited_pr",
}


def _is_affirmative_claim(value) -> bool:
    """A value that commits the profile to a non-trivial maintainer policy."""
    if value is None:
        return False
    if isinstance(value, bool):
        return value is True
    if isinstance(value, str):
        v = value.strip().lower()
        if v in ("", "none", "false", "n/a", "unknown"):
            return False
        return True
    if isinstance(value, list):
        return len(value) > 0
    if isinstance(value, dict):
        return len(value) > 0
    return True


def check_profile_guideline_evidence(
    files: list[Path],
    parse_frontmatter,
    warnings: list[str],
    errors: list[str],
    ROOT: Path,
) -> None:
    """Check 6: profile guideline evidence (tiered policy).

    - error if agent_guidelines present but agent_guidelines_evidence dict missing
    - warning only on affirmative policy claims lacking evidence_url
    - auto-derived metadata fields and false/none policy fields are excused
    """
    print(f"[Check 6] Profile guideline evidence (tiered)")
    profile_files = [
        f for f in files
        if f.name == "index.md"
        and re.match(r"^[a-zA-Z0-9_-]+-[a-zA-Z0-9_-]+$", f.parent.name)
    ]
    profiles_without_evidence = 0
    missing_field_count = 0
    for f in profile_files:
        fm, _ = parse_frontmatter(f.read_text(encoding="utf-8"))
        if fm is None or "_error" in fm:
            continue
        if fm.get("type") != "Repo Profile":
            continue
        gl = fm.get("agent_guidelines")
        if not isinstance(gl, dict):
            continue
        evidence = fm.get("agent_guidelines_evidence")
        if evidence is None or not isinstance(evidence, dict):
            profiles_without_evidence += 1
            errors.append(
                f"{f.relative_to(ROOT)}: agent_guidelines 存在但无 agent_guidelines_evidence dict"
            )
            continue
        for k, v in gl.items():
            if _is_auto_derived(k):
                continue
            if k in BOOLEAN_POLICY_FIELDS and not _is_affirmative_claim(v):
                continue
            if not _is_affirmative_claim(v):
                continue
            if k not in evidence:
                missing_field_count += 1
                warnings.append(
                    f"{f.relative_to(ROOT)}: agent_guidelines.{k} 缺 evidence_url"
                )
    print(
        f"   profiles: {len(profile_files)}, "
        f"without evidence dict: {profiles_without_evidence}/{len(profile_files)}, "
        f"affirmative-policy fields missing URL: {missing_field_count}"
    )
