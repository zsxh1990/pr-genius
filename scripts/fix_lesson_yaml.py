#!/usr/bin/env python3
"""
One-shot fix for misakanet-50/lesson-*.md frontmatter.

Bug: each file has a stray JSON line embedded inside YAML frontmatter:
---
domain: "..."
title: "..."
verification: "..."
{"title": "...", "domain": "...", ...}   <- WRONG: stray JSON line
---
(content here)

Fix: delete the stray JSON line, keep proper YAML structure.
"""
import re
import sys
from pathlib import Path

LESSON_DIR = Path(__file__).resolve().parent.parent / "misakanet-50"

def fix_lesson(path: Path) -> bool:
    """Return True if file was modified."""
    text = path.read_text(encoding='utf-8')

    # Match frontmatter
    m = re.match(r'^(---)\n(.*?)\n(---)\n(.*)$', text, re.DOTALL)
    if not m:
        print(f"  {path.name}: no frontmatter found, skipping")
        return False

    fm = m.group(2)

    # Find stray JSON line (starts with `{` on its own line)
    stray_json_match = re.search(r'^\{.*\}\s*$', fm, re.MULTILINE)
    if not stray_json_match:
        print(f"  {path.name}: no stray JSON line found, already fixed?")
        return False

    # Strip the stray JSON line
    fm_fixed = re.sub(r'^\{.*\}\s*\n', '', fm, flags=re.MULTILINE).rstrip()

    new_text = f"---\n{fm_fixed}\n---\n{m.group(4)}"
    path.write_text(new_text, encoding='utf-8')
    print(f"  {path.name}: FIXED")
    return True


def main():
    lessons = sorted(LESSON_DIR.glob("lesson-*.md"))
    print(f"Found {len(lessons)} lesson files in {LESSON_DIR}")
    fixed = 0
    for lesson in lessons:
        if fix_lesson(lesson):
            fixed += 1
    print(f"\nFixed {fixed}/{len(lessons)} files")
    if fixed > 0:
        print("Run `python3 validate.py` to verify.")


if __name__ == "__main__":
    main()