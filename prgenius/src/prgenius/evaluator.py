"""PR Evaluator — 提交前改进顾问

v1.0.0: 从"合并概率预测器"转为"提交前改进顾问"
- 核心接口: analyze_pr() → 结构化信号 + 可操作建议 + 三档风险
- 降级: predict_success_rate() 仅内部使用，不对外暴露
- 砍掉: 成功模式匹配从评分中移除（语义太粗，跨仓库泛化差）
- 保留: 反模式检测 + 标签信号 + author 历史 → 直接输出 actionable 建议
"""
from __future__ import annotations
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ============================================================
# 常量
# ============================================================

# 标签信号 — 用于检测，不再用于评分
LABEL_SIGNALS: Dict[str, str] = {
    # 负面
    "ai-policy-violation": "negative",
    "invalid": "negative",
    "wontfix": "negative",
    "spam": "negative",
    "duplicate": "negative",
    "missing-issue-link": "negative",
    "needs-information": "negative",
    "awaiting-response": "negative",
    "stale": "negative",
    "new-contributor": "neutral",
    "first-time contributor": "neutral",
    # 正面
    "help wanted": "positive",
    "good first issue": "positive",
    "enhancement": "positive",
    "bug": "positive",
    "documentation": "positive",
    "dependencies": "positive",
}

# Bot 作者集合
BOT_AUTHORS = {
    "dependabot[bot]", "pre-commit-ci[bot]", "renovate[bot]",
    "github-actions[bot]", "mergify[bot]", "codecov[bot]",
    "snyk-bot", "greenkeeper[bot]",
}

# Issue 关联正则
ISSUE_LINK_RE = re.compile(
    r"(?:fix(?:es|ed)?|close[sd]?|resolve[sd]?|references?|related\s+to)\s+?",
    re.IGNORECASE,
)

# author_association 描述
ASSOCIATION_LABELS = {
    "OWNER": "仓库所有者",
    "MEMBER": "组织成员",
    "COLLABORATOR": "协作者",
    "CONTRIBUTOR": "历史贡献者",
    "NONE": "首次贡献者",
}

# 反模式严重程度
ANTI_PATTERN_SEVERITY = {
    "ai-generated-content": "critical",
    "spam": "critical",
    "cosmetic-no-user-pain": "high",
    "breaking-change-no-compat": "high",
    "missing-issue-reference": "high",
    "duplicate-pr-same-author": "high",
    "low-value-contribution": "medium",
    "upstream-already-implementing": "medium",
    "fork-main-sync-upstream": "low",
}


# ============================================================
# 辅助函数
# ============================================================

def is_bot_author(author: str) -> bool:
    """判断是否为 Bot 作者

    规则优先级:
    1. 白名单精确匹配
    2. login 以 [bot] 结尾 → 确定是 bot
    3. login 包含 -bot 或 _bot → 弱信号 (不单独使用)
    """
    login = author.lower().strip()
    # 白名单
    if login in {a.lower() for a in BOT_AUTHORS}:
        return True
    # 通用规则: [bot] 后缀
    if login.endswith("[bot]"):
        return True
    return False


def get_repo_size(star_count: int) -> str:
    if star_count < 5000:
        return "small"
    elif star_count < 50000:
        return "medium"
    else:
        return "large"


def check_issue_link(body: str) -> bool:
    return bool(ISSUE_LINK_RE.search(body))


def _check_requires_dco(repo: str, repo_root) -> Optional[bool]:
    """检查仓库是否要求 DCO sign-off

    返回:
        True  — requires_dco: true
        False — requires_dco: false
        None  — 未找到 profile 或未声明
    """
    # v1.4.0 修复: 接受 str | Path
    repo_root = Path(repo_root) if not isinstance(repo_root, Path) else repo_root
    # 尝试加载仓库 profile
    target_folder = repo.replace("/", "-").lower()
    profile_dir = repo_root / "profiles" / target_folder
    index_file = profile_dir / "index.md"
    if not index_file.exists():
        return None

    try:
        content = index_file.read_text(encoding="utf-8")
        match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if not match:
            return None
        # 简单搜索 requires_dco 字段
        for line in match.group(1).split("\n"):
            line = line.strip()
            if line.startswith("requires_dco:") or line.startswith("require_signed_off:"):
                value = line.split(":", 1)[1].strip().lower()
                if value in ("true", "yes"):
                    return True
                elif value in ("false", "no"):
                    return False
        return None
    except Exception:
        return None


