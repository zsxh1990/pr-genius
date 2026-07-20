#!/usr/bin/env python3
"""Auto-generate anti-patterns/README.md index from frontmatter.

Scans anti-patterns/*.md, extracts key/symptom/trigger_keywords,
generates a markdown table grouped by category.

Usage:
    python3 scripts/generate_ap_readme.py
    python3 scripts/generate_ap_readme.py --dry-run
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def _parse_frontmatter(text: str) -> dict:
    """Parse YAML frontmatter from markdown text."""
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    yaml_text = text[4:end]
    result = {}
    current_key = None
    current_list = None
    for line in yaml_text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("- ") and current_key:
            if current_list is None:
                current_list = []
            current_list.append(line[2:].strip('"').strip("'"))
            continue
        if current_list is not None:
            result[current_key] = current_list
            current_list = None
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if val:
                result[key] = val
                current_key = None
            else:
                current_key = key
                current_list = None
    if current_list is not None and current_key:
        result[current_key] = current_list
    return result


def _categorize(key: str) -> str:
    """Categorize anti-pattern by key prefix."""
    if key.startswith("contribai-"):
        return "ContribAI"
    elif key.startswith("openclaw-"):
        return "OpenClaw"
    elif key.startswith("nousresearch-"):
        return "NousResearch"
    elif key.startswith("uv-"):
        return "uv"
    elif key.startswith("vite-"):
        return "Vite"
    else:
        return "General"


def main():
    dry_run = "--dry-run" in sys.argv
    ap_dir = REPO / "anti-patterns"

    entries = []
    for f in sorted(ap_dir.glob("*.md")):
        if f.name == "README.md":
            continue
        text = f.read_text(encoding="utf-8")
        fm = _parse_frontmatter(text)
        if not fm:
            continue
        key = fm.get("key", f.stem)
        symptom = fm.get("symptom", "").strip()
        if isinstance(symptom, list):
            symptom = " ".join(symptom)
        # Truncate symptom to first line
        symptom = symptom.split("\n")[0][:120]
        trigger = fm.get("trigger_keywords", [])
        if isinstance(trigger, str):
            trigger = [trigger]
        category = _categorize(key)
        entries.append({
            "key": key,
            "file": f.name,
            "symptom": symptom,
            "trigger": trigger[:3],
            "category": category,
        })

    # Group by category
    categories = {}
    for e in entries:
        categories.setdefault(e["category"], []).append(e)

    # Generate README
    lines = [
        "---",
        "type: Anti-Pattern Bundle",
        "title: Anti-Patterns 索引",
        "description: PR 提交流程中的反模式（可检索的失败信号）",
        "version: 0.2.0",
        "created: 2026-07-02",
        "updated: 2026-07-19",
        "auto_generated: true",
        "---",
        "",
        "# Anti-Patterns 反模式库",
        "",
        f"> **{len(entries)} 条反模式**，自动从 frontmatter 生成。",
        "> 当 Agent 遇到 PR 失败信号时，拿报错 / 拒绝语关键词去匹配本库，实现秒级自愈。",
        "",
    ]

    for cat in sorted(categories.keys()):
        cat_entries = categories[cat]
        lines.append(f"## {cat} ({len(cat_entries)})")
        lines.append("")
        lines.append("| Key | Symptom | Keywords |")
        lines.append("|-----|---------|----------|")
        for e in sorted(cat_entries, key=lambda x: x["key"]):
            kw = ", ".join(f"`{k}`" for k in e["trigger"][:3])
            symptom_short = e["symptom"][:80] + ("..." if len(e["symptom"]) > 80 else "")
            lines.append(f"| [{e['key']}]({e['file']}) | {symptom_short} | {kw} |")
        lines.append("")

    content = "\n".join(lines) + "\n"

    if dry_run:
        print(content)
    else:
        readme_path = ap_dir / "README.md"
        readme_path.write_text(content, encoding="utf-8")
        print(f"✅ Generated {readme_path.relative_to(REPO)} ({len(entries)} entries)")


if __name__ == "__main__":
    main()
