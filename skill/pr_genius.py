#!/usr/bin/env python3
"""
PR Genius — 提交前改进顾问 (standalone skill version)

v1.0.0: 从"合并概率预测器"转为"提交前改进顾问"

Usage:
    python3 pr_genius.py analyze "feat: add feature" --repo org/repo --body "..."
    python3 pr_genius.py analyze "feat: add feature" --repo org/repo --format json
    python3 pr_genius.py eval "feat: add feature" --repo org/repo  (兼容旧命令)
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

KNOWLEDGE_BASE = Path(__file__).parent.parent

# ============================================================
# 常量
# ============================================================

LABEL_SIGNALS: Dict[str, str] = {
    "ai-policy-violation": "negative", "invalid": "negative", "wontfix": "negative",
    "spam": "negative", "duplicate": "negative", "missing-issue-link": "negative",
    "needs-information": "negative", "awaiting-response": "negative", "stale": "negative",
    "new-contributor": "neutral", "first-time contributor": "neutral",
    "help wanted": "positive", "good first issue": "positive", "enhancement": "positive",
    "bug": "positive", "documentation": "positive", "dependencies": "positive",
}

BOT_AUTHORS = {
    "dependabot[bot]", "pre-commit-ci[bot]", "renovate[bot]",
    "github-actions[bot]", "mergify[bot]", "codecov[bot]",
    "snyk-bot", "greenkeeper[bot]",
}

ISSUE_LINK_RE = re.compile(
    r"(?:fix(?:es|ed)?|close[sd]?|resolve[sd]?)\s+#\d+", re.IGNORECASE,
)

ASSOCIATION_LABELS = {
    "OWNER": "仓库所有者", "MEMBER": "组织成员", "COLLABORATOR": "协作者",
    "CONTRIBUTOR": "历史贡献者", "NONE": "首次贡献者",
}

ANTI_PATTERN_SEVERITY = {
    "ai-generated-content": "critical", "spam": "critical",
    "cosmetic-no-user-pain": "high", "breaking-change-no-compat": "high",
    "missing-issue-reference": "high", "duplicate-pr-same-author": "high",
    "low-value-contribution": "medium", "upstream-already-implementing": "medium",
    "fork-main-sync-upstream": "low",
}


# ============================================================
# 辅助函数
# ============================================================

def is_bot_author(author: str) -> bool:
    """判断是否为 Bot 作者 (白名单 + [bot] 后缀规则)"""
    login = author.lower().strip()
    if login in {a.lower() for a in BOT_AUTHORS}:
        return True
    if login.endswith("[bot]"):
        return True
    return False


def get_repo_size(star_count: int) -> str:
    if star_count < 5000: return "small"
    elif star_count < 50000: return "medium"
    else: return "large"


def check_issue_link(body: str) -> bool:
    return bool(ISSUE_LINK_RE.search(body))


def _check_requires_dco(repo: str) -> Optional[bool]:
    """检查仓库是否要求 DCO (True/False/None=未知)"""
    target_folder = repo.replace("/", "-").lower()
    index_file = KNOWLEDGE_BASE / target_folder / "index.md"
    if not index_file.exists():
        return None
    try:
        content = index_file.read_text(encoding="utf-8")
        match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if not match:
            return None
        for line in match.group(1).split("\n"):
            line = line.strip()
            if line.startswith("requires_dco:") or line.startswith("require_signed_off:"):
                value = line.split(":", 1)[1].strip().lower()
                if value in ("true", "yes"): return True
                elif value in ("false", "no"): return False
        return None
    except Exception:
        return None


def _check_require_issue_first(repo: str) -> Optional[bool]:
    """检查仓库是否要求先 Issue 后 PR (True/False/None=未知)"""
    target_folder = repo.replace("/", "-").lower()
    index_file = KNOWLEDGE_BASE / target_folder / "index.md"
    if not index_file.exists():
        return None
    try:
        content = index_file.read_text(encoding="utf-8")
        match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if not match:
            return None
        for line in match.group(1).split("\n"):
            line = line.strip()
            if line.startswith("require_issue_first:"):
                value = line.split(":", 1)[1].strip().lower()
                if value in ("true", "yes"): return True
                elif value in ("false", "no"): return False
        return None
    except Exception:
        return None


def _parse_label(label: str) -> Tuple[str, str]:
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

def _parse_frontmatter(content: str) -> Optional[dict]:
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
                    fm[current_key] = current_value if in_list else ' '.join(current_value).strip()
                key, value = line.split(":", 1)
                current_key = key.strip()
                value = value.strip()
                if value == '':
                    current_value = []; in_list = True
                elif value.startswith('['):
                    current_value = [v.strip().strip('"') for v in value[1:-1].split(",")]; in_list = False
                else:
                    current_value = [value]; in_list = False
            elif line.startswith('  - ') and in_list:
                current_value.append(line[4:].strip().strip('"'))
            elif line.startswith('  ') and not in_list:
                current_value.append(line.strip())
        if current_key:
            fm[current_key] = current_value if in_list else ' '.join(current_value).strip()
        return fm
    except Exception:
        return None


def load_anti_patterns() -> Dict[str, dict]:
    patterns = {}
    d = KNOWLEDGE_BASE / "anti-patterns"
    if not d.exists(): return patterns
    for f in d.glob("*.md"):
        if f.name == "README.md": continue
        fm = _parse_frontmatter(f.read_text(encoding="utf-8"))
        if fm: patterns[f.stem] = fm
    return patterns


def load_success_patterns() -> Dict[str, dict]:
    patterns = {}
    d = KNOWLEDGE_BASE / "success-patterns"
    if not d.exists(): return patterns
    for f in d.glob("*.md"):
        if f.name == "README.md": continue
        fm = _parse_frontmatter(f.read_text(encoding="utf-8"))
        if fm: patterns[f.stem] = fm
    return patterns


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


# ============================================================
# 核心: analyze_pr
# ============================================================

def analyze_pr(
    title: str, description: str, repo: str,
    body: str = "", labels: Optional[List[str]] = None,
    author: str = "", star_count: int = 0,
    repo_merge_rate: float = 0.0, author_association: str = "NONE",
) -> dict:
    if labels is None: labels = []

    signals_pos, signals_neg, signals_neu = [], [], []
    checklist = []

    # 1. Issue 关联 (跳过 Bot, 仓库感知)
    is_bot = is_bot_author(author)
    require_issue_first = _check_require_issue_first(repo)

    if not is_bot:
        has_issue_link = check_issue_link(body) if body else False
        if has_issue_link:
            signals_pos.append({"key": "issue_linked", "description": "PR body 包含 Issue 关联 (fixes/closes/resolves #NNN)"})
        else:
            if require_issue_first is True:
                signals_neg.append({"key": "no_issue_link", "description": "PR body 缺少 Issue 关联（该仓库要求先 Issue 后 PR）", "severity": "high"})
                checklist.append({"action": "add_issue_link", "priority": "P0", "done": False,
                                  "hint": "在 body 中添加 `Fixes #NNN` 或 `Closes #NNN`"})
            elif require_issue_first is None:
                signals_neu.append({"key": "no_issue_link_hint", "description": "PR body 未包含 Issue 关联，建议确认是否需要"})
                checklist.append({"action": "add_issue_link", "priority": "P2", "done": False,
                                  "hint": "建议在 body 中添加 Issue 关联（如果仓库要求）"})
            # require_issue_first = False → 不提示

    # 2. 反模式
    anti_matches = check_anti_patterns(title, description, repo, body=body)
    for match in anti_matches:
        key = match["key"]
        severity = ANTI_PATTERN_SEVERITY.get(key, "medium")
        signals_neg.append({
            "key": key, "description": match.get("symptom", ""), "severity": severity,
            "fix_action": match.get("fix_action", ""), "source_pr": match.get("source_pr", ""),
        })
        if match.get("fix_action"):
            checklist.append({"action": f"fix_{key}", "priority": "P0" if severity in ("critical", "high") else "P1",
                              "done": False, "hint": match["fix_action"]})

    # 3. 标签
    neg_labels, pos_labels = [], []
    for label in labels:
        _, polarity = _parse_label(label)
        if polarity == "negative": neg_labels.append(label)
        elif polarity == "positive": pos_labels.append(label)
    if neg_labels:
        signals_neg.append({"key": "negative_labels", "description": f"PR 带有负面标签: {', '.join(neg_labels)}", "severity": "high"})
        checklist.append({"action": "resolve_labels", "priority": "P0", "done": False,
                          "hint": "先解决标签标记的问题再提交"})
    if pos_labels:
        signals_pos.append({"key": "positive_labels", "description": f"PR 带有正面标签: {', '.join(pos_labels)}"})

    # 4. 作者身份
    assoc_upper = author_association.upper().strip()
    if is_bot:
        signals_neu.append({"key": "bot_author", "description": f"Bot PR ({author})"})
    elif assoc_upper == "OWNER":
        signals_pos.append({"key": "owner_author", "description": "仓库所有者提交"})
    elif assoc_upper in ("MEMBER", "COLLABORATOR"):
        signals_pos.append({"key": "insider_author", "description": f"{ASSOCIATION_LABELS.get(assoc_upper)}，有写入权限"})
    elif assoc_upper == "CONTRIBUTOR":
        signals_pos.append({"key": "returning_contributor", "description": "历史贡献者"})
    elif assoc_upper == "NONE":
        if star_count > 20000:
            signals_neg.append({"key": "first_contributor_large_repo",
                                "description": f"首次在大仓 ({star_count:,}⭐) 提 PR", "severity": "medium"})
            checklist.append({"action": "build_trust", "priority": "P1", "done": False,
                              "hint": "先在 Issue 中参与讨论，建立维护者信任"})
        else:
            signals_neu.append({"key": "first_contributor", "description": "首次贡献者"})

    # 5. 仓库上下文
    repo_context = {}
    if star_count > 0:
        repo_context["star_count"] = star_count
        repo_context["repo_size"] = get_repo_size(star_count)
    if repo_merge_rate > 0:
        repo_context["merge_rate"] = repo_merge_rate
        if repo_merge_rate < 0.3:
            signals_neu.append({"key": "strict_repo", "description": f"该仓库 merge 率较低 ({repo_merge_rate:.0%})，审查严格"})
        elif repo_merge_rate > 0.8:
            signals_pos.append({"key": "lenient_repo", "description": f"该仓库 merge 率较高 ({repo_merge_rate:.0%})"})

    # 6. 通用清单
    if not is_bot:
        checklist.append({"action": "ci_passing", "priority": "P1", "done": False, "hint": "确认 CI 全部通过"})
        # DCO: 仓库感知
        requires_dco = _check_requires_dco(repo)
        if requires_dco is True:
            checklist.append({"action": "dco_signoff", "priority": "P1", "done": False, "hint": "使用 `git commit -s` 添加 DCO sign-off"})
        elif requires_dco is None:
            checklist.append({"action": "dco_signoff", "priority": "P2", "done": False, "hint": "确认是否需要 DCO sign-off (`git commit -s`)"})

    # 7. 计算 tier
    neg_critical = sum(1 for s in signals_neg if s.get("severity") in ("critical", "high"))
    neg_medium = sum(1 for s in signals_neg if s.get("severity") == "medium")
    pos_count = len(signals_pos)

    if neg_critical >= 1 or neg_medium >= 2 or (neg_medium >= 1 and pos_count == 0):
        tier = "high_risk"
    elif neg_medium >= 1 or pos_count == 0:
        tier = "medium_risk"
    elif pos_count >= 2 and neg_critical == 0:
        tier = "low_risk"
    else:
        tier = "medium_risk"

    return {
        "repo": repo, "title": title, "tier": tier,
        "signals": {"positive": signals_pos, "negative": signals_neg, "neutral": signals_neu},
        "checklist": checklist,
        "anti_patterns_hit": [m["key"] for m in anti_matches],
        "repo_context": repo_context,
    }


# ============================================================
# 兼容: eval_pr
# ============================================================

def eval_pr(
    title: str, description: str, repo: str,
    body: str = "", labels: Optional[List[str]] = None,
    author: str = "", star_count: int = 0,
    repo_merge_rate: float = 0.0, author_association: str = "NONE",
) -> dict:
    analysis = analyze_pr(
        title, description, repo, body=body, labels=labels, author=author,
        star_count=star_count, repo_merge_rate=repo_merge_rate,
        author_association=author_association,
    )
    tier_map = {"low_risk": "低风险", "medium_risk": "中风险", "high_risk": "高风险"}
    return {
        "title": title, "repo": repo, "author": author, "labels": labels,
        "is_bot": is_bot_author(author) if author else False,
        "tier": tier_map.get(analysis["tier"], analysis["tier"]),
        "tier_raw": analysis["tier"], "analysis": analysis,
    }


# ============================================================
# CLI
# ============================================================

TIER_ICONS = {"low_risk": "🟢", "medium_risk": "🟡", "high_risk": "🔴"}
TIER_LABELS = {"low_risk": "低风险", "medium_risk": "中风险", "high_risk": "高风险"}


def _print_analysis(result: dict):
    tier = result["tier"]
    icon = TIER_ICONS.get(tier, "⚪")
    label = TIER_LABELS.get(tier, tier)
    signals = result["signals"]

    print(f"## PR 分析: {result['repo']}\n")
    print(f"**{icon} 综合评估: {label}** ({len(signals['positive'])} 正面 / {len(signals['negative'])} 负面)\n")

    if signals["negative"]:
        print("### ⚠️ 需要改进\n")
        for i, s in enumerate(signals["negative"], 1):
            sev = s.get("severity", "")
            sev_icon = {"critical": "🚨", "high": "⚠️", "medium": "📋"}.get(sev, "•")
            print(f"{i}. {sev_icon} **{s['description']}**")
            if s.get("fix_action"): print(f"   → {s['fix_action']}")
            if s.get("source_pr"): print(f"   (历史案例: {s['source_pr']})")
        print()

    if signals["positive"]:
        print("### ✅ 已具备\n")
        for s in signals["positive"]: print(f"- {s['description']}")
        print()

    if signals["neutral"]:
        print("### ℹ️ 参考信息\n")
        for s in signals["neutral"]: print(f"- {s['description']}")
        print()

    if result["checklist"]:
        print("### 📋 提交前清单\n")
        for item in result["checklist"]:
            mark = "✅" if item["done"] else "☐"
            print(f"- [{mark}] **[{item['priority']}]** {item['hint']}")
        print()

    ctx = result.get("repo_context", {})
    if ctx:
        parts = []
        if "star_count" in ctx: parts.append(f"{ctx['star_count']:,}⭐")
        if "repo_size" in ctx: parts.append(ctx["repo_size"])
        if "merge_rate" in ctx: parts.append(f"merge率 {ctx['merge_rate']:.0%}")
        if parts: print(f"*仓库: {' | '.join(parts)}*\n")


def main():
    parser = argparse.ArgumentParser(description="PR Genius — 提交前改进顾问")
    subparsers = parser.add_subparsers(dest="command", help="命令")

    # analyze
    ap = subparsers.add_parser("analyze", help="分析 PR 并生成改进建议")
    ap.add_argument("title")
    ap.add_argument("--description", "-d", default="")
    ap.add_argument("--body", "-b", default="")
    ap.add_argument("--repo", "-r", required=True)
    ap.add_argument("--labels", "-l", nargs="*", default=[])
    ap.add_argument("--author", "-a", default="")
    ap.add_argument("--star-count", type=int, default=0)
    ap.add_argument("--repo-merge-rate", type=float, default=0.0)
    ap.add_argument("--author-association", default="NONE")
    ap.add_argument("--format", "-f", choices=["text", "json"], default="text")

    # eval (兼容)
    ep = subparsers.add_parser("eval", help="评估 PR (降级为三档)")
    ep.add_argument("title")
    ep.add_argument("--description", "-d", default="")
    ep.add_argument("--body", "-b", default="")
    ep.add_argument("--repo", "-r", required=True)
    ep.add_argument("--labels", "-l", nargs="*", default=[])
    ep.add_argument("--author", "-a", default="")
    ep.add_argument("--star-count", type=int, default=0)
    ep.add_argument("--repo-merge-rate", type=float, default=0.0)
    ep.add_argument("--author-association", default="NONE")

    # coach (Agent PR Dojo)
    ch = subparsers.add_parser("coach", help="Agent PR Dojo — exit 0=pass, exit 1=fail")
    ch.add_argument("title")
    ch.add_argument("--description", "-d", default="")
    ch.add_argument("--body", "-b", default="")
    ch.add_argument("--repo", "-r", required=True)
    ch.add_argument("--labels", "-l", nargs="*", default=[])
    ch.add_argument("--author", "-a", default="")
    ch.add_argument("--star-count", type=int, default=0)
    ch.add_argument("--repo-merge-rate", type=float, default=0.0)
    ch.add_argument("--author-association", default="NONE")
    ch.add_argument("--format", "-f", choices=["text", "json"], default="text")

    # describe
    dp = subparsers.add_parser("describe", help="生成 PR 描述模板")
    dp.add_argument("title")
    dp.add_argument("--description", "-d", default="")
    dp.add_argument("--repo", "-r", required=True)
    dp.add_argument("--issue", "-i")

    args = parser.parse_args()

    if args.command == "analyze":
        result = analyze_pr(
            args.title, args.description, args.repo,
            body=args.body, labels=args.labels, author=args.author,
            star_count=args.star_count, repo_merge_rate=args.repo_merge_rate,
            author_association=args.author_association,
        )
        if args.format == "json":
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            _print_analysis(result)

    elif args.command == "eval":
        result = eval_pr(
            args.title, args.description, args.repo,
            body=args.body, labels=args.labels, author=args.author,
            star_count=args.star_count, repo_merge_rate=args.repo_merge_rate,
            author_association=args.author_association,
        )
        tier = result["tier"]
        icon = TIER_ICONS.get(result.get("tier_raw", ""), "⚪")
        print(f"**{icon} 风险等级: {tier}**\n")
        analysis = result["analysis"]
        if analysis["signals"]["negative"]:
            print("### ⚠️ 风险点")
            for s in analysis["signals"]["negative"]: print(f"- {s['description']}")
            print()
        if analysis["checklist"]:
            print("### 📋 建议")
            for item in analysis["checklist"]:
                if not item["done"]: print(f"- **[{item['priority']}]** {item['hint']}")

    elif args.command == "coach":
        result = analyze_pr(
            args.title, args.description, args.repo,
            body=args.body, labels=args.labels, author=args.author,
            star_count=args.star_count, repo_merge_rate=args.repo_merge_rate,
            author_association=args.author_association,
        )
        tier = result["tier"]
        icon = TIER_ICONS.get(tier, "⚪")
        label = TIER_LABELS.get(tier, tier)
        passed = tier != "high_risk"

        if args.format == "json":
            result["pass"] = passed
            result["exit_code"] = 0 if passed else 1
            import json as _json
            print(_json.dumps(result, indent=2, ensure_ascii=False))
        else:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{icon} {status} — {label}\n")
            if result["signals"]["negative"]:
                for s in result["signals"]["negative"]:
                    sev = s.get("severity", "")
                    sev_icon = {"critical": "🚨", "high": "⚠️", "medium": "📋"}.get(sev, "•")
                    print(f"  {sev_icon} {s['description']}")
                    if s.get("fix_action"): print(f"     → {s['fix_action']}")
                print()
            undone = [c for c in result["checklist"] if not c["done"]]
            if undone:
                print("📋 待修复:")
                for item in undone: print(f"  [{item['priority']}] {item['hint']}")
                print()
            if passed:
                print("可以提交，但建议先完成上述 checklist。")
            else:
                print("请先修复上述问题再提交。")
        sys.exit(0 if passed else 1)

    elif args.command == "describe":
        print(f"## PR 描述\n### 标题\n{args.title}\n### 描述\n{args.description}\n")
        if args.issue: print(f"### 关联 Issue\nCloses {args.issue}\n")
        print("### 验收标准\n- [ ] 代码实现\n- [ ] 测试覆盖\n- [ ] DCO sign-off\n- [ ] CI 通过")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
