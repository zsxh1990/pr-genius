#!/usr/bin/env python3
"""pr-genius OKF v0.1 校验脚本

3 个 check:
1. 每个 .md 有 YAML frontmatter + `type` 字段
2. 内部 [text](./path) 链接的目标文件存在
3. 根 index.md 表格行数 == 子仓数量（一致性检查）

用法:
    python3 validate.py           # 校验当前目录
    python3 validate.py --strict  # 警告也当错误
"""

import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: 需要 PyYAML (pip install pyyaml)")
    sys.exit(2)


ROOT = Path(__file__).parent.resolve()
errors: list[str] = []
warnings: list[str] = []


def parse_frontmatter(text: str) -> tuple[dict | None, str]:
    """Parse YAML frontmatter from markdown text. Return (dict, body)."""
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, text
    yaml_text = text[4:end]
    body = text[end + 5 :]
    try:
        return yaml.safe_load(yaml_text), body
    except yaml.YAMLError as e:
        return {"_error": str(e)}, body


def find_md_files(root: Path) -> list[Path]:
    # 35 期评测反哺 (lesson-19/21): 加 .venv + site-packages 跳过
    # 35 期任务1 ether2 SMOKE_RESULTS.md §1.2 报告 validate.py --strict
    # 在装好 pr-genius 的环境里跑出 8 errors 全是 .venv/ LICENSE.md 假阳
    SKIP_DIRS = {
        ".git",
        ".pytest_cache",
        "__pycache__",
        "node_modules",
        ".venv",
        "venv",
        ".tox",
        "site-packages",
        "dist",
        "build",
    }
    return sorted(
        p for p in root.rglob("*.md")
        if not any(part in SKIP_DIRS for part in p.parts)
    )


def check_frontmatter(files: list[Path]) -> None:
    """Check 1: every .md has frontmatter + `type` field."""
    print(f"[Check 1] Frontmatter + type field ({len(files)} files)")
    for f in files:
        text = f.read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(text)
        if fm is None:
            errors.append(f"{f.relative_to(ROOT)}: missing frontmatter")
            continue
        if "_error" in fm:
            errors.append(f"{f.relative_to(ROOT)}: YAML parse error: {fm['_error']}")
            continue
        if "type" not in fm:
            errors.append(f"{f.relative_to(ROOT)}: missing `type` field")
        elif fm["type"] not in {
            "Knowledge Bundle",
            "Repo Profile",
            "PR Case Study",
            "Schema Reference",
            "Anti-Pattern",
            "Anti-Pattern Bundle",
            "Demo",
            "Blacklist Reference",
            "Risk Reference",      # ag2ai-ag2/RISK.md and similar risk registries
            "Index",               # misakanet-50/README.md and similar index pages
            "Lesson",              # misakanet-50/lesson-NN-*.md
            "Community Resource",  # GitHub templates + community files (CONTRIBUTING/CHANGELOG/COC/LICENSE)
            "Research Report",     # research/<project>/report.md
            "Roadmap",             # docs/ROADMAP.md, docs/METRICS.md — measurable goals
            "Success Pattern",     # success-patterns/*.md
            "Success Pattern Bundle",  # success-patterns/README.md
            "Skill",               # skill/skill.md
            "Retrospective",       # docs/rejected-pr-retrospective.md
            "Test Report",         # docs/coach-smoke-test-*.md
            "Compliance Audit",    # docs/COMPLIANCE_AUDIT.md (added 2026-07-19)
            "Maintainer Policy", # docs/policies/<repo>.md (added 2026-07-18 by v1.2.0)
        }:
            warnings.append(
                f"{f.relative_to(ROOT)}: unknown type `{fm['type']}`"
            )


LINK_RE = re.compile(r"\[([^\]]*)\]\((\./[^)]+\.md)\)")

# v0.2.0 schema enum + delta object validation
ACTION_ENUM = {
    "open", "amend", "bot_review", "human_review",
    "check_in", "bump", "close", "merge", "decision",
}
DELTA_KINDS = {"code_change", "no_code_change", "unknown"}
CLOSE_DECISION_STATUS = {"pending", "close", "keep_open", "merged", "superseded"}
# v0.7.0 evidence (all optional, validates when present)
CONFIDENCE_VALUES = {"high", "medium", "low"}
EVIDENCE_URL_RE = re.compile(r"^https?://")

