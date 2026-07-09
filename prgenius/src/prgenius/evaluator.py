"""PR Evaluator — 基于反模式和成功模式评估 PR

提供 PR 评估、建议生成、成功率预测等功能。
"""
from __future__ import annotations
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


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


def check_anti_patterns(title: str, description: str, repo: str, repo_root: Path) -> List[dict]:
    """检查 PR 是否命中反模式"""
    anti_patterns = load_anti_patterns(repo_root)
    matches = []

    # 合并标题和描述进行检查
    text = f"{title} {description}".lower()

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


def check_success_patterns(title: str, description: str, repo: str, repo_root: Path) -> List[dict]:
    """检查 PR 是否符合成功模式"""
    success_patterns = load_success_patterns(repo_root)
    matches = []

    # 合并标题和描述进行检查
    text = f"{title} {description}".lower()

    for key, pattern in success_patterns.items():
        # 检查 success_factors
        factors = pattern.get("success_factors", [])
        if isinstance(factors, list):
            match_count = 0
            for factor in factors:
                # 简单的关键词匹配
                factor_keywords = re.findall(r'\w+', factor.lower())
                if any(kw in text for kw in factor_keywords):
                    match_count += 1

            # 如果匹配了大部分因素，认为符合模式
            if match_count >= len(factors) * 0.5:
                matches.append({
                    "key": key,
                    "description": pattern.get("description", ""),
                    "success_factors": factors,
                    "source_pr": pattern.get("source_pr", ""),
                })

    return matches


def predict_success_rate(title: str, description: str, repo: str, repo_root: Path) -> Tuple[float, str]:
    """预测 PR 成功率"""
    anti_matches = check_anti_patterns(title, description, repo, repo_root)
    success_matches = check_success_patterns(title, description, repo, repo_root)

    # 基础成功率
    base_rate = 0.5

    # 反模式惩罚
    for match in anti_matches:
        # 根据反模式类型调整惩罚
        key = match["key"]
        if "cosmetic" in key:
            base_rate -= 0.3
        elif "breaking" in key:
            base_rate -= 0.25
        elif "upstream" in key:
            base_rate -= 0.1  # 这个其实是有价值的
        elif "low-value" in key:
            base_rate -= 0.2

    # 成功模式加成
    for match in success_matches:
        base_rate += 0.15

    # 限制在 0-1 之间
    base_rate = max(0.0, min(1.0, base_rate))

    # 生成预测说明
    if base_rate >= 0.7:
        level = "高"
    elif base_rate >= 0.4:
        level = "中"
    else:
        level = "低"

    return base_rate, level


def generate_suggestions(title: str, description: str, repo: str, repo_root: Path) -> List[str]:
    """生成改进建议"""
    suggestions = []

    anti_matches = check_anti_patterns(title, description, repo, repo_root)
    success_matches = check_success_patterns(title, description, repo, repo_root)

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

    # 通用建议
    suggestions.append("### 通用建议\n")
    suggestions.append("1. **先 Issue 后 PR**: 先在 Issue 中讨论方案\n")
    suggestions.append("2. **完整交付**: 代码 + 测试 + 文档\n")
    suggestions.append("3. **单一 commit**: 保持 PR 干净\n")
    suggestions.append("4. **DCO sign-off**: 使用 `git commit -s`\n")
    suggestions.append("")

    return suggestions


def eval_pr(title: str, description: str, repo: str, repo_root: Path) -> dict:
    """评估 PR"""
    rate, level = predict_success_rate(title, description, repo, repo_root)
    anti_matches = check_anti_patterns(title, description, repo, repo_root)
    success_matches = check_success_patterns(title, description, repo, repo_root)
    suggestions = generate_suggestions(title, description, repo, repo_root)

    return {
        "title": title,
        "description": description,
        "repo": repo,
        "success_rate": rate,
        "success_level": level,
        "anti_patterns": anti_matches,
        "success_patterns": success_matches,
        "suggestions": suggestions,
    }


def suggest_pr(title: str, description: str, repo: str, repo_root: Path) -> dict:
    """生成改进建议"""
    suggestions = generate_suggestions(title, description, repo, repo_root)

    return {
        "title": title,
        "description": description,
        "repo": repo,
        "suggestions": suggestions,
    }