def _check_require_issue_first(repo: str, repo_root) -> Optional[bool]:
    """检查仓库是否要求先 Issue 后 PR

    返回:
        True  — require_issue_first: true
        False — require_issue_first: false
        None  — 未找到 profile 或未声明
    """
    # v1.4.0 修复: 接受 str | Path
    repo_root = Path(repo_root) if not isinstance(repo_root, Path) else repo_root
    target_folder = repo.replace("/", "-").lower()
    index_file = repo_root / "profiles" / target_folder / "index.md"
    if not index_file.exists():
        return None

    try:
        content = index_file.read_text(encoding="utf-8")
        match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if not match:
            return None
        for line in match.group(1).split("\n"):
            line = line.strip()
            if line.startswith("require_issue_first:") or line.startswith("require_issue_first :"):
                value = line.split(":", 1)[1].strip().lower()
                if value in ("true", "yes"):
                    return True
                elif value in ("false", "no"):
                    return False
        return None
    except Exception:
        return None


def _check_has_policy(repo: str, repo_root) -> bool:
    """检查仓库是否有 pr-genius profile + maintainer policy

    返回:
        True  — 仓在 pr-genius 有 profile + policy 文件
        False — 无 profile 或无 policy
    """
    # v1.4.0 修复: 接受 str | Path
    repo_root = Path(repo_root) if not isinstance(repo_root, Path) else repo_root
    target_folder = repo.replace("/", "-").lower()
    profile_index = repo_root / "profiles" / target_folder / "index.md"
    if not profile_index.exists():
        return False
    policy_file = repo_root / "docs" / "policies" / f"{target_folder}.md"
    return policy_file.exists()


def _parse_label(label: str) -> Tuple[str, str]:
    """返回 (label, polarity) — positive/negative/neutral/unknown"""
    label_lower = label.lower().strip()
    if label_lower in LABEL_SIGNALS:
        return label, LABEL_SIGNALS[label_lower]
    for key, polarity in LABEL_SIGNALS.items():
        if key in label_lower:
            return label, polarity
    return label, "unknown"


# ============================================================
# 模式加载
# ============================================================

_anti_patterns_cache: Dict[str, Dict[str, dict]] = {}
_success_patterns_cache: Dict[str, Dict[str, dict]] = {}

def load_anti_patterns(repo_root) -> Dict[str, dict]:
    # v1.4.0 修复: 接受 str | Path (MCP smoke test 发现)
    repo_root = Path(repo_root) if not isinstance(repo_root, Path) else repo_root
    cache_key = str(repo_root)
    if cache_key in _anti_patterns_cache:
        return _anti_patterns_cache[cache_key]
    patterns = {}
    anti_patterns_dir = repo_root / "anti-patterns"
    if not anti_patterns_dir.exists():
        return patterns

    for file in anti_patterns_dir.glob("*.md"):
        if file.name == "README.md":
            continue
        content = file.read_text(encoding="utf-8")
        match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if not match:
            continue
        try:
            fm = {}
            current_key = None
            current_value = []
            in_list = False
            for line in match.group(1).strip().split("\n"):
                if re.match(r'^[a-zA-Z_]+:', line) and not line.startswith('  '):
                    if current_key:
                        fm[current_key] = current_value if in_list else ' '.join(current_value).strip()
                    key, value = line.split(":", 1)
                    current_key = key.strip()
                    value = value.strip()
                    if value == '':
                        current_value = []
                        in_list = True
                    elif value.startswith('['):
                        current_value = [v.strip().strip('"') for v in value[1:-1].split(",")]
                        in_list = False
                    else:
                        current_value = [value]
                        in_list = False
                elif line.startswith('  - ') and in_list:
                    current_value.append(line[4:].strip().strip('"'))
                elif line.startswith('  ') and not in_list:
                    current_value.append(line.strip())
            if current_key:
                fm[current_key] = current_value if in_list else ' '.join(current_value).strip()
            patterns[file.stem] = fm
        except Exception:
            continue

    # Load JSON patterns (from API/automation)
    # v1.6.3 修复: JSON patterns 仅用于 search_patterns() 查询,
    # 不参与 check_anti_patterns() 匹配 — 标题提取的 keywords 太泛化导致假阳性
    import json as _json
    for file in anti_patterns_dir.glob("*.json"):
        try:
            data = _json.loads(file.read_text(encoding="utf-8"))
            if isinstance(data, dict) and "id" in data:
                fm = {
                    "key": data.get("id", file.stem),
                    "description": data.get("title", data.get("description", "")),
                    "trigger_keywords": [],  # JSON patterns 不提取 keywords — 避免假阳性
                    "symptom": "",
                    "fix_action": "",
                    "source_pr": data.get("source_pr", ""),
                    "source_url": data.get("source_url", ""),
                    "_is_json_pattern": True,  # 标记来源, check_anti_patterns 跳过
                }
                patterns[file.stem] = fm
        except Exception:
            continue

    _anti_patterns_cache[cache_key] = patterns
    return patterns


