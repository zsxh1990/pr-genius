#!/usr/bin/env python3
"""Auto-inject `links:` field into every case study based on body text.

克莱恩 2026-07-19 战略评估 Month 2 P0 #4:
'case study ↔ anti-pattern 反向链 — 给 case study frontmatter 加 links:
字段指向相关 anti-pattern'

策略:
- 扫所有 anti-patterns/*.md frontmatter key
- 扫所有 <org>-<repo>/pr-*.md body 文本
- 如果 case body 含 anti-pattern key, 在 frontmatter 加 links: 字段
  (target: anti-patterns/<key>.md, type: anti-pattern)
- 不重复添加已有 links
- 保留原 frontmatter 其他字段

Run:
    python3 scripts/inject_anti_pattern_links.py           # dry-run, print changes
    python3 scripts/inject_anti_pattern_links.py --apply   # 实际写文件
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))


def parse_frontmatter(text: str):
    """Parse YAML frontmatter from markdown text using PyYAML safe_load.

    Returns (fm_dict_or_None, body_after_frontmatter).
    """
    if not text.startswith("---\n"):
        return None, text
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not m:
        return None, text
    fm_text = m.group(1)
    body = m.group(2)
    try:
        import yaml
        return yaml.safe_load(fm_text), body
    except Exception:
        return None, body


def serialize_frontmatter(fm: dict) -> str:
    """Serialize dict back to YAML frontmatter using PyYAML safe_dump.

    修复历史 bug: 自写的 naive parser/dumper 吞掉了嵌套结构 (rounds/delta/
    close_decision/agent_guidelines_applied) — 导致 inject 脚本 一次 --
    apply 损坏 7 个 case study 的 rounds / close_decision 字段. 现在用
    PyYAML 标准库, 保证 round-trip 100% 保真.
    """
    import yaml
    if fm is None:
        return "---\n---\n"
    dumped = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True,
                           default_flow_style=False, width=1000)
    return f"---\n{dumped}---\n"


def main():
    parser = argparse.ArgumentParser(
        description="Auto-inject links: field into case study frontmatter (Month 2 P0 #4)"
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="实际写文件 (default: dry-run 只 print changes)"
    )
    args = parser.parse_args()

    # 1. 收集所有 anti-pattern keys
    ap_dir = REPO / "anti-patterns"
    if not ap_dir.exists():
        print(f"❌ anti-patterns/ 不存在")
        return 1

    ap_keys: set[str] = set()
    for f in ap_dir.glob("*.md"):
        if f.name == "README.md":
            continue
        fm, _ = parse_frontmatter(f.read_text(encoding="utf-8"))
        if fm and fm.get("key"):
            ap_keys.add(fm["key"])
    print(f"📊 收集到 {len(ap_keys)} 个 anti-pattern keys")

    # 2. 扫所有 case study
    case_files = []
    for d in REPO.iterdir():
        if not d.is_dir():
            continue
        if not re.match(r"^[a-zA-Z0-9_-]+-[a-zA-Z0-9_-]+$", d.name):
            continue
        if d.name.startswith("."):
            continue
        for f in d.glob("pr-*.md"):
            case_files.append(f)

    print(f"📊 扫到 {len(case_files)} 个 case study")
    print()

    total_added = 0
    cases_modified = 0
    for cf in case_files:
        text = cf.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)
        if fm is None:
            continue
        # Skip legacy v0.1 schema (no links 概念)
        sv = fm.get("schema_version", "")
        if not sv.startswith("rounds-v"):
            continue
        # Parse existing links
        existing_links = fm.get("links", [])
        if isinstance(existing_links, str):
            existing_links = [existing_links]
        existing_targets = set()
        for link in existing_links:
            if isinstance(link, dict):
                existing_targets.add(link.get("target", ""))
            elif isinstance(link, str):
                existing_targets.add(link)
        # Find anti-pattern keys in body
        body_lower = body.lower()
        new_links = []
        for key in sorted(ap_keys):
            target = f"anti-patterns/{key}.md"
            if target in existing_targets:
                continue
            if key.lower() in body_lower:
                new_links.append({
                    "target": target,
                    "type": "anti-pattern",
                })
        if not new_links:
            continue
        # Append to existing links
        if existing_links:
            for link in existing_links:
                if isinstance(link, str):
                    new_links.insert(0, link)
                else:
                    new_links.insert(0, link)
        # Re-serialize
        fm["links"] = new_links
        new_text = serialize_frontmatter(fm) + body
        if args.apply:
            cf.write_text(new_text, encoding="utf-8")
            cases_modified += 1
            total_added += len(new_links) - len(existing_links)
        else:
            cases_modified += 1
            total_added += len(new_links) - len(existing_links)
            print(f"  would add {len(new_links) - len(existing_links)} link(s) to {cf.relative_to(REPO)}")

    action = "✅ modified" if args.apply else "🔍 dry-run (would modify)"
    print()
    print(f"{action} {cases_modified} case studies, added {total_added} reverse links")
    print()
    print("Re-run validate.py to see orphan anti-pattern count drop.")


if __name__ == "__main__":
    main()
