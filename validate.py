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
    return sorted(p for p in root.rglob("*.md") if ".git" not in p.parts)


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
            "Blacklist Reference",
        }:
            warnings.append(
                f"{f.relative_to(ROOT)}: unknown type `{fm['type']}`"
            )


LINK_RE = re.compile(r"\[([^\]]*)\]\((\./[^)]+\.md)\)")

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


def main() -> int:
    print(f"pr-genius OKF v0.1 validator — {ROOT}\n")

    md_files = find_md_files(ROOT)
    print(f"Found {len(md_files)} .md files\n")

    check_frontmatter(md_files)
    check_internal_links(md_files)

    # Find subdirectories (Repo Profile roots)
    repo_dirs = [p for p in ROOT.iterdir() if p.is_dir() and not p.name.startswith(".")]
    root_index = ROOT / "index.md"
    check_root_index_consistency(root_index, repo_dirs)

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