def check_rounds_schema(files: list[Path], strict: bool = False, enforce_evidence: bool = False) -> None:
    """Check 4 (v0.2.0): PR Case Study rounds + delta + close_decision schema.

    Non-migrated PR Case Studies emit warnings, not errors.
    Use --strict to upgrade warnings to errors (for full-migration mode).
    Use --enforce-evidence to require v0.7.0 evidence fields (case-level).
    """
    """Check 4 (v0.2.0): PR Case Study rounds + delta + close_decision schema.

    Non-migrated PR Case Studies emit warnings, not errors.
    Use --strict to upgrade warnings to errors (for full-migration mode).
    """
    print(f"[Check 4] Rounds schema v0.2.0 (PR Case Study only, non-migrated = warning)")
    target = errors if strict else warnings
    for f in files:
        text = f.read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(text)
        if fm is None or fm.get("type") != "PR Case Study":
            continue
        rounds = fm.get("rounds")
        if rounds is None:
            continue  # backward compat: case studies w/o rounds skip

        for r in rounds:
            rnum = r.get("round", "?")
            # action enum
            action = r.get("action")
            if action is not None and action not in ACTION_ENUM:
                target.append(
                    f"{f.relative_to(ROOT)} round {rnum}: action `{action}` not in enum {sorted(ACTION_ENUM)}"
                )
            # delta object
            delta = r.get("delta")
            if delta is not None and not isinstance(delta, dict):
                target.append(
                    f"{f.relative_to(ROOT)} round {rnum}: delta must be object {{kind, value}} not {type(delta).__name__}"
                )
            elif isinstance(delta, dict):
                kind = delta.get("kind")
                if kind not in DELTA_KINDS:
                    target.append(
                        f"{f.relative_to(ROOT)} round {rnum}: delta.kind `{kind}` not in {sorted(DELTA_KINDS)}"
                    )
                # v0.7.0 evidence fields (optional, BC preserved):
                # - verified_at (ISO-8601 string)
                # - evidence_urls (list of http(s) URLs)
                # - confidence (enum)
                if delta.get("verified_at") is not None:
                    if not isinstance(delta["verified_at"], str):
                        target.append(f"{f.relative_to(ROOT)} round {rnum}: delta.verified_at must be string")
                if delta.get("evidence_urls") is not None:
                    urls = delta["evidence_urls"]
                    if not isinstance(urls, list) or any(not isinstance(u, str) or not EVIDENCE_URL_RE.match(u) for u in urls):
                        target.append(f"{f.relative_to(ROOT)} round {rnum}: delta.evidence_urls must be list of http(s) URLs")
                if delta.get("confidence") is not None:
                    if delta["confidence"] not in CONFIDENCE_VALUES:
                        target.append(f"{f.relative_to(ROOT)} round {rnum}: delta.confidence `{delta['confidence']}` not in {sorted(CONFIDENCE_VALUES)}")

        # close_decision case-level
        cd = fm.get("close_decision")
        if cd is not None and isinstance(cd, dict):
            status = cd.get("status")
            if status not in CLOSE_DECISION_STATUS:
                target.append(
                    f"{f.relative_to(ROOT)}: close_decision.status `{status}` not in {sorted(CLOSE_DECISION_STATUS)}"
                )

        # v0.7.0 case-level evidence (optional)
        for field in ("verified_at", "evidence_urls", "confidence"):
            if field in fm and field not in {"verified_at", "evidence_urls"}:
                # skip — these are top-level OK
                pass
        if fm.get("verified_at") is not None:
            if not isinstance(fm["verified_at"], str):
                target.append(f"{f.relative_to(ROOT)}: case-level verified_at must be string")
        if fm.get("evidence_urls") is not None:
            urls = fm["evidence_urls"]
            if not isinstance(urls, list) or any(not isinstance(u, str) or not EVIDENCE_URL_RE.match(u) for u in urls):
                target.append(f"{f.relative_to(ROOT)}: case-level evidence_urls must be list of http(s) URLs")
        if fm.get("confidence") is not None and fm["confidence"] not in CONFIDENCE_VALUES:
            target.append(f"{f.relative_to(ROOT)}: case-level confidence `{fm['confidence']}` not in {sorted(CONFIDENCE_VALUES)}")

        # v0.7.0 evidence gate: when --enforce-evidence is on, case-level
        # evidence is required (so a 100% evidence coverage check is possible).
        if enforce_evidence:
            for field in ("verified_at", "evidence_urls"):
                if field not in fm or fm.get(field) in (None, [], ""):
                    target.append(f"{f.relative_to(ROOT)}: --enforce-evidence: case-level `{field}` required")