# Generic words that appear in almost any PR — skip to avoid false positives
_ANTI_PATTERN_STOPWORDS = frozenset({
    # Common English words
    "small", "medium", "large", "from", "with", "when", "type", "values",
    "model", "file", "test", "this", "that", "for", "and", "the", "not",
    "but", "are", "was", "has", "have", "been", "will", "would", "could",
    "should", "may", "might", "can", "shall", "must", "need", "want",
    "like", "just", "also", "only", "even", "still", "already", "yet",
    "now", "then", "here", "there", "where", "why", "how", "what",
    "which", "who", "whom", "whose", "all", "each", "every", "both",
    "few", "more", "most", "other", "some", "such", "no", "any",
    "new", "old", "first", "last", "long", "great", "little", "own",
    "right", "big", "high", "different", "next", "early", "young",
    "important", "public", "bad", "same", "able", "back", "much",
    "go", "come", "made", "find", "thing", "many", "people", "take",
    "year", "them", "time", "very", "know", "give", "us", "about",
    # PR-specific generic words
    "readme", "fixes", "typo", "issue", "bug", "error", "fix", "update",
    "add", "remove", "delete", "rename", "move", "copy", "merge", "split",
    "refactor", "improve", "enhance", "optimize", "clean", "format",
    "lint", "style", "indent", "whitespace", "comment", "documentation",
    "example", "sample", "demo", "tutorial", "guide", "instructions",
    "build", "pull", "requests", "discussion", "docs", "bump", "junk",
    "rollup", "avoid", "set", "get", "put", "see", "way", "day", "got",
    # Code/technical generic words
    "check", "path", "diff", "site", "call", "stack", "field", "names",
    "into", "extras", "extra", "allow", "prevent", "computed", "leaking",
    "instant", "validation", "witness", "throw", "mount", "labelling",
    "error", "handle", "response", "request", "status", "code", "line",
    "function", "method", "class", "module", "import", "return", "value",
    "data", "key", "name", "id", "number", "string", "list",
    "dict", "object", "array", "null", "true", "false", "none",
    "config", "setting", "env", "environment", "server", "client",
    "token", "auth", "login", "session", "user", "password",
    "database", "table", "column", "row", "index", "query",
    # More generic technical words
    "description", "parameter", "undocumented", "meaningful",
    "timeout", "redirect", "nginx", "slash", "hang", "endpoint",
    "feat", "fix", "chore", "docs", "test", "ci", "refactor",
    "connection", "request", "response", "status", "code", "line",
    "function", "method", "class", "module", "import", "return",
    "value", "data", "key", "name", "id", "number", "string",
    "list", "dict", "object", "array", "null", "true", "false",
    "none", "config", "setting", "env", "environment", "server",
    "client", "token", "auth", "login", "session", "user", "password",
    "database", "table", "column", "row", "index", "query",
})


def check_anti_patterns(title: str, description: str, repo: str, repo_root, body: str = "") -> List[dict]:
    """检查 PR 是否命中反模式"""
    # v1.4.0 修复: 接受 str | Path
    repo_root = Path(repo_root) if not isinstance(repo_root, Path) else repo_root
    anti_patterns = load_anti_patterns(repo_root)
    matches = []
    seen_keys = set()  # 防止同一 pattern 重复命中
    text = f"{title} {description} {body}".lower()
    repo_lower = repo.strip("/").lower()
    for key, pattern in anti_patterns.items():
        if key in seen_keys:
            continue
        # v1.6.3: JSON patterns 仅用于搜索, 不参与匹配 (关键词太泛化)
        if pattern.get("_is_json_pattern"):
            continue
        # Only match anti-patterns from the same repo or generic patterns (no repo)
        pattern_repo = pattern.get("repo", "").strip("/").lower()
        if pattern_repo and pattern_repo != repo_lower:
            continue
        keywords = pattern.get("trigger_keywords", [])
        matched = False
        if isinstance(keywords, list):
            for keyword in keywords:
                kw = keyword.lower()
                # Skip generic stopwords to reduce false positives
                if kw in _ANTI_PATTERN_STOPWORDS:
                    continue
                if kw in text:
                    matches.append({
                        "key": key, "keyword": keyword,
                        "symptom": pattern.get("symptom", ""),
                        "fix_action": pattern.get("fix_action", ""),
                        "source_pr": pattern.get("source_pr", ""),
                        "source_url": pattern.get("source_url", ""),
                        "updated": pattern.get("updated", ""),
                        "confidence": pattern.get("confidence", ""),
                    })
                    seen_keys.add(key)
                    matched = True
                    break
        if not matched:
            symptom = pattern.get("symptom", "")
            if symptom and symptom.lower() in text:
                matches.append({
                    "key": key, "symptom": symptom,
                    "fix_action": pattern.get("fix_action", ""),
                    "source_pr": pattern.get("source_pr", ""),
                    "source_url": pattern.get("source_url", ""),
                    "updated": pattern.get("updated", ""),
                    "confidence": pattern.get("confidence", ""),
                })
                seen_keys.add(key)
    return matches


