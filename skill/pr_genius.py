#!/usr/bin/env python3
"""
PR Genius — PR 评估和建议工具 (standalone skill version)

基于历史反模式和成功模式，评估 PR 的成功率，提供改进建议。

v0.3.0: P0 issue-linked-fix 正则匹配, P1 标签信号层, P2 Bot PR 独立通道

Usage:
    python3 pr_genius.py eval "feat: add error handler" --repo vitejs/vite
    python3 pr_genius.py eval "fix: update deps" --repo langchain-ai/langchain --author "dependabot[bot]" --labels "dependencies"
    python3 pr_genius.py suggest "feat: add error handler" --repo vitejs/vite
    python3 pr_genius.py describe "feat: add error handler" --repo vitejs/vite
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 知识库路径
KNOWLEDGE_BASE = Path(__file__).parent.parent

# ============================================================
# 常量
# ============================================================

# P1: 标签信号层
LABEL_SIGNALS: Dict[str, float] = {
    "ai-policy-violation": -20,
    "invalid": -20,
    "wontfix": -20,
    "spam": -25,
    "duplicate": -25,
    "missing-issue-link": -10,
    "needs-information": -10,
    "awaiting-response": -5,
    "stale": -10,
    "new-contributor": -3,
    "first-time contributor": -3,
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

# Issue 关联正则
ISSUE_LINK_RE = re.compile(
    r"(?:fix(?:es|ed)?|close[sd]?|resolve[sd]?)\s+#\d+",
    re.IGNORECASE,
)

# 基线和阈值
BASE_RATE_HUMAN = 0.45
BOT_BASE_RATES = {"small": 0.70, "medium": 0.50, "large": 0.30}
THRESHOLD_HIGH = 0.60
THRESHOLD_MED = 0.35

# P3: author_association 加权
ASSOCIATION_BOOST = {
    "OWNER": 0.40,
    "MEMBER": 0.25,
    "COLLABORATOR": 0.20,
    "CONTRIBUTOR": 0.05,
    "NONE": 0.0,
}


# ============================================================
# 辅助函数
# ============================================================

def is_bot_author(author: str) -> bool:
    return author.lower().strip() in {a.lower() for a in BOT_AUTHORS}


def get_repo_size(star_count: int) -> str:
    if star_count < 5000:
        return "small"
    elif star_count < 50000:
        return "medium"
    else:
        return "large"


def check_issue_link(body: str) -> bool:
    return bool(ISSUE_LINK_RE.search(body))


def compute_label_score(labels: List[str]) -> float:
    score = 0.0
    for label in labels:
        label_lower = label.lower().strip()
        if label_lower in LABEL_SIGNALS:
            score += LABEL_SIGNALS[label_lower]
        else:
            for key, val in LABEL_SIGNALS.items():
                if key in label_lower:
                    score += val
                    break
    return score


# ============================================================
# 模式加载
# ============================================================

def _parse_frontmatter(content: str) -> Optional[dict]:
    """解析 Markdown frontmatter"""
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None

    try:
        fm = {}
        current_key = None
        current_value = []
        in_list = False

        for line in match.group(1).strip().split("\n"):
            if re.match(r'^[a-zA-Z_]+:', line) and not line.startswith('  '):
                if current_key:
                    if in_list:
                        fm[current_key] = current_value
                    else:
                        fm[current_key] = ' '.join(current_value).strip()

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
                item = line[4:].strip().strip('"')
                current_value.append(item)

            elif line.startswith('  ') and not in_list:
                current_value.append(line.strip())

        if current_key:
            if in_list:
                fm[current_key] = current_value
            else:
                fm[current_key] = ' '.join(current_value).strip()

        return fm
    except Exception:
        return None


def load_anti_patterns() -> Dict[str, dict]:
    patterns = {}
    anti_patterns_dir = KNOWLEDGE_BASE / "anti-patterns"
    if not anti_patterns_dir.exists():
        return patterns

    for file in anti_patterns_dir.glob("*.md"):
        if file.name == "README.md":
            continue
        content = file.read_text(encoding="utf-8")
        fm = _parse_frontmatter(content)
        if fm:
            patterns[file.stem] = fm

    return patterns


def load_success_patterns() -> Dict[str, dict]:
    patterns = {}
    success_patterns_dir = KNOWLEDGE_BASE / "success-patterns"
    if not success_patterns_dir.exists():
        return patterns

    for file in success_patterns_dir.glob("*.md"):
        if file.name == "README.md":
            continue
        content = file.read_text(encoding="utf-8")
        fm = _parse_frontmatter(content)
        if fm:
            patterns[file.stem] = fm

    return patterns


def load_repo_config(repo: str) -> Optional[dict]:
    org, name = repo.split("/")
    repo_dir = KNOWLEDGE_BASE / f"{org}-{name}"
    if not repo_dir.exists():
        return None

    index_file = repo_dir / "index.md"
    if not index_file.exists():
        return None

    content = index_file.read_text(encoding="utf-8")
    return _parse_frontmatter(content)


# ============================================================
# 评估逻辑
# ============================================================

def check_anti_patterns(title: str, description: str, repo: str, body: str = "") -> List[dict]:
    anti_patterns = load_anti_patterns()
    matches = []
    text = f"{title} {description} {body}".lower()

    for key, pattern in anti_patterns.items():
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
    title: str, description: str, repo: str, body: str = "",
) -> List[dict]:
    """P0: 对含 Issue 关联语义的 factor，要求 body 匹配 fixes|closes|resolves #NNN"""
    success_patterns = load_success_patterns()
    matches = []
    text = f"{title} {description}".lower()
    full_text = f"{title} {description} {body}".lower()

    issue_semantic_keywords = {
        "fix", "fixes", "fixed", "close", "closes", "closed",
        "resolve", "resolves", "resolved", "issue", "bug",
    }

    for key, pattern in success_patterns.items():
        factors = pattern.get("success_factors", [])
        if isinstance(factors, list):
            match_count = 0
            for factor in factors:
                factor_keywords = set(re.findall(r'\w+', factor.lower()))
                has_issue_semantic = bool(factor_keywords & issue_semantic_keywords)

                if has_issue_semantic:
                    if body and check_issue_link(body):
                        match_count += 1
                else:
                    if any(kw in full_text for kw in factor_keywords):
                        match_count += 1

            # 阈值 0.5
            if match_count >= len(factors) * 0.5:
                matches.append({
                    "key": key,
                    "description": pattern.get("description", ""),
                    "success_factors": factors,
                    "source_pr": pattern.get("source_pr", ""),
                })

    return matches


