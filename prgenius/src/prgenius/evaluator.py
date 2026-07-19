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
    r"(?:fix(?:es|ed)?|close[sd]?|resolve[sd]?)\s+#\d+",
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


def _check_requires_dco(repo: str, repo_root: Path) -> Optional[bool]:
    """检查仓库是否要求 DCO sign-off

    返回:
        True  — requires_dco: true
        False — requires_dco: false
        None  — 未找到 profile 或未声明
    """
    # 尝试加载仓库 profile
    target_folder = repo.replace("/", "-").lower()
    profile_dir = repo_root / target_folder
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


def _check_require_issue_first(repo: str, repo_root: Path) -> Optional[bool]:
    """检查仓库是否要求先 Issue 后 PR

    返回:
        True  — require_issue_first: true
        False — require_issue_first: false
        None  — 未找到 profile 或未声明
    """
    target_folder = repo.replace("/", "-").lower()
    index_file = repo_root / target_folder / "index.md"
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


def _check_has_policy(repo: str, repo_root: Path) -> bool:
    """检查仓库是否有 pr-genius profile + maintainer policy

    返回:
        True  — 仓在 pr-genius 有 profile + policy 文件
        False — 无 profile 或无 policy
    """
    target_folder = repo.replace("/", "-").lower()
    profile_index = repo_root / target_folder / "index.md"
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

def load_anti_patterns(repo_root: Path) -> Dict[str, dict]:
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
    return patterns


def check_anti_patterns(title: str, description: str, repo: str, repo_root: Path, body: str = "") -> List[dict]:
    """检查 PR 是否命中反模式"""
    anti_patterns = load_anti_patterns(repo_root)
    matches = []
    text = f"{title} {description} {body}".lower()
    for key, pattern in anti_patterns.items():
        keywords = pattern.get("trigger_keywords", [])
        if isinstance(keywords, list):
            for keyword in keywords:
                if keyword.lower() in text:
                    matches.append({
                        "key": key, "keyword": keyword,
                        "symptom": pattern.get("symptom", ""),
                        "fix_action": pattern.get("fix_action", ""),
                        "source_pr": pattern.get("source_pr", ""),
                    })
                    break
        symptom = pattern.get("symptom", "")
        if symptom and symptom.lower() in text:
            matches.append({
                "key": key, "symptom": symptom,
                "fix_action": pattern.get("fix_action", ""),
                "source_pr": pattern.get("source_pr", ""),
            })
    return matches


def load_success_patterns(repo_root: Path) -> Dict[str, dict]:
    """保留加载但不再用于评分 — 仅作参考"""
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
    return patterns


# ============================================================
# 核心: analyze_pr — 提交前改进顾问
# ============================================================

def analyze_pr(
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
        signals_neg.append({
            "key": key,
            "description": match.get("symptom", match.get("description", "")),
            "severity": severity,
            "fix_action": match.get("fix_action", ""),
            "source_pr": match.get("source_pr", ""),
        })
        if match.get("fix_action"):
            checklist.append({
                "action": f"fix_{key}",
                "priority": "P0" if severity in ("critical", "high") else "P1",
                "done": False,
                "hint": match["fix_action"],
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
            signals_neg.append({
                "key": "first_contributor_large_repo",
                "description": f"首次在大仓 ({star_count:,}⭐) 提 PR，外部贡献者合并率通常较低",
                "severity": "medium",
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
    # P0-A2 克莱恩 验收门槛: 无 policy 仓 默认 需 preflight.
    # star_count 未知 (==0) 也触发, 因用户可能不想传 star 但仍需 preflight.
    if not has_policy and (star_count >= 10000 or star_count == 0):
        signals_neg.append({
            "key": "needs_preflight",
            "description": (
                f"大仓 ({star_count:,}⭐) 无 pr-genius profile/policy。"
                "对未知仓, 默认不轻易 pass, 必须跑 preflight 检查。"
            ),
            "severity": "high",
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
    pos_count = len(signals_pos)

    if neg_critical >= 1:
        tier = "high_risk"
    elif neg_medium >= 2 or (neg_medium >= 1 and pos_count == 0):
        tier = "high_risk"
    elif neg_medium >= 1 or (pos_count == 0 and len(signals_neu) == 0):
        tier = "medium_risk"
    elif pos_count >= 2 and neg_critical == 0:
        tier = "low_risk"
    else:
        tier = "medium_risk"

    return {
        "repo": repo,
        "title": title,
        "tier": tier,
        "signals": {
            "positive": signals_pos,
            "negative": signals_neg,
            "neutral": signals_neu,
        },
        "checklist": checklist,
        "anti_patterns_hit": [m["key"] for m in anti_matches],
        "repo_context": repo_context,
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
