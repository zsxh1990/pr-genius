"""Check 6 (Month 2 P0 #5): profile guideline evidence drift detection.

克莱恩 2026-07-19 路线图: 'repo profile 里的 guideline 必须有证据'.

agent_guidelines 17 字段当前没有 evidence 字段 — agent 无法追溯
true/false 值来源 (CONTRIBUTING.md / 实测 PR / 调研报告).

新增 v0.2 字段:
    agent_guidelines_evidence:
      ai_policy: 'https://github.com/X/Y/blob/main/CONTRIBUTING.md'
      maintainer_vibe: 'https://github.com/X/Y/issues/N'

当前实现: warning only (现有 49 profile 全 missing,
一次性 error 会破坏 validate.py 通过状态).
Month 3 才升级 error.
"""
from __future__ import annotations

import re
from pathlib import Path


def check_profile_guideline_evidence(
    files: list[Path],
    parse_frontmatter,
    warnings: list[str],
    errors: list[str],
    ROOT: Path,
) -> None:
    """Check 6: profile guideline evidence required.

    Scans <org>-<repo>/index.md (Repo Profile schema) for agent_guidelines.
    Warns if:
    - profile has agent_guidelines but no agent_guidelines_evidence dict
    - a guideline field is in agent_guidelines but missing from agent_guidelines_evidence
    """
    print(f"[Check 6] Profile guideline evidence required")
    profile_files = [
        f for f in files
        if f.name == "index.md"
        and re.match(r"^[a-zA-Z0-9_-]+-[a-zA-Z0-9_-]+$", f.parent.name)
    ]
    profiles_without_evidence = 0
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
            continue
        for k in gl.keys():
            if k not in evidence:
                warnings.append(
                    f"{f.relative_to(ROOT)}: agent_guidelines.{k} 缺 evidence_url"
                )
    print(
        f"   profiles: {len(profile_files)}, "
        f"without evidence: {profiles_without_evidence}/{len(profile_files)} "
        f"(Month 2 过渡期 warning only, Month 3 升级 error)"
    )