def predict_success_rate(
    title: str, description: str, repo: str,
    body: str = "", labels: Optional[List[str]] = None,
    author: str = "", star_count: int = 0,
    repo_merge_rate: float = 0.0,
    author_association: str = "NONE",
) -> Tuple[float, str]:
    if labels is None:
        labels = []

    # 动态基线
    if repo_merge_rate > 0:
        dynamic_base = repo_merge_rate * 0.7 + BASE_RATE_HUMAN * 0.3
    else:
        dynamic_base = BASE_RATE_HUMAN

    # P2: Bot PR 独立通道
    if author and is_bot_author(author):
        repo_size = get_repo_size(star_count) if star_count > 0 else "medium"
        base_rate = BOT_BASE_RATES.get(repo_size, 0.50)
        label_adj = compute_label_score(labels) * 0.5
        base_rate = max(0.0, min(1.0, base_rate + label_adj / 100))
        if base_rate >= THRESHOLD_HIGH:
            level = "高"
        elif base_rate >= THRESHOLD_MED:
            level = "中"
        else:
            level = "低"
        return base_rate, level

    # 人类 PR
    anti_matches = check_anti_patterns(title, description, repo, body=body)
    success_matches = check_success_patterns(title, description, repo, body=body)

    base_rate = dynamic_base

    # P3: author_association 加权
    assoc_upper = author_association.upper().strip()
    base_rate += ASSOCIATION_BOOST.get(assoc_upper, 0.0)

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
            base_rate -= 0.15

    # 成功模式加成（封顶 +0.12，P6 降权）
    if success_matches:
        base_rate += min(0.12, len(success_matches) * 0.03)

    # P1: 标签信号
    label_adj = compute_label_score(labels)
    base_rate += label_adj / 100

    base_rate = max(0.0, min(1.0, base_rate))

    if base_rate >= THRESHOLD_HIGH:
        level = "高"
    elif base_rate >= THRESHOLD_MED:
        level = "中"
    else:
        level = "低"

    return base_rate, level


