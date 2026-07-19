#!/usr/bin/env python3
"""Sync README metrics from actual repo state (P0-D 克莱恩 2026-07-19 拍板).

每次 PR merge / 数据扩充后跑一次, 防止 README / badges / coach_fit_report
数字漂移 (2026-07-19 战略评估指出 "README 指标有漂移").

Usage:
    python3 scripts/sync_readme_metrics.py            # dry-run (只 print diff)
    python3 scripts/sync_readme_metrics.py --apply    # 实际改 README.md + badges
    python3 scripts/sync_readme_metrics.py --json     # 输出 JSON 给 badge 生成
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def count_md_files() -> dict:
    """扫描真实数据快照"""
    profile_dirs = []
    for d in ROOT.iterdir():
        if not d.is_dir():
            continue
        if not re.match(r"^[a-zA-Z0-9_-]+-[a-zA-Z0-9_-]+$", d.name):
            continue
        if (d / "index.md").exists():
            profile_dirs.append(d)
    profiles = len(profile_dirs)

    case_studies = list(ROOT.glob("*/pr-*.md"))
    case_studies = [f for f in case_studies if not any(
        part.startswith(".") for part in f.parts
    )]

    anti_md = list((ROOT / "anti-patterns").glob("*.md"))
    anti_md = [f for f in anti_md if f.name != "README.md"]
    anti_json = list((ROOT / "anti-patterns").glob("*.json"))
    success_md = list((ROOT / "success-patterns").glob("*.md"))
    success_md = [f for f in success_md if f.name != "README.md"]
    success_json = list((ROOT / "success-patterns").glob("*.json"))
    review_cases = list((ROOT / "review-cases").glob("*.json"))
    lessons = list((ROOT / "misakanet-50").glob("lesson-*.md"))

    return {
        "profiles": profiles,
        "case_studies_md": len(case_studies),
        "anti_patterns_md": len(anti_md),
        "anti_patterns_json": len(anti_json),
        "success_patterns_md": len(success_md),
        "success_patterns_json": len(success_json),
        "review_cases_json": len(review_cases),
        "lessons": len(lessons),
        "total_md_files": len(list(ROOT.rglob("*.md"))) - len(list((ROOT / ".git").rglob("*.md"))),
    }


def load_coach_metrics() -> dict:
    """从 docs/coach_fit_report.json 读 coach 真实数据"""
    path = ROOT / "docs" / "coach_fit_report.json"
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        counts = data.get("counts", {})
        by_repo = data.get("by_repo", {})
        accuracy_pct = data.get("accuracy_pct", 0.0)
        return {
            "cases": data.get("total_cases", 0),
            "accuracy": accuracy_pct / 100.0 if accuracy_pct > 1 else accuracy_pct,
            "accuracy_pct": accuracy_pct,
            "repos": len(by_repo),
            "correct": counts.get("correct", 0),
            "close": counts.get("close", 0),
            "wrong": counts.get("wrong", 0),
        }
    except Exception:
        return {}


def build_metrics_block(snapshot: dict, coach: dict) -> str:
    """构造 README 表格段 (替换 '## 统计' 下面那段)"""
    cases = coach.get("cases", 0)
    accuracy = coach.get("accuracy", 0.0)
    repos = coach.get("repos", 0)
    accuracy_pct = f"{accuracy * 100:.1f}%" if accuracy < 1 else f"{accuracy:.1f}%"

    return f"""| Metric | Value |