def load_success_patterns(repo_root) -> Dict[str, dict]:
    """保留加载但不再用于评分 — 仅作参考"""
    # v1.4.0 修复: 接受 str | Path
    repo_root = Path(repo_root) if not isinstance(repo_root, Path) else repo_root
    cache_key = str(repo_root)
    if cache_key in _success_patterns_cache:
        return _success_patterns_cache[cache_key]
    patterns = {}
    success_patterns_dir = repo_root / "success-patterns"
    if not success_patterns_dir.exists():
        return patterns
    for file in success_patterns_dir.glob("*.md"):
        if file.name == "README.md":
            continue
        content = file.read_text(encoding="utf-8")
        match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if not match:
            continue
        try:
            fm = {}
            current_key = None
            current_value = []
            in_list = False
            for line in match.group(1).strip().split("\n"):
                if re.match(r'^[a-zA-Z_]+:', line) and not line.startswith('  '):
                    if current_key:
                        fm[current_key] = current_value if in_list else ' '.join(current_value).strip()
                    key, value = line.split(":", 1)
                    current_key = key.strip()
                    value = value.strip()
                    if value == '':
                        current_value = []
                        in_list = True
                    elif value.startswith('['):
                        current_value = [v.strip().strip('"') for v in value[1:-1].split(",")]
                        in_list = False
                    else:
                        current_value = [value]
                        in_list = False
                elif line.startswith('  - ') and in_list:
                    current_value.append(line[4:].strip().strip('"'))
                elif line.startswith('  ') and not in_list:
                    current_value.append(line.strip())
            if current_key:
                fm[current_key] = current_value if in_list else ' '.join(current_value).strip()
            patterns[file.stem] = fm
        except Exception:
            continue

    # Load JSON patterns (from API/automation)
    import json as _json
    for file in success_patterns_dir.glob("*.json"):
        try:
            data = _json.loads(file.read_text(encoding="utf-8"))
            if isinstance(data, dict) and "id" in data:
                # Normalize JSON pattern to match MD format
                fm = {
                    "key": data.get("id", file.stem),
                    "description": data.get("title", data.get("description", "")),
                    "tags": data.get("tags", []),
                    "source_pr": data.get("source_pr", ""),
                }
                patterns[file.stem] = fm
        except Exception:
            continue

    _success_patterns_cache[cache_key] = patterns
    return patterns


# ============================================================
# 核心: analyze_pr — 提交前改进顾问
# ============================================================

