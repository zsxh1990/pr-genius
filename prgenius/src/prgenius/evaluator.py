"""PR Evaluator — 基于反模式和成功模式评估 PR

提供 PR 评估、建议生成、成功率预测等功能。

v0.3.0 改进:
- P0: issue-linked-fix 匹配改用正则，不再子串匹配
- P1: 新增标签信号层 (LABEL_SIGNALS)
- P2: Bot PR 独立评估通道
- 基线从 0.5 降到 0.45，阈值调整为偏保守
"""
from __future__ import annotations
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ============================================================
# 常量
# ============================================================

# P1: 标签信号层 — 正面/负面分数
LABEL_SIGNALS: Dict[str, float] = {
    # 强拒绝信号
    "ai-policy-violation": -20,
    "invalid": -20,
    "wontfix": -20,
    "spam": -25,
    "duplicate": -15,
    # 中等拒绝信号
    "missing-issue-link": -10,
    "needs-information": -10,
    "awaiting-response": -5,
    "stale": -10,
    # 弱信号
    "new-contributor": -3,
    "first-time contributor": -3,
    # 正面信号
    "help wanted": 5,
    "good first issue": 3,
    "enhancement": 3,
    "bug": 5,
    "documentation": 3,
    "dependencies": 2,
}

# P2: Bot PR 作者集合
BOT_AUTHORS = {
    "dependabot[bot]",
    "pre-commit-ci[bot]",
    "renovate[bot]",
    "github-actions[bot]",
    "mergify[bot]",
    "codecov[bot]",
    "snyk-bot",
    "greenkeeper[bot]",
}

# Issue 关联正则 — 只匹配真正的 Issue 引用
ISSUE_LINK_RE = re.compile(
    r"(?:fix(?:es|ed)?|close[sd]?|resolve[sd]?)\s+#\d+",
    re.IGNORECASE,
)

# P0: 基线和阈值（偏保守）
BASE_RATE_HUMAN = 0.45       # 人类 PR 基线（从 0.5 降到 0.45）
BOT_BASE_RATES = {           # Bot PR 基线按仓库规模
    "small": 0.70,           # <5k stars
    "medium": 0.50,          # 5k-50k stars
    "large": 0.30,           # >50k stars
}
THRESHOLD_HIGH = 0.60        # "高" 阈值（从 0.7 降到 0.6）
THRESHOLD_MED = 0.35         # "中" 阈值（从 0.4 降到 0.35）


# ============================================================
# 辅助函数
# ============================================================

def is_bot_author(author: str) -> bool:
    """判断是否为 Bot 作者"""
    return author.lower().strip() in {a.lower() for a in BOT_AUTHORS}


def get_repo_size(star_count: int) -> str:
    """根据 star 数判断仓库规模"""
    if star_count < 5000:
        return "small"
    elif star_count < 50000:
        return "medium"
    else:
        return "large"


def check_issue_link(body: str) -> bool:
    """检查 body 是否包含真正的 Issue 关联 (fixes #NNN / closes #NNN)"""
    return bool(ISSUE_LINK_RE.search(body))


def compute_label_score(labels: List[str]) -> float:
    """计算标签信号分数"""
    score = 0.0
    for label in labels:
        label_lower = label.lower().strip()
        # 精确匹配
        if label_lower in LABEL_SIGNALS:
            score += LABEL_SIGNALS[label_lower]
        else:
            # 模糊匹配（标签可能带前缀/后缀）
            for key, val in LABEL_SIGNALS.items():
                if key in label_lower:
                    score += val
                    break
    return score


# ============================================================
# 模式加载
# ============================================================