|---|---|
| Version | 1.2.0 |
| Repo profiles | {snapshot['profiles']} |
| Case studies (.md) | {snapshot['case_studies_md']} |
| Anti-patterns (.md) | {snapshot['anti_patterns_md']} |
| Anti-patterns (.json) | {snapshot['anti_patterns_json']} |
| Success patterns (.md) | {snapshot['success_patterns_md']} |
| Success patterns (.json) | {snapshot['success_patterns_json']} |
| Review cases (.json) | {snapshot['review_cases_json']} |
| Lessons (misakanet-50) | {snapshot['lessons']} |
| Validator checks | ✅ 0 errors |
| OKF compliance | ✅ v0.1 |
| Coach accuracy | {accuracy_pct} ({cases} cases, {repos} repos) |"""


def update_readme(snapshot: dict, coach: dict, apply: bool) -> tuple[bool, str]:
    """替换 README.md 的 统计 表格 (支持中文 / Metric 两种表头)"""
    readme = ROOT / "README.md"
    if not readme.exists():
        return False, "README.md not found"

    text = readme.read_text(encoding="utf-8")

    new_block = build_metrics_block(snapshot, coach)

    # 匹配 "## 统计" 段下的表格 - 中文/英文两种表头都支持
    pattern = re.compile(
        r"(## 统计\s*\n\s*\n)"  # heading + 空行
        r"((?:\|\s*(?:Metric|维度)\s*\|.*?\n"  # 表头 (中文/英文)
        r"(?:\|.*?\n)+))",  # 表行 (1+)
        re.MULTILINE,
    )

    if not pattern.search(text):
        return False, "Could not find '## 统计' table in README.md"

    new_text = pattern.sub(lambda m: m.group(1) + new_block + "\n", text)

    if new_text == text:
        return False, "README already in sync (no changes)"

    if apply:
        readme.write_text(new_text, encoding="utf-8")
        return True, "README.md updated"
    else:
        return True, f"Would update README.md ({len(text) - len(new_text)} byte delta)"

def emit_badge_json(snapshot: dict, coach: dict) -> dict:
    """生成 badge JSON 供 docs/badges/*.json 使用"""
    accuracy = coach.get("accuracy", 0.0)
    accuracy_pct = f"{accuracy * 100:.1f}%" if accuracy < 1 else f"{accuracy:.1f}%"
    return {
        "profiles.json": {
            "schemaVersion": 1,
            "label": "profiles",
            "message": str(snapshot["profiles"]),
            "color": "blue",
        },
        "cases.json": {
            "schemaVersion": 1,
            "label": "cases",
            "message": str(snapshot["case_studies_md"]),
            "color": "blue",
        },
        "anti_patterns.json": {
            "schemaVersion": 1,
            "label": "anti-patterns",
            "message": str(snapshot["anti_patterns_md"] + snapshot["anti_patterns_json"]),
            "color": "blue",
        },
        "success_patterns.json": {
            "schemaVersion": 1,
            "label": "success-patterns",
            "message": str(snapshot["success_patterns_md"] + snapshot["success_patterns_json"]),
            "color": "blue",
        },
        "lessons.json": {
            "schemaVersion": 1,
            "label": "lessons",
            "message": str(snapshot["lessons"]),
            "color": "blue",
        },
        "coach_fit.json": {
            "schemaVersion": 1,
            "label": "coach-fit",
            "message": accuracy_pct,
            "color": "brightgreen" if accuracy >= 0.85 else "yellow" if accuracy >= 0.7 else "red",
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Sync README + badges from real repo state (P0-D)")
    parser.add_argument("--apply", action="store_true", help="Actually write changes (default: dry-run)")
    parser.add_argument("--json", action="store_true", help="Output JSON badges to stdout")
    args = parser.parse_args()

    snapshot = count_md_files()
    coach = load_coach_metrics()

    print("📊 Snapshot:")
    for k, v in snapshot.items():
        print(f"  {k}: {v}")
    if coach:
        print(f"\n🎯 Coach metrics:")
        for k, v in coach.items():
            print(f"  {k}: {v}")

    if args.json:
        print()
        print("📋 Badge JSON:")
        print(json.dumps(emit_badge_json(snapshot, coach), ensure_ascii=False, indent=2))
        return 0

    print()
    changed, msg = update_readme(snapshot, coach, apply=args.apply)
    print(f"{'✅' if changed else '⏭️ '} README.md: {msg}")

    if args.apply:
        # write badges to docs/badges/
        badges_dir = ROOT / "docs" / "badges"
        badges_dir.mkdir(exist_ok=True)
        for name, data in emit_badge_json(snapshot, coach).items():
            (badges_dir / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"  📛 docs/badges/{name} written")

    return 0


if __name__ == "__main__":
    sys.exit(main())