def generate_suggestions(
    title: str, description: str, repo: str,
    body: str = "", labels: Optional[List[str]] = None,
    author: str = "",
) -> List[str]:
    suggestions = []
    anti_matches = check_anti_patterns(title, description, repo, body=body)
    success_matches = check_success_patterns(title, description, repo, body=body)

    for match in anti_matches:
        suggestions.append(f"### 避免 {match['key']} 反模式\n")
        suggestions.append(f"**问题**: {match.get('symptom', '未知')}\n")
        suggestions.append(f"**建议**: {match.get('fix_action', '无')}\n")
        if match.get('source_pr'):
            suggestions.append(f"**历史案例**: {match['source_pr']}\n")
        suggestions.append("")

    if success_matches:
        suggestions.append("### 参考成功模式\n")
        for match in success_matches:
            suggestions.append(f"- **{match['key']}**: {match.get('description', '')}\n")
            if match.get('success_factors'):
                suggestions.append("  - 成功因素:\n")
                for factor in match['success_factors'][:3]:
                    suggestions.append(f"    - {factor}\n")
        suggestions.append("")

    if labels:
        label_score = compute_label_score(labels)
        if label_score < -10:
            suggestions.append("### ⚠️ 标签警告\n")
            negative_labels = [l for l in labels if compute_label_score([l]) < 0]
            suggestions.append(f"以下标签可能影响合并概率: {', '.join(negative_labels)}\n")
            suggestions.append("建议先解决标签标记的问题再提交 PR\n\n")

    suggestions.append("### 通用建议\n")
    suggestions.append("1. **先 Issue 后 PR**: 先在 Issue 中讨论方案\n")
    suggestions.append("2. **完整交付**: 代码 + 测试 + 文档\n")
    suggestions.append("3. **单一 commit**: 保持 PR 干净\n")
    suggestions.append("4. **DCO sign-off**: 使用 `git commit -s`\n")
    suggestions.append("")

    return suggestions


def eval_pr(
    title: str, description: str, repo: str,
    body: str = "", labels: Optional[List[str]] = None,
    author: str = "", star_count: int = 0,
    repo_merge_rate: float = 0.0,
    author_association: str = "NONE",
) -> str:
    if labels is None:
        labels = []

    rate, level = predict_success_rate(
        title, description, repo,
        body=body, labels=labels, author=author, star_count=star_count,
        repo_merge_rate=repo_merge_rate, author_association=author_association,
    )
    anti_matches = check_anti_patterns(title, description, repo, body=body)
    success_matches = check_success_patterns(title, description, repo, body=body)

    output = []
    output.append("## PR 评估结果\n")

    if author and is_bot_author(author):
        output.append("🤖 **Bot PR** — 走独立评估通道\n\n")

    output.append(f"### 成功率预测: {rate:.0%} ({level})\n")

    if labels:
        label_score = compute_label_score(labels)
        if label_score != 0:
            signal = "正面" if label_score > 0 else "负面"
            output.append(f"### 标签信号: {signal} ({label_score:+.0f} 分)\n")
            output.append(f"标签: {', '.join(labels)}\n\n")

    if anti_matches:
        output.append("### 反模式命中\n")
        for match in anti_matches:
            output.append(f"- ⚠️ **{match['key']}**: {match.get('symptom', '未知')}\n")
            if match.get('fix_action'):
                output.append(f"  - 建议: {match['fix_action']}\n")
            if match.get('source_pr'):
                output.append(f"  - 历史案例: {match['source_pr']}\n")
        output.append("")
    else:
        output.append("### 反模式命中\n")
        output.append("- ✅ 未命中任何反模式\n\n")

    if success_matches:
        output.append("### 成功模式匹配\n")
        for match in success_matches:
            output.append(f"- ✅ **{match['key']}**: {match.get('description', '')}\n")
        output.append("")
    else:
        output.append("### 成功模式匹配\n")
        output.append("- ❌ 未匹配任何成功模式\n\n")

    suggestions = generate_suggestions(
        title, description, repo, body=body, labels=labels, author=author,
    )
    if suggestions:
        output.append("### 改进建议\n")
        output.extend(suggestions)

    return "".join(output)


