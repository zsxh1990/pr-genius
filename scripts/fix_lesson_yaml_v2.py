#!/usr/bin/env python3
"""
Fix misakanet-50/lesson-*.md frontmatter — improved regex for empty/short JSON lines.

Bug pattern: frontmatter contains a stray JSON object line + extra closing ---
The previous regex `^\{.*\}$` required non-empty content. Some JSON lines
end with `""` so the regex *did* match them — but a new bug pattern has
emerged where the JSON line is missing some fields and has a closing
`---` immediately after. This version handles:
  - multi-line JSON objects (rare)
  - trailing blank lines before closing ---
"""
import re
from pathlib import Path

LESSON_DIR = Path(__file__).resolve().parent.parent / "misakanet-50"


def fix_lesson(path: Path) -> bool:
    text = path.read_text(encoding='utf-8')

    # Match frontmatter (first --- block)
    m = re.match(r'^(---)\n(.*?)\n(---)\n(.*)$', text, re.DOTALL)
    if not m:
        return False

    fm = m.group(2)

    # Look for any JSON-like line in frontmatter
    stray_json_match = re.search(r'^\s*\{[^}]*\}\s*$', fm, re.MULTILINE)
    if not stray_json_match:
        # Try multiline JSON (rare but possible)
        stray_json_match = re.search(r'^\s*\{[\s\S]*?\}\s*$', fm, re.MULTILINE)

    if not stray_json_match:
        return False

    # Strip the stray JSON line and any blank lines after it
    fm_fixed = re.sub(r'^\s*\{[\s\S]*?\}\s*\n', '', fm, flags=re.MULTILINE).rstrip()

    new_text = f"---\n{fm_fixed}\n---\n{m.group(4)}"
    path.write_text(new_text, encoding='utf-8')
    print(f"  FIXED: {path.name}")
    return True


def main():
    lessons = sorted(LESSON_DIR.glob("lesson-*.md"))
    print(f"Found {len(lessons)} lesson files in {LESSON_DIR}")
    fixed = 0
    for lesson in lessons:
        if fix_lesson(lesson):
            fixed += 1
    print(f"\nFixed {fixed}/{len(lessons)} files")


if __name__ == "__main__":
    main()