def load_anti_patterns(repo_root: Path) -> Dict[str, dict]:
    """加载反模式库"""
    patterns = {}
    anti_patterns_dir = repo_root / "anti-patterns"

    if not anti_patterns_dir.exists():
        return patterns

    for file in anti_patterns_dir.glob("*.md"):
        if file.name == "README.md":
            continue

        content = file.read_text(encoding="utf-8")

        # 解析 frontmatter
        match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if not match:
            continue

        try:
            fm = {}
            current_key = None
            current_value = []
            in_list = False

            for line in match.group(1).strip().split("\n"):
                # 检查是否是新的 key-value 对
                if re.match(r'^[a-zA-Z_]+:', line) and not line.startswith('  '):
                    # 保存之前的 key-value 对
                    if current_key:
                        if in_list:
                            fm[current_key] = current_value
                        else:
                            fm[current_key] = ' '.join(current_value).strip()

                    # 开始新的 key-value 对
                    key, value = line.split(":", 1)
                    current_key = key.strip()
                    value = value.strip()

                    # 检查是否是列表
                    if value == '':
                        current_value = []
                        in_list = True
                    elif value.startswith('['):
                        # 内联列表
                        current_value = [v.strip().strip('"') for v in value[1:-1].split(",")]
                        in_list = False
                    else:
                        current_value = [value]
                        in_list = False

                elif line.startswith('  - ') and in_list:
                    # 列表项
                    item = line[4:].strip().strip('"')
                    current_value.append(item)

                elif line.startswith('  ') and not in_list:
                    # 多行值
                    current_value.append(line.strip())

            # 保存最后一个 key-value 对
            if current_key:
                if in_list:
                    fm[current_key] = current_value
                else:
                    fm[current_key] = ' '.join(current_value).strip()

            patterns[file.stem] = fm
        except Exception:
            continue

    return patterns


def load_success_patterns(repo_root: Path) -> Dict[str, dict]:
    """加载成功模式库"""
    patterns = {}
    success_patterns_dir = repo_root / "success-patterns"

    if not success_patterns_dir.exists():
        return patterns

    for file in success_patterns_dir.glob("*.md"):
        if file.name == "README.md":
            continue

        content = file.read_text(encoding="utf-8")

        # 解析 frontmatter
        match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if not match:
            continue

        try:
            fm = {}
            current_key = None
            current_value = []
            in_list = False

            for line in match.group(1).strip().split("\n"):
                # 检查是否是新的 key-value 对
                if re.match(r'^[a-zA-Z_]+:', line) and not line.startswith('  '):
                    # 保存之前的 key-value 对
                    if current_key:
                        if in_list:
                            fm[current_key] = current_value
                        else:
                            fm[current_key] = ' '.join(current_value).strip()

                    # 开始新的 key-value 对
                    key, value = line.split(":", 1)
                    current_key = key.strip()
                    value = value.strip()

                    # 检查是否是列表
                    if value == '':
                        current_value = []
                        in_list = True
                    elif value.startswith('['):
                        # 内联列表
                        current_value = [v.strip().strip('"') for v in value[1:-1].split(",")]
                        in_list = False
                    else:
                        current_value = [value]
                        in_list = False

                elif line.startswith('  - ') and in_list:
                    # 列表项
                    item = line[4:].strip().strip('"')
                    current_value.append(item)

                elif line.startswith('  ') and not in_list:
                    # 多行值
                    current_value.append(line.strip())

            # 保存最后一个 key-value 对
            if current_key:
                if in_list:
                    fm[current_key] = current_value
                else:
                    fm[current_key] = ' '.join(current_value).strip()

            patterns[file.stem] = fm
        except Exception:
            continue

    return patterns


# ============================================================
# 评估逻辑
# ============================================================

def check_anti_patterns(title: str, description: str, repo: str, repo_root: Path, body: str = "") -> List[dict]:
    """检查 PR 是否命中反模式"""
    anti_patterns = load_anti_patterns(repo_root)
    matches = []

    # 合并标题、描述、body 进行检查
    text = f"{title} {description} {body}".lower()

    for key, pattern in anti_patterns.items():
        # 检查 trigger_keywords
        keywords = pattern.get("trigger_keywords", [])
        if isinstance(keywords, list):
            for keyword in keywords:
                if keyword.lower() in text:
                    matches.append({
                        "key": key,
                        "keyword": keyword,
                        "symptom": pattern.get("symptom", ""),
                        "fix_action": pattern.get("fix_action", ""),
                        "source_pr": pattern.get("source_pr", ""),
                    })
                    break

        # 检查 symptom
        symptom = pattern.get("symptom", "")
        if symptom and symptom.lower() in text:
            matches.append({
                "key": key,
                "symptom": symptom,
                "fix_action": pattern.get("fix_action", ""),
                "source_pr": pattern.get("source_pr", ""),
            })

    return matches


