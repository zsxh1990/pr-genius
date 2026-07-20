"""Check 6: profile guideline evidence drift detection.

v1.5.0 升级:
- profile 无 agent_guidelines_evidence dict → error
- 字段缺 evidence_url → warning (Month 4 升级 error)
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
    """Check 6: profile guideline evidence required (v1.5.0: error on missing dict).

    Scans <org>-<repo>/index.md (Repo Profile schema) for agent_guidelines.
    Error if: profile has agent_guidelines but no agent_guidelines_evidence dict
    Warn if: individual guideline field missing from agent_guidelines_evidence
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
            errors.append(
                f"{f.relative_to(ROOT)}: agent_guidelines 存在但无 agent_guidelines_evidence dict"
            )
            continue
        for k in gl.keys():
            if k not in evidence:
                warnings.append(
                    f"{f.relative_to(ROOT)}: agent_guidelines.{k} 缺 evidence_url"
                )
    print(
        f"   profiles: {len(profile_files)}, "
        f"without evidence: {profiles_without_evidence}/{len(profile_files)} "
        f"(v1.5.0: error on missing dict, warning on missing fields)"
    )
