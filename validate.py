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

from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    # issue #65: PyYAML 可选。缺失时不再 exit 2, 而是走 stdlib 降级解析器
    # (_yaml_lite_load), 让 validate.py 在干净机器上也能跑出结果。
    yaml = None


ROOT = Path(__file__).parent.resolve()
errors: list[str] = []
warnings: list[str] = []


# ---- PyYAML 不可用时的 stdlib 降级解析器 (issue #65) --------------------
# 只覆盖 OKF frontmatter 实际用到的 YAML 子集: 标量 / 引号串 / flow 序列与
# 映射 / 块序列 / 嵌套映射 / 块标量 / 行内注释。无法忠实解析的结构抛
# ValueError — 由 parse_frontmatter 转成 {"_error": ...} 走正常报错路径,
# 不猜结果也不假装成功 (lesson: frontmatter-parsing-edge-cases)。


class _YamlLiteError(ValueError):
    """降级解析器无法忠实解析该 YAML 子集。"""


def _strip_yaml_comment(line: str) -> str:
    """去掉行内注释: 引号外、行首或空白后的 `#` 起注释。

    整行 split('#') 会把 "0.15  # 说明" 截成 "0.15", 也会把
    source_pr: "x#123" 截错 — 所以必须跳过引号内的 #。
    """
    in_s = in_d = False
    i = 0
    while i < len(line):
        ch = line[i]
        if in_s:
            if ch == "'":
                if i + 1 < len(line) and line[i + 1] == "'":
                    i += 2
                    continue  # '' 是单引号串里的转义引号
                in_s = False
        elif in_d:
            if ch == "\\" and i + 1 < len(line):
                i += 2
                continue
            if ch == '"':
                in_d = False
        else:
            if ch == "'":
                in_s = True
            elif ch == '"':
                in_d = True
            elif ch == "#" and (i == 0 or line[i - 1] in " \t"):
                return line[:i].rstrip()
        i += 1
    return line


_TS_RE = re.compile(
    r"^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})"
    r"(?:(?:[Tt]|[ \t]+)(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})"
    r"(?P<fraction>\.\d*)?(?:[ \t]*(?P<tz>Z|[-+]\d{2}(?::?\d{2})?))?)?$"
)
_BLOCK_SCALAR_RE = re.compile(r"^[|>][+-]?\d*$")