def analyze_pr(
    title: str,
    description: str,
    repo: str,
    repo_root,
    body: str = "",
    labels: Optional[List[str]] = None,
    author: str = "",
    star_count: int = 0,
    repo_merge_rate: float = 0.0,
    author_association: str = "NONE",
    mergeable: str = "MERGEABLE",
) -> dict:
    """分析 PR 并生成结构化改进建议

    返回:
    {
        "repo": str,
        "title": str,
        "tier": "low_risk" | "medium_risk" | "high_risk",
        "signals": {
            "positive": [{"key": str, "description": str}],
            "negative": [{"key": str, "description": str, "severity": str}],
            "neutral":  [{"key": str, "description": str}]
        },
        "checklist": [
            {"action": str, "priority": "P0"|"P1"|"P2", "done": bool, "hint": str}
        ],
        "anti_patterns_hit": [...],
        "repo_context": {...}
    }
    """
    # Accept str | Path — fix str/str 除法 bug (M0 MCP smoke test 暴露)
    repo_root = Path(repo_root) if not isinstance(repo_root, Path) else repo_root
    if labels is None:
        labels = []

    signals_pos = []
    signals_neg = []
    signals_neu = []
    checklist = []

    # ---- 0. 合并冲突检查 ----
    if mergeable and mergeable.upper() == "CONFLICTING":
        signals_neg.append({
            "key": "merge_conflict",
            "description": "PR 有合并冲突，需要 rebase 或解决冲突",
            "severity": "high",
        })
        checklist.append({
            "action": "resolve_conflicts",
            "priority": "P0",
            "done": False,
            "hint": "解决合并冲突后 force push",
        })

    # ---- 1. Issue 关联检查 (跳过 Bot, 仓库感知) ----
    is_bot = is_bot_author(author)
    require_issue_first = _check_require_issue_first(repo, repo_root)

    if not is_bot:
        has_issue_link = check_issue_link(body) if body else False
        if has_issue_link:
            signals_pos.append({"key": "issue_linked", "description": "PR body 包含 Issue 关联 (fixes/closes/resolves #NNN)"})
        else:
            # 仓库感知：require_issue_first 决定严重程度
            if require_issue_first is True:
                signals_neg.append({
                    "key": "no_issue_link",
                    "description": "PR body 缺少 Issue 关联（该仓库要求先 Issue 后 PR）",
                    "severity": "high",
                })
                checklist.append({
                    "action": "add_issue_link",
                    "priority": "P0",
                    "done": False,
                    "hint": "在 body 中添加 `Fixes #NNN` 或 `Closes #NNN`，关联已有的 Issue",
                })
            elif require_issue_first is None:
                # 未知仓库，降级为 P2 提醒
                signals_neu.append({
                    "key": "no_issue_link_hint",
                    "description": "PR body 未包含 Issue 关联，建议确认是否需要",
                })
                checklist.append({
                    "action": "add_issue_link",
                    "priority": "P2",
                    "done": False,
                    "hint": "建议在 body 中添加 Issue 关联（如果仓库要求）",
                })
            # require_issue_first = False → 不提示

    # ---- 2. 反模式检测 ----
    anti_matches = check_anti_patterns(title, description, repo, repo_root, body=body)
    for match in anti_matches:
        key = match["key"]
        severity = ANTI_PATTERN_SEVERITY.get(key, "medium")
        symptom = match.get("symptom", "")
        fix_action = match.get("fix_action", "")
        source_pr = match.get("source_pr", "")

        # 建设性信号描述: 症状 + 改进方向 + 案例来源
        desc_parts = []
        if symptom:
            desc_parts.append(symptom)
        else:
            desc_parts.append(f"反模式风险: {key}")
        if fix_action:
            desc_parts.append(f"改进: {fix_action}")
        if source_pr:
            desc_parts.append(f"(参考: {source_pr})")

        signals_neg.append({
            "key": key,
            "description": " | ".join(desc_parts),
            "severity": severity,
            "fix_action": fix_action,
            "source_pr": source_pr,
        })
        if fix_action:
            checklist.append({
                "action": f"fix_{key}",
                "priority": "P0" if severity in ("critical", "high") else "P1",
                "done": False,
                "hint": fix_action,
            })

    # ---- 3. 标签信号 ----
    negative_labels = []
    positive_labels = []
    for label in labels:
        _, polarity = _parse_label(label)
        if polarity == "negative":
            negative_labels.append(label)
        elif polarity == "positive":
            positive_labels.append(label)

    if negative_labels:
        signals_neg.append({
            "key": "negative_labels",
            "description": f"PR 带有负面标签: {', '.join(negative_labels)}",
            "severity": "high",
        })
        checklist.append({
            "action": "resolve_labels",
            "priority": "P0",
            "done": False,
            "hint": "先解决标签标记的问题（如 missing-issue-link → 添加 Issue 关联）再提交",
        })
    if positive_labels:
        signals_pos.append({"key": "positive_labels", "description": f"PR 带有正面标签: {', '.join(positive_labels)}"})

    # ---- 4. 作者身份分析 ----
    assoc_upper = author_association.upper().strip()
    assoc_label = ASSOCIATION_LABELS.get(assoc_upper, assoc_upper)

    if is_bot:
        signals_neu.append({"key": "bot_author", "description": f"Bot PR ({author})"})
    elif assoc_upper == "OWNER":
        signals_pos.append({"key": "owner_author", "description": "仓库所有者提交，通常有更高合并率"})
    elif assoc_upper in ("MEMBER", "COLLABORATOR"):
        signals_pos.append({"key": "insider_author", "description": f"{assoc_label}，有仓库写入权限"})
    elif assoc_upper == "CONTRIBUTOR":
        signals_pos.append({"key": "returning_contributor", "description": "历史贡献者，有合并记录"})
    elif assoc_upper == "NONE":
        if star_count > 20000:
            # High merge rate repos: lower severity
            first_contrib_severity = "low" if repo_merge_rate >= 0.6 else "medium"
            signals_neg.append({
                "key": "first_contributor_large_repo",
                "description": f"首次在大仓 ({star_count:,}⭐) 提 PR，外部贡献者合并率通常较低",
                "severity": first_contrib_severity,
            })
            checklist.append({
                "action": "build_trust",
                "priority": "P1",
                "done": False,
                "hint": "先在 Issue 中参与讨论、回复评论，建立维护者信任后再提 PR",
            })
        else:
            signals_neu.append({"key": "first_contributor", "description": "首次贡献者"})

    # ---- 5. 仓库上下文 ----
    repo_context = {}
    if star_count > 0:
        repo_context["star_count"] = star_count
        repo_context["repo_size"] = get_repo_size(star_count)
    if repo_merge_rate > 0:
        repo_context["merge_rate"] = repo_merge_rate
        if repo_merge_rate < 0.3:
            signals_neu.append({"key": "strict_repo", "description": f"该仓库近期 merge 率较低 ({repo_merge_rate:.0%})，审查严格"})
        elif repo_merge_rate > 0.8:
            signals_pos.append({"key": "lenient_repo", "description": f"该仓库近期 merge 率较高 ({repo_merge_rate:.0%})"})
            # High merge rate offsets big repo penalty
            if star_count > 20000:
                # Remove the "first_contributor_large_repo" negative signal if present
                signals_neg[:] = [s for s in signals_neg if s.get("key") != "first_contributor_large_repo"]

    # ---- 5.5. 无 policy 大仓 needs_preflight 检查 (克莱恩 2026-07-19 P1) ----
    has_policy = _check_has_policy(repo, repo_root)
    repo_context["has_policy"] = has_policy

    # Check if repo has a profile (even without policy)
    from .parser import profile_get
    has_profile = profile_get(repo_root, repo) is not None

    # Only trigger preflight if no profile AND no policy AND genuinely large repo
    if not has_policy and not has_profile and star_count >= 10000:
        # High merge rate repos: lower severity
        if repo_merge_rate >= 0.6:
            preflight_severity = "low"
        else:
            preflight_severity = "medium"  # Reduced from "high" — profile exists
        signals_neg.append({
            "key": "needs_preflight",
            "description": (
                f"大仓 ({star_count:,}⭐) 无 pr-genius profile/policy。"
                "对未知仓, 默认不轻易 pass, 必须跑 preflight 检查。"
            ),
            "severity": preflight_severity,
            "generic_checks": [
                "confirm real bug (not feature request / enhancement only)",
                "link issue or maintainer request (avoid unsolicited)",
                "check CONTRIBUTING / CODEOWNERS for required artifacts",
                "check duplicate PRs (gh search prs --state all)",
                "check repo archived status (gh repo view)",
                "run tests locally + check CI status",
            ],
        })
        for check in [
            "confirm real bug",
            "link issue or maintainer request",
            "check CONTRIBUTING",
            "check duplicate PRs",
            "check archived status",
            "run tests + check CI",
        ]:
            checklist.append({
                "action": f"preflight_{check.split()[0].lower()}",
                "priority": "P0",
                "done": False,
                "hint": check,
            })

    # ---- 6. Bot 特殊检查 ----
    if is_bot:
        # Bot PR 通常有 auto-merge，但小仓更可靠
        if star_count > 0 and star_count < 5000:
            signals_pos.append({"key": "bot_small_repo", "description": "小仓 Bot PR 通常配置了 auto-merge"})
        checklist.append({
            "action": "bot_auto_merge",
            "priority": "P2",
            "done": True,  # Bot 通常自动处理
            "hint": "Bot PR 通常由自动化流程处理",
        })

    # ---- 7. 通用清单 ----
    if not is_bot:
        checklist.append({
            "action": "ci_passing",
            "priority": "P1",
            "done": False,
            "hint": "确认 CI 全部通过",
        })

        # DCO: 仓库感知
        requires_dco = _check_requires_dco(repo, repo_root)
        if requires_dco is True:
            checklist.append({
                "action": "dco_signoff",
                "priority": "P1",
                "done": False,
                "hint": "使用 `git commit -s` 添加 DCO sign-off",
            })
        elif requires_dco is None:
            # 未知仓库，降级为 P2 提醒
            checklist.append({
                "action": "dco_signoff",
                "priority": "P2",
                "done": False,
                "hint": "确认是否需要 DCO sign-off (`git commit -s`)",
            })

    # ---- 8. 计算 tier ----
    neg_critical = sum(1 for s in signals_neg if s.get("severity") in ("critical", "high"))
    neg_medium = sum(1 for s in signals_neg if s.get("severity") == "medium")
    neg_low = sum(1 for s in signals_neg if s.get("severity") == "low")
    pos_count = len(signals_pos)

    if neg_critical >= 1:
        tier = "high_risk"
    elif neg_medium >= 2 or (neg_medium >= 1 and pos_count == 0):
        tier = "high_risk"
    elif neg_medium >= 1 or (pos_count == 0 and len(signals_neu) == 0 and neg_low == 0):
        tier = "medium_risk"
    elif pos_count >= 2 and neg_critical == 0:
        tier = "low_risk"
    else:
        tier = "medium_risk"

    # ---- 8.5. PR 大小评估 ----
    from .pr_metadata import parse_diff_stat, assess_scope, detect_breaking_change, detect_security_sensitive
    files_changed, lines_added, lines_deleted = parse_diff_stat("")
    total_lines = lines_added + lines_deleted

    # PR 大小分级 (基于标题关键词启发式)
    title_lower = title.lower()
    body_lower = body.lower() if body else ""
    combined = f"{title_lower} {body_lower}"

    # 启发式判断 PR 大小
    if any(kw in combined for kw in ["major", "refactor", "rewrite", "migration", "breaking"]):
        pr_size = "XL"
        pr_size_label = "超大 (>500 行) — 标题暗示大规模变更"
    elif any(kw in combined for kw in ["add", "implement", "feature", "enhance"]):
        pr_size = "M"
        pr_size_label = "中等 (150-300 行) — 新功能"
    elif any(kw in combined for kw in ["fix", "bug", "patch", "hotfix"]):
        pr_size = "S"
        pr_size_label = "小 (50-150 行) — Bug 修复"
    elif any(kw in combined for kw in ["docs", "readme", "typo", "comment"]):
        pr_size = "XS"
        pr_size_label = "极小 (<50 行) — 文档/注释"
    else:
        pr_size = "S"
        pr_size_label = "小 (50-150 行)"

    # 影响评分 (0-100)
    impact_score = 0

    # 基于标题关键词评分
    if any(kw in combined for kw in ["breaking", "migration", "deprecat"]):
        impact_score += 40  # Breaking change
    elif any(kw in combined for kw in ["security", "auth", "vulnerability", "cve"]):
        impact_score += 35  # Security
    elif any(kw in combined for kw in ["major", "refactor", "rewrite"]):
        impact_score += 30  # Major refactor
    elif any(kw in combined for kw in ["add", "implement", "feature"]):
        impact_score += 20  # New feature
    elif any(kw in combined for kw in ["fix", "bug", "patch"]):
        impact_score += 10  # Bug fix
    elif any(kw in combined for kw in ["docs", "readme", "typo"]):
        impact_score += 5   # Documentation

    # 基于 labels 评分
    if labels:
        if any("breaking" in l.lower() for l in labels):
            impact_score += 25
        if any("security" in l.lower() for l in labels):
            impact_score += 20
        if any("feature" in l.lower() for l in labels):
            impact_score += 15

    impact_score = min(100, impact_score)

    # 风险分类
    if impact_score >= 70:
        risk_level = "high"
        risk_description = "高风险变更，需要仔细审查"
    elif impact_score >= 40:
        risk_level = "medium"
        risk_description = "中等风险，建议审查"
    else:
        risk_level = "low"
        risk_description = "低风险变更"

    # ---- 9. 合并概率估算 + 优化路径 ----
    merge_rate = repo_context.get("external_merge_rate_30", 0.0)

    # 直接用仓库合并率作为基础概率
    # 这是最诚实的起点：你在这个仓库提 PR，平均能 merge 多少
    if merge_rate > 0:
        base_probability = merge_rate
    else:
        # 无数据时用 tier 估算
        if tier == "low_risk":
            base_probability = 0.60
        elif tier == "medium_risk":
            base_probability = 0.35
        else:
            base_probability = 0.15

    # 只对真正区分性的信号做调整（避免和 tier 重复计算）
    # 这些信号能改变合并概率，不只是风险标记
    for neg in signals_neg:
        key = neg.get("key", "")
        if key == "merge_conflict":
            base_probability *= 0.3  # 有冲突 → 大幅降低
        elif key == "duplicate_pr_explicit_declare":
            base_probability *= 0.1  # 明确重复 → 几乎不可能
        elif key == "maintainer_internal_handling":
            base_probability *= 0.05  # 维护者要内部处理 → 不可能

    # 优化路径（所有 negative signals 都列出来供参考）
    optimization_path = []
    for neg in signals_neg:
        sev = neg.get("severity", "medium")
        if sev == "critical":
            optimization_path.append({
                "issue": neg["description"],
                "impact": "阻断性问题，必须修复",
                "priority": "P0",
            })
        elif sev == "high":
            optimization_path.append({
                "issue": neg["description"],
                "impact": "高风险，建议修复",
                "priority": "P1",
            })
        elif sev == "medium":
            optimization_path.append({
                "issue": neg["description"],
                "impact": "中等风险，建议改进",
                "priority": "P2",
            })

    merge_probability = max(0.05, min(0.95, base_probability))

    # 对比同仓库已合并 PR
    comparison = {}
    if merge_rate > 0:
        comparison["repo_merge_rate"] = merge_rate
        comparison["your_estimate"] = f"{merge_probability:.0%}"
        if merge_probability < merge_rate * 0.5:
            optimization_path.append({
                "issue": "合并概率低于仓库平均值的一半",
                "impact": "需要显著改进才能达到仓库平均水平",
                "priority": "P0",
            })

    # Positive confirmation (borrowed from Cubic AI pattern)
    if tier == "low_risk":
        summary = f"🟢 No issues found — {len(signals_pos)} positive signal(s), {len(signals_neg)} concern(s)"
    elif tier == "medium_risk":
        summary = f"🟡 {len(signals_neg)} concern(s) to review — see checklist"
    else:
        summary = f"🔴 {len(signals_neg)} blocking issue(s) — fix before submitting"

    # 去重 checklist (相同 action 只保留第一个)
    seen_actions = set()
    unique_checklist = []
    for item in checklist:
        action_key = item.get("action", "")
        if action_key not in seen_actions:
            seen_actions.add(action_key)
            unique_checklist.append(item)
    checklist = unique_checklist

    return {
        "repo": repo,
        "title": title,
        "tier": tier,
        "summary": summary,
        "merge_probability": round(merge_probability, 3),
        "optimization_path": optimization_path,
        "signals": {
            "positive": signals_pos,
            "negative": signals_neg,
            "neutral": signals_neu,
        },
        "checklist": checklist,
        "anti_patterns_hit": [m["key"] for m in anti_matches],
        "anti_patterns_detail": anti_matches,
        "repo_context": repo_context,
        "comparison": comparison,
        # v1.6.3: PR 大小和影响评估
        "pr_size": pr_size,
        "pr_size_label": pr_size_label,
        "impact_score": impact_score,
        "risk_level": risk_level,
        "risk_description": risk_description,
    }