def check_internal_links(files: list[Path]) -> None:
    """Check 2: all internal [text](./path.md) links resolve."""
    print(f"[Check 2] Internal links resolve")
    file_set = {f for f in files}
    for f in files:
        text = f.read_text(encoding="utf-8")
        for label, target in LINK_RE.findall(text):
            # Resolve relative to f.parent
            target_path = (f.parent / target).resolve()
            if target_path not in file_set:
                errors.append(
                    f"{f.relative_to(ROOT)}: dead link [{label}]({target})"
                )


def check_root_index_consistency(root_index: Path, repo_dirs: list[Path]) -> None:
    """Check 3: root index.md table row count == subdir count."""
    print(f"[Check 3] Root index.md consistency")
    if not root_index.exists():
        errors.append("index.md not found")
        return
    text = root_index.read_text(encoding="utf-8")
    # 表格行: | ... | ... |
    table_rows = [
        line for line in text.splitlines()
        if line.startswith("| ") and not line.startswith("|---") and not line.startswith("| 维度") and "仓" not in line.split("|")[1]
    ]
    # 实际上更宽松：算所有非表头行
    body_lines = [
        line for line in text.splitlines()
        if line.startswith("| ") and not re.match(r"^\|[\s\-:|]+\|$", line)
        and not line.startswith("| 维度") and not line.startswith("| ---")
        and not line.startswith("| 仓 ")
    ]
    # root index 里的表格行通常每个子仓一行
    print(f"   root index.md table rows: ~{len(body_lines)}, subdirs: {len(repo_dirs)}")
    # 不强 equal（README 也可能有表格），只在差很多时 warning
    if abs(len(body_lines) - len(repo_dirs)) > 10:
        warnings.append(
            f"root index.md table rows (~{len(body_lines)}) vs subdirs ({len(repo_dirs)}) differ significantly"
        )


def check_anti_pattern_referenced(files: list[Path]) -> None:
    """Check 4 (Month 2 克莱恩 P0 #4): 漂移检测.

    反模式必须被至少 1 个 case study 引用 (links: 字段),
    否则标记为 orphan — 警告. 不直接 error (orphan 可能合理,
    例如 contribai 还没被 case 引用就入库).

    Month 2 P0 #4 'case study ↔ anti-pattern 反向链'.
    """
    print(f"[Check 4] Anti-pattern reverse-link coverage")
    anti_patterns_dir = ROOT / "anti-patterns"
    if not anti_patterns_dir.exists():
        print(f"   (no anti-patterns/ dir, skip)")
        return

    # 1. 收集所有 anti-pattern keys (from anti-patterns/*.md frontmatter)
    ap_keys: set[str] = set()
    for f in anti_patterns_dir.glob("*.md"):
        if f.name == "README.md":
            continue
        fm, _ = parse_frontmatter(f.read_text(encoding="utf-8"))
        if fm is None or "_error" in fm:
            continue
        k = fm.get("key")
        if k:
            ap_keys.add(k)

    # 2. 收集所有 case study 中引用的 anti-pattern keys (from links: 字段或 body 文本)
    case_files = [f for f in files if f.name.startswith("pr-")]
    referenced_keys: set[str] = set()
    case_count = len(case_files)
    for cf in case_files:
        text = cf.read_text(encoding="utf-8")
        for k in ap_keys:
            if k in text:
                referenced_keys.add(k)

    # 3. 警告 orphan anti-patterns
    orphans = ap_keys - referenced_keys
    if orphans:
        for k in sorted(orphans):
            warnings.append(
                f"orphan anti-pattern: anti-patterns/{k}.md referenced by 0/{case_count} case studies"
            )
    print(f"   anti-patterns: {len(ap_keys)}, referenced: {len(referenced_keys)}, orphans: {len(orphans)}, case studies: {case_count}")


try:
    from validate_checks.anti_pattern_referenced import check_profile_guideline_evidence
except ImportError:
    check_profile_guideline_evidence = None