def _parse_scalar_lite(s: str):
    """标量解析: 对齐 PyYAML 的 bool/int/float/null/timestamp 解析。"""
    s = s.strip()
    if s == "" or s in ("~", "null", "Null", "NULL"):
        return None
    # PyYAML 走 YAML 1.1: yes/no/on/off 也是 bool
    if s in ("true", "True", "TRUE", "yes", "Yes", "YES", "on", "On", "ON"):
        return True
    if s in ("false", "False", "FALSE", "no", "No", "NO", "off", "Off", "OFF"):
        return False
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "'\"":
        return _unquote_lite(s)
    if s.startswith("["):
        return _parse_flow_seq(s)
    if s.startswith("{"):
        return _parse_flow_map(s)
    if s.startswith(("|", ">")):
        # 块标量指示符必须在映射值分支消费; 走到这里 = 结构不对
        raise _YamlLiteError(f"unexpected block-scalar indicator: {s[:20]!r}")
    if s[0] in "'\"" and not (len(s) >= 2 and s[0] == s[-1]):
        # 引号未闭合 = 多行引号串, 本子集不支持 (报错, 不猜)
        raise _YamlLiteError(f"unterminated quoted scalar: {s[:30]!r}")
    m = _TS_RE.match(s)
    if m:
        # 与 PyYAML 一致: 纯日期 → date, 带时间 → datetime
        # (verified_at 的 isinstance(str) 判定两边才一致)
        if m.group("hour") is None:
            return dt.date(int(m.group("year")), int(m.group("month")), int(m.group("day")))
        frac = m.group("fraction") or ""
        micro = int((frac[1:] + "000000")[:6]) if frac else 0
        base = dt.datetime(
            int(m.group("year")), int(m.group("month")), int(m.group("day")),
            int(m.group("hour")), int(m.group("minute")), int(m.group("second")), micro,
        )
        tz = m.group("tz")
        if tz == "Z":
            return base.replace(tzinfo=dt.timezone.utc)
        if tz:
            sign = 1 if tz[0] == "+" else -1
            tz = tz[1:].replace(":", "")
            delta = dt.timedelta(hours=int(tz[:2]), minutes=int(tz[2:] or 0))
            return base.replace(tzinfo=dt.timezone(sign * delta))
        return base
    if re.fullmatch(r"[-+]?\d+", s):
        return int(s)
    if s in (".inf", ".Inf", ".INF"):
        return float("inf")
    if s in ("-.inf", "-.Inf", "-.INF"):
        return float("-inf")
    if re.fullmatch(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?", s):
        return float(s)
    return s


def _unquote_lite(s: str) -> str:
    quote = s[0]
    inner = s[1:-1]
    if quote == "'":
        return inner.replace("''", "'")
    # 双引号: 走 JSON 转义规则 (与 YAML double-quoted 基本一致)
    try:
        return json.loads(s)
    except ValueError:
        return inner.replace('\\"', '"').replace("\\\\", "\\")


def _split_flow_items(s: str) -> list[str]:
    """按顶层逗号切 flow 集合元素 (跳过引号/嵌套括号)。空元素保留 = null。"""
    items, depth, in_s, in_d, start = [], 0, False, False, 0
    for i, ch in enumerate(s):
        if in_s:
            if ch == "'":
                in_s = False
        elif in_d:
            if ch == "\\":
                continue
            if ch == '"':
                in_d = False
        elif ch == "'":
            in_s = True
        elif ch == '"':
            in_d = True
        elif ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
        elif ch == "," and depth == 0:
            items.append(s[start:i].strip())
            start = i + 1
    items.append(s[start:].strip())
    return items


def _parse_flow_seq(s: str) -> list:
    if not s.endswith("]"):
        raise _YamlLiteError(f"unterminated flow sequence: {s[:40]!r}")
    inner = s[1:-1].strip()
    if not inner:
        return []
    return [_parse_scalar_lite(it) for it in _split_flow_items(inner)]


def _parse_flow_map(s: str) -> dict:
    if not s.endswith("}"):
        raise _YamlLiteError(f"unterminated flow mapping: {s[:40]!r}")
    inner = s[1:-1].strip()
    if not inner:
        return {}
    result = {}
    for it in _split_flow_items(inner):
        key, sep, val = it.partition(":")
        if not sep:
            raise _YamlLiteError(f"flow mapping entry missing ':': {it!r}")
        result[_parse_scalar_lite(key)] = _parse_scalar_lite(val)
    return result


def _indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _split_key(content: str, lineno: int) -> tuple[str, str]:
    """拆 `key: rest`; key 可为引号串。返回 (key, rest)。"""
    if content.startswith(("'", '"')):
        quote = content[0]
        i = 1
        while i < len(content):
            if content[i] == quote:
                if quote == "'" and i + 1 < len(content) and content[i + 1] == "'":
                    i += 2
                    continue
                break
            if quote == '"' and content[i] == "\\":
                i += 2
                continue
            i += 1
        else:
            raise _YamlLiteError(f"line {lineno}: unterminated quoted key")
        if i + 1 >= len(content) or content[i + 1] != ":":
            raise _YamlLiteError(f"line {lineno}: expected ':' after key {content[:20]!r}")
        key = _unquote_lite(content[: i + 1])
        rest = content[i + 2 :]
    else:
        # plain key: 第一个冒号后必须是空白或行尾 (否则是 "https://..." 这类值)
        m = re.match(r"^([^:#\s][^:]*?)\s*:(\s+|$)", content)
        if not m:
            raise _YamlLiteError(f"line {lineno}: not a mapping entry: {content[:40]!r}")
        key = m.group(1).strip()
        rest = content[m.end(1) + 1 :]  # 跳过冒号
    if key == "":
        raise _YamlLiteError(f"line {lineno}: empty key")
    return key, rest.strip()


def _is_key_line(content: str) -> bool:
    """判断一行是否形如 `key: ...` / `key:` (供序列项 `- key: val` 判定)。"""
    try:
        _split_key(content, 0)
        return True
    except _YamlLiteError:
        return False


def _parse_block_scalar(
    lines: list[str], i: int, indicator: str, key_indent: int
) -> tuple[str, int]:
    """解析 `|`/`>` 块标量, 返回 (value, next_i)。i 指向 header 的下一行。"""
    style = indicator[0]
    chomp = ""
    for ch in indicator[1:]:
        if ch in "+-":
            chomp = ch
        # 其余是显式缩进数字, 这里按首行缩进推断, 不用它
    block: list[str] = []
    j = i
    content_indent = None
    while j < len(lines):
        raw = lines[j]
        if raw.strip() == "":
            block.append("")
            j += 1
            continue
        ind = _indent_of(raw)
        if ind <= key_indent:
            break
        if content_indent is None:
            content_indent = ind
        block.append(raw[content_indent:] if len(raw) > content_indent else "")
        j += 1
    while block and block[-1] == "":
        block.pop()
    if style == ">":
        # folded: 非缩进行折成空格 (frontmatter 少用, 能解析就别报错)
        folded: list[str] = []
        for ln in block:
            if folded and ln and not ln[0].isspace() and folded[-1]:
                folded[-1] += " " + ln
            else:
                folded.append(ln)
        value = "\n".join(folded)
    else:
        value = "\n".join(block)
    if chomp == "-":
        return value, j
    if chomp == "+":
        return value + "\n", j
    return value + ("\n" if value else ""), j


def _next_content(lines: list[str], i: int) -> int:
    """跳过空行/纯注释行, 返回下一个内容行下标。"""
    while i < len(lines):
        stripped = _strip_yaml_comment(lines[i]).strip()
        if stripped:
            return i
        i += 1
    return i


def _fold_plain_continuation(lines: list[str], i: int, parent_indent: int, value):
    """收集多行 plain 标量的续行并按 YAML fold 语义折回 (issue #65)。

    PyYAML 对 `key: long text` 后面更深缩进的续行按空格折行、空行变 \\n。
    续行若长得像 key 或序列项就停下 — 那不是标量的一部分。
    """
    if not isinstance(value, str) or value == "":
        return value, i
    parts = [value]
    while i < len(lines):
        stripped = _strip_yaml_comment(lines[i]).rstrip()
        if not stripped.strip():
            # 空行只有在后面还有续行时才属于标量
            j = i
            while j < len(lines) and not _strip_yaml_comment(lines[j]).strip():
                j += 1
            if j >= len(lines):
                break
            nxt = _strip_yaml_comment(lines[j]).rstrip()
            n_content = nxt.strip()
            if (
                _indent_of(nxt) <= parent_indent
                or n_content == "-"
                or n_content.startswith("- ")
                or _is_key_line(n_content)
            ):
                break
            parts.append("")
            i += 1
            continue
        ind = _indent_of(stripped)
        if ind <= parent_indent:
            break
        content = stripped.strip()
        if content == "-" or content.startswith("- ") or _is_key_line(content):
            break
        parts.append(content)
        i += 1
    if len(parts) == 1:
        return value, i
    out = parts[0]
    prev_blank = False
    for p in parts[1:]:
        if p == "":
            out += "\n"
            prev_blank = True
        elif prev_blank:
            out += p
            prev_blank = False
        else:
            out += " " + p
    return out, i


def _parse_value_block(lines: list[str], i: int, key_indent: int):
    """解析 `key:` 空值后的嵌套块。

    嵌套映射要比 key 缩进更深; 序列可以与 key 同缩进 (indentless
    sequence — 本仓 evidence_urls/tags 就是这种写法)。
    """
    j = _next_content(lines, i)
    if j >= len(lines):
        return None, i
    stripped = _strip_yaml_comment(lines[j]).rstrip()
    ind = _indent_of(stripped)
    content = stripped.strip()
    if ind > key_indent:
        return _parse_block(lines, j, key_indent + 1)
    if ind == key_indent and (content == "-" or content.startswith("- ")):
        return _parse_sequence(lines, j, ind)
    return None, i


def _parse_block(lines: list[str], i: int, min_indent: int):
    """解析缩进块 (映射或序列), 返回 (value, next_i)。"""
    j = _next_content(lines, i)
    if j >= len(lines):
        return None, j
    stripped = _strip_yaml_comment(lines[j]).rstrip()
    ind = _indent_of(stripped)
    if ind < min_indent:
        return None, j
    content = stripped.strip()
    if content == "-" or content.startswith("- "):
        return _parse_sequence(lines, j, ind)
    return _parse_mapping(lines, j, ind)


def _parse_mapping(
    lines: list[str], i: int, key_indent: int, first: tuple[str, int] | None = None
) -> tuple[dict, int]:
    """解析映射。first=(content, indent) 用于序列项 `- key: val` 的首行。"""
    result: dict = {}
    pending_first = first
    while i < len(lines) or pending_first is not None:
        if pending_first is not None:
            content, ind = pending_first
            pending_first = None
            i += 1  # 消费 `- key: val` 的 dash 行, 后续逻辑与普通 key 行一致
        else:
            raw = lines[i]
            stripped = _strip_yaml_comment(raw).rstrip()
            if not stripped.strip():
                i += 1
                continue
            ind = _indent_of(stripped)
            if ind < key_indent:
                break
            if ind > key_indent:
                raise _YamlLiteError(f"line {i + 1}: unexpected indent")
            content = stripped.strip()
            if content == "-" or content.startswith("- "):
                raise _YamlLiteError(f"line {i + 1}: sequence item inside mapping")
            i += 1
        key, rest = _split_key(content, i)
        if _BLOCK_SCALAR_RE.match(rest or ""):
            result[key], i = _parse_block_scalar(lines, i, rest, ind)
        elif rest == "":
            result[key], i = _parse_value_block(lines, i, ind)
        else:
            value = _parse_scalar_lite(rest)
            # 只有 plain 标量才折续行; 引号串/flow 后面跟内容 = 解析错误
            if rest[:1] not in ("'", '"', "[", "{"):
                value, i = _fold_plain_continuation(lines, i, ind, value)
            result[key] = value
    return result, i


def _parse_sequence(lines: list[str], i: int, seq_indent: int) -> tuple[list, int]:
    result: list = []
    while i < len(lines):
        raw = lines[i]
        stripped = _strip_yaml_comment(raw).rstrip()
        if not stripped.strip():
            i += 1
            continue
        ind = _indent_of(stripped)
        if ind < seq_indent:
            break
        if ind > seq_indent:
            raise _YamlLiteError(f"line {i + 1}: unexpected indent in sequence")
        content = stripped.strip()
        if not (content == "-" or content.startswith("- ")):
            break
        item_src = stripped[seq_indent + 1 :]  # dash 后的剩余部分
        lead = len(item_src) - len(item_src.lstrip(" "))
        item_indent = seq_indent + 1 + lead
        item_text = item_src.lstrip(" ")
        if item_text == "":
            # 裸 `-` 项: 嵌套块必须比序列缩进更深 (同缩进的下一个 `-` 是兄弟项)
            value, i = _parse_block(lines, i + 1, seq_indent + 1)
            result.append(value)
        elif _is_key_line(item_text):
            # `- key: val` = 映射项: 首行 key 在 item_indent 列
            value, i = _parse_mapping(lines, i, item_indent, first=(item_text, item_indent))
            result.append(value)
        elif item_text == "-" or item_text.startswith("- "):
            # 序列里直接嵌序列 (罕见), 不猜折叠方式 — 按解析失败报错
            raise _YamlLiteError(f"line {i + 1}: nested inline sequence not supported")
        else:
            value = _parse_scalar_lite(item_text)
            i += 1
            if item_text[:1] not in ("'", '"', "[", "{"):
                value, i = _fold_plain_continuation(lines, i, seq_indent, value)
            result.append(value)
    return result, i


def _yaml_lite_load(text: str):
    """stdlib 降级 YAML 子集解析器 (PyYAML 不可用时的 issue #65 兜底)。"""
    if not text.strip():
        return None  # 与 yaml.safe_load("") 一致
    lines = text.splitlines()
    value, _ = _parse_block(lines, 0, 0)
    if not isinstance(value, dict):
        raise _YamlLiteError("frontmatter must be a mapping")
    return value


def parse_frontmatter(text: str) -> tuple[dict | None, str]:
    """Parse YAML frontmatter from markdown text. Return (dict, body).

    PyYAML 可用时用 safe_load (更正确); 缺失时用 _yaml_lite_load 降级解析。
    解析失败统一返回 {"_error": ...}, 由 check_frontmatter 按文件报错 —
    不因缺依赖 exit 2, 也不在解析不动时假装成功 (issue #65)。
    """
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, text
    yaml_text = text[4:end]
    body = text[end + 5 :]
    try:
        if yaml is not None:
            return yaml.safe_load(yaml_text), body
        return _yaml_lite_load(yaml_text), body
    except Exception as e:
        # yaml.YAMLError / _YamlLiteError 都走同一报告路径
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
        # audit scratch dir — the OpenCodeReview audit report is not a
        # knowledge bundle entry; treating it as one would emit a false
        # `missing type field` error.
        ".audit",
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
            # 2026-10-01 validate 债务清理: 以下 type 是仓库里真实在用的有意分类,
            # 之前只因枚举过窄而报 unknown type — 扩枚举, 不改文件 frontmatter。
            "Document",            # QUALITY_PLAN.md, docs/workflows/post-release-maintenance.md
            "Report",              # AUDIT_REPORT_*.md
            "Documentation",       # docs/*.md 叙述性文档, prgenius/CHANGELOG.md
            "Analysis",            # docs/pr-genius-efficiency-analysis.md
            "Reference",           # docs/tool_call_prediction_table.md
            "agent-guide",         # CLAUDE.md
            "Maintainer Document", # docs/maintainer/pr-genius-observation.md
            "Case Study",          # anti-patterns/*-pending.md (待定性 PR 案例记录)
            "Target Pattern",      # success-patterns/*-target.md (贡献目标画像)
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


PROFILE_LINK_RE = re.compile(r"\]\(\./profiles/([^)/]+)/index\.md\)")


def check_root_index_consistency(root_index: Path, profiles_dir: Path) -> None:
    """Check 3: root index.md 索引到每个 profiles/ 子仓 (OKF S2/S4).

    本 bundle 的"子仓"是 profiles/ 下的 Repo Profile。比较根 index.md 里
    ./profiles/<slug>/index.md 链接覆盖的 slug 集合与 profiles/ 子目录集合:
    未被索引的 profile 或指向不存在 profile 的悬空链接都算漂移 (warning)。

    2026-10-01 修正: 旧实现拿"根目录顶层目录数 (19)"当子仓数去对"全表行数
    (~61, 含工具/type 词汇表)", 两个口径都错 — 表格行数漂移警告从那时起就是
    测量失真。现在改为 1:1 覆盖检查。
    """
    print(f"[Check 3] Root index.md consistency")
    if not root_index.exists():
        errors.append("index.md not found")
        return
    text = root_index.read_text(encoding="utf-8")
    linked = set(PROFILE_LINK_RE.findall(text))
    profile_dirs: set[str] = set()
    if profiles_dir.is_dir():
        profile_dirs = {
            p.name
            for p in profiles_dir.iterdir()
            if p.is_dir() and (p / "index.md").exists()
        }
    unlisted = sorted(profile_dirs - linked)
    dangling = sorted(linked - profile_dirs)
    print(
        f"   root index.md profile links: {len(linked)}, "
        f"profiles/ subdirs: {len(profile_dirs)}"
    )
    if unlisted or dangling:
        detail = ""
        if unlisted:
            detail += f"; unlisted: {', '.join(unlisted)}"
        if dangling:
            detail += f"; dangling: {', '.join(dangling)}"
        warnings.append(
            f"root index.md profile links ({len(linked)}) vs profiles/ subdirs "
            f"({len(profile_dirs)}) differ significantly{detail}"
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
    # Include pr-* case studies + README.md (which references patterns in examples)
    case_files = [f for f in files if f.name.startswith("pr-") or f.name == "README.md"]
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


# loader 实际读取的字段 —— 写进 frontmatter 才算数
_LOADER_CONSUMED = ("trigger_keywords", "match_mode", "severity", "symptom")
# 明显的占位符, 不是真值
_PLACEHOLDERS = {"no-keywords", "no_keywords", "todo", "tbd", "xxx", "fixme", "none", "null"}


def check_pattern_loader_visibility() -> None:
    """Check 4b: 字段必须写在 frontmatter 里, 否则 loader 根本看不见.

    为什么需要这一层: 2026-10-04 发现 anti-patterns/ 里有文件把
    `trigger_keywords:` 写在 **正文** (frontmatter 的收尾 `---` 之后),
    值还是占位符 `no-keywords`. load_anti_patterns 只读 frontmatter,
    于是这些模式 0 关键词、永不可能命中 —— 而且没有任何东西会报警.
    一个作者把字段写错位置就静默失效, 这类腐烂必须由校验器挡.

    顺带挡两类同源问题:
      - 字段值是占位符 (no-keywords / TODO / tbd ...), 那不是真关键词;
      - anti-patterns/ 里放着 `type: Lesson` 的文件 —— 装错目录,
        loader 会把它当反模式数进分母.
    """
    print("[Check 4b] Pattern loader visibility (fields must be in frontmatter)")
    d = ROOT / "anti-patterns"
    if not d.is_dir():
        print("   (no anti-patterns/ dir, skip)")
        return

    misplaced: list[str] = []
    placeholder: list[str] = []
    misfiled: list[str] = []

    for f in sorted(d.glob("*.md")):
        if f.name == "README.md":
            continue
        text = f.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)
        if fm is None or "_error" in (fm or {}):
            continue

        # 1. loader 字段写在正文里 → loader 看不到
        for field in _LOADER_CONSUMED:
            if field in fm:
                continue
            # 正文里出现 `字段名:` 开头的行, 说明作者本意是给 loader 的
            if re.search(rf"^{field}\s*:", body or "", re.MULTILINE):
                misplaced.append(f"{f.relative_to(ROOT)}: `{field}` is in the body, not the frontmatter — load_anti_patterns will never see it")

        # 2. 占位符值
        for field in _LOADER_CONSUMED:
            v = fm.get(field)
            if isinstance(v, str) and v.strip().lower() in _PLACEHOLDERS:
                placeholder.append(f"{f.relative_to(ROOT)}: `{field}` is a placeholder ({v!r}), not a real value")
            if isinstance(v, list):
                for item in v:
                    if isinstance(item, str) and item.strip().lower() in _PLACEHOLDERS:
                        placeholder.append(f"{f.relative_to(ROOT)}: `{field}` contains placeholder {item!r}")

        # 3. 装错目录 —— anti-patterns/ 只该放 Anti-Pattern。
        #    loader 会把目录里所有 .md 都当反模式数进分母, 放 Lesson/Case Study
        #    会让覆盖率分母虚高, 也让"反模式"这个词失去意义。
        ftype = str(fm.get("type", "")).strip()
        if ftype and ftype != "Anti-Pattern":
            misfiled.append(
                f"{f.relative_to(ROOT)}: type is `{ftype}` but the file sits in anti-patterns/ "
                f"(load_anti_patterns counts it as an anti-pattern, inflating the denominator)"
            )

    for msg in misplaced + placeholder:
        warnings.append(msg)
    for msg in misfiled:
        warnings.append(msg)

    print(
        f"   misplaced-fields: {len(misplaced)}, placeholder-values: {len(placeholder)}, "
        f"misfiled-type: {len(misfiled)}"
    )


def check_dsh_manifest_contract() -> None:
    """Check 4c: package.json 的 dsh.compatibility.dshReleases 只能用契约允许的值.

    契约出处: DSH-Store registry/README.md —— "声明值只接受 compatible、
    incompatible 或 unknown; 未声明的版本写为 unknown"。
    2026-10-05 自动检查报 AUTOMATIC_POLICY_REJECTED, 因为我们写的是 "planned"
    (不在允许集合里)。这类枚举写错没有任何本地反馈, 只有等外部扫描器发现,
    所以要进 validate。

    注意诚实性: 值本身必须反映实测结果。插件曾在真 DSH 宿主跑过 (issue
    #100/#101/#103 即真机暴露), 但 2.1.5 起的修复未复验 —— 所以某个版本标
    compatible/incompatible 由维护者的实测决定, 校验器不替你判断。这里只挡
    "planned" 这类非法枚举。
    """
    print("[Check 4c] DSH manifest compatibility contract")
    allowed = {"compatible", "incompatible", "unknown"}
    p = ROOT / "package.json"
    if not p.is_file():
        print("   (no package.json, skip)")
        return
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except ValueError as e:
        errors.append(f"package.json: unreadable JSON: {e}")
        return
    rel = data.get("dsh", {}).get("compatibility", {}).get("dshReleases")
    if rel is None:
        print("   (no dsh.compatibility.dshReleases, skip)")
        return
    bad = [f"{k}={v!r}" for k, v in rel.items() if v not in allowed]
    if bad:
        errors.append(
            "package.json dsh.compatibility.dshReleases: value must be one of "
            f"{sorted(allowed)} — got {', '.join(bad)} "
            "(DSH-Store rejects the whole entry on this)"
        )
    print(f"   dshReleases: {len(rel)} entries, {len(bad)} invalid")

    # DSH-Store 的 compatibility 还要求 dsh/node/systems/profiles 四项**必填**
    # （registry/catalog-detail.schema.json 的 required）。缺一项整条候选被拒 ——
    # #1304 就是这么被 AUTOMATIC_POLICY_REJECTED 的。枚举合法但字段缺失同样过不了，
    # 所以一起挡。
    comp = data.get("dsh", {}).get("compatibility") or {}
    required_fields = ("dsh", "node", "systems", "profiles")
    missing = [f for f in required_fields if f not in comp]
    if missing:
        errors.append(
            "package.json dsh.compatibility is missing required field(s): "
            f"{missing} — the store schema requires all four "
            f"{list(required_fields)}"
        )
    ops = comp.get("dshOperations") or {}
    ops_allowed = {"passed", "failed", "unknown"}
    bad_ops = [
        f"{rel}/{op}={val!r}"
        for rel, record in ops.items()
        if isinstance(record, dict)
        for op, val in record.items()
        if val not in ops_allowed
    ]
    if bad_ops:
        errors.append(
            "package.json dsh.compatibility.dshOperations: value must be one of "
            f"{sorted(ops_allowed)} — got {', '.join(bad_ops)}"
        )
    print(f"   compatibility: {len(required_fields) - len(missing)}/{len(required_fields)} required fields present")


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
    check_root_index_consistency(root_index, ROOT / "profiles")
    check_anti_pattern_referenced(md_files)
    check_pattern_loader_visibility()
    check_dsh_manifest_contract()
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

    # Check 9 (issue #41): review-cases/*.json evidence gate.
    # validate_checks 可选模块的 house pattern 是 ImportError 时跳过, 但这个
    # check 本身就是证据门 —— 模块缺失时静默跳过 = 又假绿。所以只有在不带
    # --enforce-evidence 时才允许"没装模块就跳过"; 带 flag 时模块缺失按 error 处理。
    enforce_evidence_flag = "--enforce-evidence" in sys.argv
    try:
        from validate_checks.review_case_evidence import check_review_case_evidence
    except ImportError as e:
        check_review_case_evidence = None
        print(f"[Check 9] review_case_evidence not available: {e}")
    if check_review_case_evidence is not None:
        check_review_case_evidence(
            ROOT, warnings, errors, enforce_evidence=enforce_evidence_flag
        )
    elif enforce_evidence_flag:
        errors.append(
            "[evidence-gate] validate_checks.review_case_evidence unavailable — "
            "--enforce-evidence cannot verify review-cases/*.json"
        )

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
    # In strict mode, only fail on critical warnings (not orphan anti-patterns or profile evidence)
    #
    # 牙齿（2026-10-17 定）：新鲜度降级后一度空心，现已选定并启用
    # **「无证据的肯定断言」**（agent_guidelines.<k> 缺 evidence_url）
    # 作为 critical —— 说了政策却不给出处，是本仓最不该放过的错误。
    # 所以 --strict 比 validate.py 多的那一道门就是它。
    if "--strict" in sys.argv:
        critical_warnings = [w for w in warnings if not (
            w.startswith("orphan anti-pattern:") or
            # 「无证据的肯定断言」**升级为 critical**（2026-10-17 定）。
            # 理由：这个仓库的核心资产就是「每句话可追溯」。一条说了政策却
            # 不给出处的断言，比文件过期严重得多 —— 它会被人当成事实引用。
            # 所以从排除名单里拿掉，让 --strict 因它变红。
            # (原先是排除的；同日把新鲜度降级后 --strict 变空心，这一类是
            #  选定的「牙齿」。)
            "unknown type" in w or
            "differ significantly" in w or
            # 新鲜度（check 7）**一律不挡 --strict**，已标记与未标记都只报告。
            #
            # 理由（2026-10-17 定）：这条门禁按**日历**变红，不按**内容**变红。
            # 它测的是「时间过去了」，不是「东西错了」。实测批次：
            # 10-08 十个、10-14 五个、10-16 十三个、10-18 预告十四个 ——
            # 四批全是同一件事，手工打标记成了纯劳役，而且画像数还会涨。
            # 未标记的超期仍然照印（并且措辞与已标记的区分开），它回到
            # **信号**这个位置；真正该挡门的是内容错误：假数字、断链、
            # 无证据的肯定断言 —— 那些走 errors，不过这个判定。
            #
            # 已标记的措辞是 "... marked needs-reverify (stale analysis retained,
            # not re-verified)"，未标记的是 "... re-verify"，两者都含
            # "90d threshold"。用它做签名，两种一起放行。
            "90d threshold" in w or
            # review-case evidence (check 9): --strict 对证据缺失**一律不挡**
            # （与 check 9 的 docstring 一致：findings 进 warnings, 不挡 --strict）。
            # 执法只在 --enforce-evidence 那一步, 且按方案 G1 分流:
            #   - `[evidence-gate/declared-debt]` = 存量已声明债务 → warnings
            #   - `[evidence-gate]` (无 declared-debt) = 新增记录缺证据 → errors
            # errors 走上面的 `if errors: return 1`, 不经过这里的 critical 判定。
            # 用前缀匹配, 同时覆盖两种标签。
            "[evidence-gate" in w
        )]
        if critical_warnings:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())