# ============================================================
# 兼容: eval_pr — 降级为三档显示
# ============================================================

def eval_pr(
    title: str,
    description: str,
    repo: str,
    repo_root: Path,
    body: str = "",
    labels: Optional[List[str]] = None,
    author: str = "",
    star_count: int = 0,
    repo_merge_rate: float = 0.0,
    author_association: str = "NONE",
) -> dict:
    """评估 PR — 降级为三档，核心数据来自 analyze_pr"""
    analysis = analyze_pr(
        title, description, repo, repo_root,
        body=body, labels=labels, author=author,
        star_count=star_count, repo_merge_rate=repo_merge_rate,
        author_association=author_association,
    )

    # 兼容旧接口
    tier_map = {"low_risk": "低风险", "medium_risk": "中风险", "high_risk": "高风险"}

    return {
        "title": title,
        "description": description,
        "repo": repo,
        "author": author,
        "labels": labels,
        "is_bot": is_bot_author(author) if author else False,
        "tier": tier_map.get(analysis["tier"], analysis["tier"]),
        "tier_raw": analysis["tier"],
        "analysis": analysis,
    }


# ============================================================
# 内部兼容: predict_success_rate (仅供 cross_validate 使用)
# ============================================================

# 评分常量 (内部使用)
_BASE_RATE = 0.45
_ASSOCIATION_BOOST = {"OWNER": 0.40, "MEMBER": 0.25, "COLLABORATOR": 0.15, "CONTRIBUTOR": 0.04, "NONE": 0.0}
_BOT_BASE_RATES = {"small": 0.70, "medium": 0.50, "large": 0.30}