def check_success_patterns(
    title: str,
    description: str,
    repo: str,
    repo_root: Path,
    body: str = "",
) -> List[dict]:
    """检查 PR 是否符合成功模式

    P0 改进: 对含 Issue 关联语义的 factor，要求 body 匹配 fixes|closes|resolves #NNN
    阈值从 0.5 提高到 0.6
    """
    success_patterns = load_success_patterns(repo_root)
    matches = []

    # 合并标题、描述、body 进行检查
    text = f"{title} {description}".lower()
    full_text = f"{title} {description} {body}".lower()

    # P0: Issue 关联语义关键词 — 命中这些词的 factor 需要正则验证
    issue_semantic_keywords = {"fix", "fixes", "fixed", "close", "closes", "closed",
                                "resolve", "resolves", "resolved", "issue", "bug"}

    for key, pattern in success_patterns.items():
        # 检查 success_factors
        factors = pattern.get("success_factors", [])
        if isinstance(factors, list):
            match_count = 0
            for factor in factors:
                factor_keywords = set(re.findall(r'\w+', factor.lower()))

                # P0: 检查这个 factor 是否涉及 Issue 关联
                has_issue_semantic = bool(factor_keywords & issue_semantic_keywords)

                if has_issue_semantic:
                    # 这个 factor 涉及 Issue 关联，必须用正则验证 body 真正引用了 Issue
                    if body and check_issue_link(body):
                        match_count += 1
                    # 否则不计分（之前会因为 "fix" 子串匹配而误加分）
                else:
                    # 非 Issue 关联的 factor，用 full_text（含 body）匹配
                    if any(kw in full_text for kw in factor_keywords):
                        match_count += 1

            # 阈值 0.5（P0 的核心改进是 issue-linked 正则，不是阈值）
            if match_count >= len(factors) * 0.5:
                matches.append({
                    "key": key,
                    "description": pattern.get("description", ""),
                    "success_factors": factors,
                    "source_pr": pattern.get("source_pr", ""),
                })

    return matches


def predict_success_rate(
    title: str,
    description: str,
    repo: str,
    repo_root: Path,
    body: str = "",
    labels: Optional[List[str]] = None,
    author: str = "",
    star_count: int = 0,
    repo_merge_rate: float = 0.0,
) -> Tuple[float, str]:
    """预测 PR 成功率

    P0: 基线 0.45，阈值调整
    P1: 标签信号层
    P2: Bot PR 独立通道
    repo_merge_rate: 仓库历史 merge 率（0-1），用于动态基线
    """
    if labels is None:
        labels = []

    # 动态基线：如果有仓库 merge 率数据，用它来调整基线
    if repo_merge_rate > 0:
        # 基线 = 仓库 merge 率 * 0.7 + 默认基线 * 0.3（防止过拟合）
        dynamic_base = repo_merge_rate * 0.7 + BASE_RATE_HUMAN * 0.3
    else:
        dynamic_base = BASE_RATE_HUMAN

    # P2: Bot PR 走独立通道
    if author and is_bot_author(author):
        repo_size = get_repo_size(star_count) if star_count > 0 else "medium"
        base_rate = BOT_BASE_RATES.get(repo_size, 0.50)
        # Bot PR 也受标签影响（但幅度较小）
        label_adj = compute_label_score(labels) * 0.5  # 标签影响减半
        base_rate = max(0.0, min(1.0, base_rate + label_adj / 100))
        if base_rate >= THRESHOLD_HIGH:
            level = "高"
        elif base_rate >= THRESHOLD_MED:
            level = "中"
        else:
            level = "低"
        return base_rate, level

    # 人类 PR 评估
    anti_matches = check_anti_patterns(title, description, repo, repo_root, body=body)
    success_matches = check_success_patterns(title, description, repo, repo_root, body=body)

    # 基础成功率（动态基线）
    base_rate = dynamic_base

    # 反模式惩罚
    for match in anti_matches:
        key = match["key"]
        if "cosmetic" in key:
            base_rate -= 0.30
        elif "breaking" in key:
            base_rate -= 0.25
        elif "upstream" in key:
            base_rate -= 0.10
        elif "low-value" in key:
            base_rate -= 0.20
        elif "ai-generated" in key or "ai-policy" in key:
            base_rate -= 0.25
        elif "missing-issue" in key:
            base_rate -= 0.15
        elif "duplicate" in key:
            base_rate -= 0.20
        else:
            base_rate -= 0.15  # 通用反模式惩罚

    # 成功模式加成（封顶 +0.15，防止叠加过多）
    if success_matches:
        base_rate += min(0.15, len(success_matches) * 0.05)

    # P1: 标签信号
    label_adj = compute_label_score(labels)
    base_rate += label_adj / 100  # 标签分数按百分比影响

    # 限制在 0-1 之间
    base_rate = max(0.0, min(1.0, base_rate))

    # 生成预测说明
    if base_rate >= THRESHOLD_HIGH:
        level = "高"
    elif base_rate >= THRESHOLD_MED:
        level = "中"
    else:
        level = "低"

    return base_rate, level