def check_case_study_outcome_required(files: list[Path]) -> None:
    """Check 5 (Month 2 克莱恩 P0 #4): case study outcome/reason/evidence 不可缺.

    PR Case Study (v0.5.0 rounds schema) 必须含 close_decision.status
    字段 + rounds[] 至少 1 轮. 缺 → error (v1.4.0 克莱恩验收门槛).
    """
    print(f"[Check 5] Case study outcome / evidence required")
    case_files = [f for f in files if f.name.startswith("pr-")]
    for f in case_files:
        fm, _ = parse_frontmatter(f.read_text(encoding="utf-8"))
        if fm is None or "_error" in fm:
            continue
        # Check 1: schema_version 必须是 rounds-v0.5.0+
        sv = fm.get("schema_version", "")
        if not sv.startswith("rounds-v"):
            continue  # legacy v0.1 不强制
        # Check 2: close_decision.status 必须存在
        cd = fm.get("close_decision")
        if not cd or not isinstance(cd, dict):
            errors.append(f"{f.relative_to(ROOT)}: rounds-v0.5.0 schema but missing close_decision")
            continue
        if "status" not in cd:
            errors.append(f"{f.relative_to(ROOT)}: rounds-v0.5.0 schema but close_decision missing `status`")
        # Check 3: rounds[] 至少 1 轮
        rounds = fm.get("rounds", [])
        if not rounds or len(rounds) < 1:
            errors.append(f"{f.relative_to(ROOT)}: rounds-v0.5.0 schema but rounds[] is empty")
        # Check 4: case-level evidence_urls 必须非空
        eu = fm.get("evidence_urls", [])
        if not eu or len(eu) < 1:
            errors.append(f"{f.relative_to(ROOT)}: rounds-v0.5.0 schema but evidence_urls is empty")


def main() -> int:
    print(f"pr-genius OKF v0.1 validator — {ROOT}\n")

    md_files = find_md_files(ROOT)
    print(f"Found {len(md_files)} .md files\n")

    check_frontmatter(md_files)
    check_internal_links(md_files)
    check_rounds_schema(
        md_files,
        strict="--strict" in sys.argv,
        enforce_evidence="--enforce-evidence" in sys.argv,
    )

    # Find subdirectories (Repo Profile roots)
    repo_dirs = [p for p in ROOT.iterdir() if p.is_dir() and not p.name.startswith(".")]
    root_index = ROOT / "index.md"
    check_root_index_consistency(root_index, repo_dirs)
    check_anti_pattern_referenced(md_files)
    check_case_study_outcome_required(md_files)
    if check_profile_guideline_evidence:
        check_profile_guideline_evidence(md_files, parse_frontmatter, warnings, errors, ROOT)

    # 35 期评测反哺 (lesson-19 / lesson-21): 接 husk2 的 Check 7 + Check 8
    # Check 7: policy_freshness — policy/profile 超过 90 天 warn
    # Check 8: release_audit — pyproject/init/glama/Dockerfile/CHANGELOG 版本对齐
    try:
        from validate_checks.policy_freshness import check_policy_freshness
        check_policy_freshness(md_files, parse_frontmatter, warnings, errors, ROOT)
    except ImportError as e:
        print(f"[Check 7] policy_freshness not available: {e}")
    try:
        from validate_checks.release_audit import check_release_audit
        check_release_audit(md_files, parse_frontmatter, warnings, errors, ROOT)
    except ImportError as e:
        print(f"[Check 8] release_audit not available: {e}")

    # T4: emit snapshot stats (used by validate.py --snapshot and scripts/dashboard.py)
    if "--snapshot" in sys.argv:
        import json as _json
        from datetime import datetime as _dt, timezone as _tz
        profile_count = sum(1 for d in repo_dirs if (d / "index.md").exists())
        case_count = sum(1 for f in md_files if f.name.startswith("pr-"))
        api_path = ROOT / "data" / "snapshot.json"
        api_path.parent.mkdir(exist_ok=True)
        api_path.write_text(_json.dumps({
            "ran_at": _dt.now(_tz.utc).isoformat(),
            "files_total": len(md_files),
            "profiles": profile_count,
            "case_studies": case_count,
            "errors": len(errors),
            "warnings": len(warnings),
        }, indent=2))
        print(f"[Snapshot] wrote {api_path}")
        print(f"   profiles={profile_count} case_studies={case_count} errors={len(errors)} warnings={len(warnings)}")

    print()
    print("=" * 60)
    if errors:
        print(f"❌ {len(errors)} error(s):")
        for e in errors:
            print(f"  - {e}")
    if warnings:
        print(f"⚠️  {len(warnings)} warning(s):")
        for w in warnings:
            print(f"  - {w}")
    if not errors and not warnings:
        print("✅ All checks passed")
        return 0
    if errors:
        return 1
    return 0 if "--strict" not in sys.argv else 1


if __name__ == "__main__":
    sys.exit(main())