def suggest_pr(
    title: str, description: str, repo: str,
    body: str = "", labels: Optional[List[str]] = None,
    author: str = "",
) -> str:
    suggestions = generate_suggestions(
        title, description, repo, body=body, labels=labels, author=author,
    )
    output = []
    output.append("## 改进建议\n")
    output.extend(suggestions)
    return "".join(output)


def describe_pr(title: str, description: str, repo: str, issue: str = None) -> str:
    output = []
    output.append("## PR 描述\n")
    output.append("### 标题\n")
    output.append(f"{title}\n\n")
    output.append("### 描述\n")
    output.append(f"{description}\n\n")

    if issue:
        output.append("### 关联 Issue\n")
        output.append(f"Closes {issue}\n\n")

    output.append("### 验收标准\n")
    output.append("- [ ] 代码实现\n")
    output.append("- [ ] 测试覆盖\n")
    output.append("- [ ] 文档更新\n")
    output.append("- [ ] DCO sign-off\n")
    output.append("- [ ] CI 通过\n")

    return "".join(output)


def main():
    parser = argparse.ArgumentParser(description="PR Genius — PR 评估和建议工具")
    subparsers = parser.add_subparsers(dest="command", help="命令")

    # eval 命令
    eval_parser = subparsers.add_parser("eval", help="评估 PR")
    eval_parser.add_argument("title", help="PR 标题")
    eval_parser.add_argument("--description", "-d", default="", help="PR 描述")
    eval_parser.add_argument("--body", "-b", default="", help="PR body")
    eval_parser.add_argument("--repo", "-r", required=True, help="目标仓库 (org/repo)")
    eval_parser.add_argument("--labels", "-l", nargs="*", default=[], help="PR 标签")
    eval_parser.add_argument("--author", "-a", default="", help="PR 作者")
    eval_parser.add_argument("--star-count", type=int, default=0, help="仓库 star 数")
    eval_parser.add_argument("--repo-merge-rate", type=float, default=0.0, help="仓库历史 merge 率 (0-1)")
    eval_parser.add_argument("--author-association", default="NONE", help="作者身份 (NONE/CONTRIBUTOR/COLLABORATOR/MEMBER/OWNER)")

    # suggest 命令
    suggest_parser = subparsers.add_parser("suggest", help="获取改进建议")
    suggest_parser.add_argument("title", help="PR 标题")
    suggest_parser.add_argument("--description", "-d", default="", help="PR 描述")
    suggest_parser.add_argument("--body", "-b", default="", help="PR body")
    suggest_parser.add_argument("--repo", "-r", required=True, help="目标仓库 (org/repo)")
    suggest_parser.add_argument("--labels", "-l", nargs="*", default=[], help="PR 标签")
    suggest_parser.add_argument("--author", "-a", default="", help="PR 作者")
    suggest_parser.add_argument("--type", "-t", choices=["all", "success", "anti-pattern"],
                               default="all", help="建议类型")

    # describe 命令
    describe_parser = subparsers.add_parser("describe", help="生成 PR 描述")
    describe_parser.add_argument("title", help="PR 标题")
    describe_parser.add_argument("--description", "-d", default="", help="PR 描述")
    describe_parser.add_argument("--repo", "-r", required=True, help="目标仓库 (org/repo)")
    describe_parser.add_argument("--issue", "-i", help="关联 Issue (org/repo#number)")

    args = parser.parse_args()

    if args.command == "eval":
        result = eval_pr(
            args.title, args.description, args.repo,
            body=args.body, labels=args.labels, author=args.author,
            star_count=args.star_count,
            repo_merge_rate=args.repo_merge_rate,
            author_association=args.author_association,
        )
        print(result)
    elif args.command == "suggest":
        result = suggest_pr(
            args.title, args.description, args.repo,
            body=args.body, labels=args.labels, author=args.author,
        )
        print(result)
    elif args.command == "describe":
        result = describe_pr(args.title, args.description, args.repo, args.issue)
        print(result)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