def generate_suggestions(
    title: str,
    description: str,
    repo: str,
    repo_root: Path,
    body: str = "",
    labels: Optional[List[str]] = None,
    author: str = "",
) -> List[str]:
    """生成改进建议"""
    suggestions = []

    anti_matches = check_anti_patterns(title, description, repo, repo_root, body=body)
    success_matches = check_success_patterns(title, description, repo, repo_root, body=body)

    # 基于反模式的建议
    for match in anti_matches:
        suggestions.append(f"### 避免 {match['key']} 反模式\n")
        suggestions.append(f"**问题**: {match.get('symptom', '未知')}\n")
        suggestions.append(f"**建议**: {match.get('fix_action', '无')}\n")
        if match.get('source_pr'):
            suggestions.append(f"**历史案例**: {match['source_pr']}\n")
        suggestions.append("")

    # 基于成功模式的建议
    if success_matches:
        suggestions.append("### 参考成功模式\n")
        for match in success_matches:
            suggestions.append(f"- **{match['key']}**: {match.get('description', '')}\n")
            if match.get('success_factors'):
                suggestions.append("  - 成功因素:\n")
                for factor in match['success_factors'][:3]:
                    suggestions.append(f"    - {factor}\n")
        suggestions.append("")

    # P1: 标签相关建议
    if labels:
        label_score = compute_label_score(labels)
        if label_score < -10:
            suggestions.append("### ⚠️ 标签警告\n")
            negative_labels = [l for l in labels if compute_label_score([l]) < 0]
            suggestions.append(f"以下标签可能影响合并概率: {', '.join(negative_labels)}\n")
            suggestions.append("建议先解决标签标记的问题再提交 PR\n\n")

    # 通用建议
    suggestions.append("### 通用建议\n")
    suggestions.append("1. **先 Issue 后 PR**: 先在 Issue 中讨论方案\n")
    suggestions.append("2. **完整交付**: 代码 + 测试 + 文档\n")
    suggestions.append("3. **单一 commit**: 保持 PR 干净\n")
    suggestions.append("4. **DCO sign-off**: 使用 `git commit -s`\n")
    suggestions.append("")

    return suggestions


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
) -> dict:
    """评估 PR"""
    if labels is None:
        labels = []

    rate, level = predict_success_rate(
        title, description, repo, repo_root,
        body=body, labels=labels, author=author, star_count=star_count,
        repo_merge_rate=repo_merge_rate,
    )
    anti_matches = check_anti_patterns(title, description, repo, repo_root, body=body)
    success_matches = check_success_patterns(title, description, repo, repo_root, body=body)
    suggestions = generate_suggestions(
        title, description, repo, repo_root,
        body=body, labels=labels, author=author,
    )

    return {
        "title": title,
        "description": description,
        "repo": repo,
        "author": author,
        "labels": labels,
        "is_bot": is_bot_author(author) if author else False,
        "success_rate": rate,
        "success_level": level,
        "anti_patterns": anti_matches,
        "success_patterns": success_matches,
        "suggestions": suggestions,
    }


def suggest_pr(
    title: str,
    description: str,
    repo: str,
    repo_root: Path,
    body: str = "",
    labels: Optional[List[str]] = None,
    author: str = "",
) -> dict:
    """生成改进建议"""
    suggestions = generate_suggestions(
        title, description, repo, repo_root,
        body=body, labels=labels, author=author,
    )

    return {
        "title": title,
        "description": description,
        "repo": repo,
        "suggestions": suggestions,
    }