def predict_success_rate(
    title: str, description: str, repo: str, repo_root: Path,
    body: str = "", labels: Optional[List[str]] = None,
    author: str = "", star_count: int = 0,
    repo_merge_rate: float = 0.0, author_association: str = "NONE",
) -> Tuple[float, str]:
    """Deprecated: 启发式校准函数，仅供 cross_validate.py 历史兼容使用。

    不要在 CLI/MCP 中暴露。新代码应使用 analyze_pr() 或 coach_pr()。
    """
    if labels is None:
        labels = []

    # 动态基线
    dynamic_base = repo_merge_rate * 0.7 + _BASE_RATE * 0.3 if repo_merge_rate > 0 else _BASE_RATE

    # Bot 通道
    if author and is_bot_author(author):
        repo_size = get_repo_size(star_count) if star_count > 0 else "medium"
        rate = _BOT_BASE_RATES.get(repo_size, 0.50)
        label_score = sum(-10 if _parse_label(l)[1] == "negative" else 0 for l in labels) * 0.5
        rate = max(0.0, min(1.0, rate + label_score / 100))
        return rate, "高" if rate >= 0.60 else "中" if rate >= 0.35 else "低"

    # 人类 PR
    rate = dynamic_base

    # association boost
    assoc_upper = author_association.upper().strip()
    raw = _ASSOCIATION_BOOST.get(assoc_upper, 0.0)
    if assoc_upper == "OWNER":
        rate += raw
    elif raw > 0 and repo_merge_rate > 0:
        scale = max(0.50, min(1.0, (repo_merge_rate - 0.2) / 0.5))
        rate += raw * scale
    else:
        rate += raw

    # 大仓 NONE 惩罚
    if assoc_upper == "NONE" and star_count > 20000:
        rate -= 0.10

    # 反模式
    anti = check_anti_patterns(title, description, repo, repo_root, body=body)
    for m in anti:
        k = m["key"]
        if "cosmetic" in k: rate -= 0.30
        elif "breaking" in k: rate -= 0.25
        elif "ai-generated" in k or "ai-policy" in k: rate -= 0.25
        elif "duplicate" in k: rate -= 0.20
        elif "low-value" in k: rate -= 0.20
        elif "missing-issue" in k: rate -= 0.15
        elif "upstream" in k: rate -= 0.10
        else: rate -= 0.15

    # 标签
    for l in labels:
        _, pol = _parse_label(l)
        if pol == "negative": rate -= 0.10
        elif pol == "positive": rate += 0.03

    rate = max(0.0, min(1.0, rate))
    return rate, "高" if rate >= 0.60 else "中" if rate >= 0.35 else "低"
