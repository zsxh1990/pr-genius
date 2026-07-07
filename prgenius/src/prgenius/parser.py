"""Markdown frontmatter parsing — pure-stdlib YAML-subset.

Goals:
- Zero hard deps (no PyYAML) — package works after `pip install prgenius-core`
- Just enough fidelity for OKF v0.1 / rounds v0.5.0 / v0.7.0 frontmatter
- Honest: returns the AST we can parse; preserves raw text for the rest

Strategy: 2-pass indent-stack parser.
- Pass 1: collect (line, indent, raw_line)
- Pass 2: walk lines; push/pop stack based on indent depth

Limitations:
- top-level key: value (string/int/bool/null/list-inline)
- 2-space indent for nested mapping
- `- item` lists (with optional inline key: value on first line)
"""
from __future__ import annotations
import re
from pathlib import Path
from typing import Iterator


_FM_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


def load(path: str | Path) -> dict:
    """Load a markdown file: return {frontmatter, body, path}."""
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    fm_match = _FM_RE.match(text)
    if not fm_match:
        return {"frontmatter": {}, "body": text, "path": str(p)}
    fm_text = fm_match.group(1)
    body = text[fm_match.end():].lstrip("\n")
    return {
        "frontmatter": parse_frontmatter(fm_text),
        "body": body,
        "path": str(p),
    }


def _unquote(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'"):
        return s[1:-1]
    return s


def _coerce(v: str):
    """Coerce a scalar string to a Python value."""
    if v == "" or v in ("null", "~"):
        return None
    if v == "true":
        return True
    if v == "false":
        return False
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        if not inner:
            return []
        return [_coerce(x.strip()) for x in inner.split(",")]
    if re.match(r"^-?\d+$", v):
        return int(v)
    if re.match(r"^-?\d+\.\d+$", v):
        return float(v)
    if len(v) >= 2 and v[0] == v[-1] and v[0] in ('"', "'"):
        return v[1:-1]
    return v


def _last_list_key(d: dict):
    for k in reversed(d.keys()):
        if isinstance(d[k], list):
            return k
    return None


def _normalize_lists(node):
    """Recursively replace `{'_': [items]}` or `{'_items': [items]}` (parser quirk)
    with the bare list.
    """
    if isinstance(node, dict):
        keys = list(node.keys())
        if (
            len(keys) == 1
            and keys[0] in ("_", "_items")
            and isinstance(node[keys[0]], list)
        ):
            return [_normalize_lists(x) for x in node[keys[0]]]
        return {k: _normalize_lists(v) for k, v in node.items()}
    if isinstance(node, list):
        return [_normalize_lists(x) for x in node]
    return node


def parse_frontmatter(text: str) -> dict:
    """Parse a YAML-subset frontmatter block.

    Strategy: walk lines, push/pop an indent-aware stack. Lists get attached
    to the most recent dict-key (the "current list"). After the walk we
    normalize any `{'_': [...]}` quirk wrappers to plain lists.
    """
    tokens = []
    for raw in text.splitlines():
        if not raw.strip():
            continue
        if raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        tokens.append((indent, raw.strip()))

    root: dict = {}
    # stack of (indent_level, container); root container indent = -1
    stack = [(-1, root)]

    for indent, line in tokens:
        # pop until stack top has smaller indent than current
        while len(stack) > 1 and stack[-1][0] >= indent:
            stack.pop()
        parent_indent, parent = stack[-1]

        if line.startswith("- "):
            content = line[2:].strip()
            if not isinstance(parent, dict):
                # shouldn't happen in our schema
                continue
            last_key = _last_list_key(parent)
            if last_key is None:
                parent["_items"] = []
                current_list = parent["_items"]
                last_key = "_items"
            else:
                current_list = parent[last_key]

            if ":" in content and not content.startswith(('"', "'")):
                k, _, v = content.partition(":")
                k = _unquote(k.strip())
                v = v.strip()
                item: dict = {k: _coerce(v)}
                current_list.append(item)
                stack.append((indent, item))
            else:
                current_list.append(_coerce(content))
            continue

        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        k = _unquote(k.strip())
        v = v.strip()

        if not isinstance(parent, dict):
            continue

        if v == "":
            new = {}
            parent[k] = new
            stack.append((indent, new))
        else:
            parent[k] = _coerce(v)

    return _normalize_lists(root)


# ---------- higher-level iterators ----------

def iter_profiles(repo_root: str | Path) -> Iterator[dict]:
    """Yield each Repo Profile dict under `<repo_root>/<folder>/index.md`."""
    root = Path(repo_root)
    skip = {
        "anti-patterns", "misakanet-50", ".github", "docs",
        "scripts", "prgenius", "__pycache__", ".git",
        "federation.yaml",
    }
    for sub in sorted(root.iterdir()):
        if not sub.is_dir() or sub.name in skip or sub.name.startswith("."):
            continue
        idx = sub / "index.md"
        if not idx.exists():
            continue
        loaded = load(idx)
        if loaded["frontmatter"].get("type") == "Repo Profile":
            loaded["folder"] = sub.name
            yield loaded


def iter_case_studies(repo_root: str | Path) -> Iterator[dict]:
    """Yield each PR Case Study dict under repo root."""
    root = Path(repo_root)
    for path in sorted(root.rglob("pr-*.md")):
        try:
            loaded = load(path)
        except Exception:
            continue
        if loaded["frontmatter"].get("type") == "PR Case Study":
            loaded["folder"] = path.parent.name
            loaded["pr_file"] = path.name
            yield loaded


def profile_get(repo_root: str | Path, repo: str) -> dict | None:
    """Look up a Repo Profile by `org/name`. None if missing."""
    target = repo.strip("/").lower()
    target_folder = target.replace("/", "-")
    for profile in iter_profiles(repo_root):
        if profile["folder"].lower() == target_folder:
            return profile
        if profile["frontmatter"].get("repo", "").strip("/").lower() == target:
            return profile
    return None


def schema_info() -> dict:
    return {
        "schema_versions": ["rounds v0.5.0", "rounds v0.7.0 (BC over v0.5.0)"],
        "delta_kinds": ["code_change", "no_code_change", "unknown"],
        "close_decision_status": ["pending", "close", "keep_open", "merged", "superseded"],
        "evidence_fields_round_level": ["verified_at", "evidence_urls", "confidence"],
        "evidence_fields_case_level": ["verified_at", "evidence_urls", "confidence"],
        "confidence_values": ["high", "medium", "low"],
        "action_enum": [
            "open", "amend", "bot_review", "human_review",
            "check_in", "bump", "close", "merge", "decision",
        ],
    }
