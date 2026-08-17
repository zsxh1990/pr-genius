"""Issue Evaluator — 自动化 issue 质量审核

v1.1.0: 维护者 review 修复
- Secret 标识改为 human-readable 名称
- Spam 检测加上下文窗口（短 body + keyword = 更高置信度）
- _calculate_risk() 保留 high severity issues 的 risk
- 分析结果带 number/title，不依赖 dict 相等性

v1.0.0: 从 PR evaluator 扩展到 issue 审核
- 核心接口: analyze_issue() → 结构化信号 + 可操作建议 + 风险等级
- 支持: 内容质量、格式规范、标签完整性、spam 检测、intake 质量
- 降级: 静默跳过无法解析的 issue
"""
from __future__ import annotations
import re
from typing import Any, Dict, List, Optional, Tuple

# ============================================================
# 常量
# ============================================================

# Issue 类型标签
ISSUE_TYPE_LABELS = {
    "bug": "bug",
    "enhancement": "feature",
    "documentation": "docs",
    "question": "question",
    "intake": "intake",
    "security": "security",
}

# 必需标签（按 issue 类型）
REQUIRED_LABELS = {
    "intake": ["intake", "pending-review"],
    "bug": ["bug"],
    "enhancement": ["enhancement"],
}

# 爬虫友好标签（可配置阈值，默认 3）
CRAWLER_LABELS = {
    "agent-friendly",
    "no-credentials",
    "has-test",
    "zero-bounty",
    "good first issue",
    "status:competition",
    "pool:quick",
    "pool:deep",
}
DEFAULT_CRAWLER_THRESHOLD = 3

# 内容质量评分维度
QUALITY_DIMENSIONS = {
    "has_title": {"weight": 10, "check": "title_length"},
    "has_body": {"weight": 20, "check": "body_length"},
    "has_labels": {"weight": 10, "check": "label_count"},
    "has_reproduction": {"weight": 15, "check": "has_repro"},
    "has_expected": {"weight": 10, "check": "has_expected"},
    "no_secrets": {"weight": 15, "check": "no_secrets"},
    "structured_format": {"weight": 10, "check": "has_headers"},
    "appropriate_length": {"weight": 10, "check": "body_length_range"},
}

# Spam 关键词（带权重，高置信度关键词）
SPAM_KEYWORDS_HIGH = [
    "buy now", "free money", "casino", "viagra",
    "crypto pump", "limited time offer", "act now",
    "you won", "claim your", "double your",
]
SPAM_KEYWORDS_LOW = [
    "click here", "congratulations", "prize", "winner",
    "free gift", "no cost", "risk free",
]

# Secret 模式 — (compiled_regex, human_readable_name)
SECRET_PATTERNS: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"(?:ghp|gho|ghu|ghs|ghr|github_pat)_[a-zA-Z0-9]{10,}"), "GitHub PAT"),
    (re.compile(r"xox[bpras]-[a-zA-Z0-9\-]{10,}"), "Slack Token"),
    (re.compile(r"(?:AKIA|ABIA|ACCA|ASIA)[A-Z0-9]{16}"), "AWS Access Key"),
    (re.compile(r"(?:sk|pk|rk|ak)[_-][a-zA-Z0-9]{10,}"), "API Key"),
    (re.compile(r"(?:password|secret|token|api[_-]?key)\s*[:=]\s*\S+", re.IGNORECASE), "Hardcoded Secret"),
    (re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----"), "Private Key"),
    (re.compile(r"eyJ[a-zA-Z0-9_-]{10,}\.eyJ[a-zA-Z0-9_-]{10,}"), "JWT Token"),
    (re.compile(r"npm_[a-zA-Z0-9]{36}"), "NPM Token"),
    (re.compile(r"glpat-[a-zA-Z0-9\-_]{20,}"), "GitLab PAT"),
]


# ============================================================
# 核心函数
# ============================================================

def analyze_issue(
    issue: Dict[str, Any],
    *,
    crawler_threshold: int = DEFAULT_CRAWLER_THRESHOLD,
) -> Dict[str, Any]:
    """分析单个 issue，返回结构化评估结果。

    Args:
        issue: GitHub issue 对象（通过 API 获取）
        crawler_threshold: 爬虫友好标签最少数量

    Returns:
        {
            "number": int,
            "title": str,
            "score": int (0-100),
            "risk": "low" | "medium" | "high" | "critical",
            "issues": [{"severity": str, "message": str, "fix": str}],
            "suggestions": [str],
            "is_crawler_friendly": bool,
            "is_spam": bool,
            "quality_grade": "A" | "B" | "C" | "D" | "F",
        }
    """
    number = issue.get("number", 0)
    title = issue.get("title", "")
    body = issue.get("body", "") or ""
    labels = [l.get("name", "") if isinstance(l, dict) else str(l)
              for l in issue.get("labels", [])]

    result: Dict[str, Any] = {
        "number": number,
        "title": title,
        "score": 0,
        "risk": "low",
        "issues": [],
        "suggestions": [],
        "is_crawler_friendly": False,
        "is_spam": False,
        "quality_grade": "F",
    }

    # 1. Spam 检测（带上下文）
    spam_confidence = _spam_confidence(title, body)
    if spam_confidence >= 2:
        result["is_spam"] = True
        result["risk"] = "critical"
        result["quality_grade"] = "F"
        result["issues"].append({
            "severity": "critical",
            "message": "Issue appears to be spam",
            "fix": "Close as spam",
        })
        return result

    # 2. Secret 泄露检测
    secrets_found = _detect_secrets(body)
    if secrets_found:
        result["issues"].append({
            "severity": "high",
            "message": f"Possible secret leakage: {', '.join(secrets_found)}",
            "fix": "Redact secrets before publishing",
        })

    # 3. 内容质量评分
    score = 0
    score += _check_title(title)
    score += _check_body(body)
    score += _check_labels(labels)
    score += _check_structure(body)
    score += _check_no_secrets(body)
    result["score"] = min(score, 100)

    # 4. 标签完整性
    label_issues = _check_labels_complete(labels, body)
    result["issues"].extend(label_issues)

    # 5. 爬虫友好度
    crawler_count = len(set(labels) & CRAWLER_LABELS)
    result["is_crawler_friendly"] = crawler_count >= crawler_threshold

    # 6. 风险等级（secret high 优先保留）
    result["risk"] = _calculate_risk(result)

    # 7. 质量等级
    result["quality_grade"] = _grade(result["score"])

    # 8. 建议
    result["suggestions"] = _generate_suggestions(result, labels)

    return result


def analyze_issues_batch(
    issues: List[Dict[str, Any]],
    *,
    crawler_threshold: int = DEFAULT_CRAWLER_THRESHOLD,
) -> Dict[str, Any]:
    """批量分析 issues，返回汇总结果。"""
    results = [analyze_issue(issue, crawler_threshold=crawler_threshold)
               for issue in issues]

    total = len(results)
    if total == 0:
        return {
            "total": 0,
            "spam_count": 0,
            "high_risk_count": 0,
            "average_score": 0,
            "crawler_friendly_count": 0,
            "grade_distribution": {g: 0 for g in ["A", "B", "C", "D", "F"]},
            "results": [],
        }

    spam_count = sum(1 for r in results if r["is_spam"])
    high_risk = sum(1 for r in results if r["risk"] in ("high", "critical"))
    avg_score = sum(r["score"] for r in results) / total
    crawler_friendly = sum(1 for r in results if r["is_crawler_friendly"])

    return {
        "total": total,
        "spam_count": spam_count,
        "high_risk_count": high_risk,
        "average_score": round(avg_score, 1),
        "crawler_friendly_count": crawler_friendly,
        "grade_distribution": {
            grade: sum(1 for r in results if r["quality_grade"] == grade)
            for grade in ["A", "B", "C", "D", "F"]
        },
        "results": results,
    }


# ============================================================
# 辅助函数 — Spam 检测
# ============================================================

def _spam_confidence(title: str, body: str) -> int:
    """Spam 置信度评分。

    返回 0-3:
    0 = clean
    1 = 低置信度（单个低权重 keyword）
    2 = 中置信度（单个高权重 keyword + 短 body，或 2+ 低权重）
    3 = 高置信度（2+ 高权重 keyword）
    """
    text = (title + " " + body).lower()

    high_hits = sum(1 for kw in SPAM_KEYWORDS_HIGH if kw in text)
    low_hits = sum(1 for kw in SPAM_KEYWORDS_LOW if kw in text)

    if high_hits >= 2:
        return 3
    if high_hits == 1 and len(body) < 100:
        return 2
    if high_hits == 1:
        return 1
    if low_hits >= 2:
        return 2
    if low_hits == 1 and len(body) < 50:
        return 1
    return 0


# ============================================================
# 辅助函数 — Secret 检测
# ============================================================

def _detect_secrets(text: str) -> List[str]:
    """检测 secret 泄露，返回 human-readable 名称列表。"""
    found = []
    for pattern, name in SECRET_PATTERNS:
        if pattern.search(text):
            if name not in found:
                found.append(name)
    return found


# ============================================================
# 辅助函数 — 内容质量评分
# ============================================================

def _check_title(title: str) -> int:
    """检查标题质量（0-15）。

    Scoring:
    - empty or <10 chars: 0
    - 10-50 chars: 10
    - 50-200 chars (optimal): 15
    - >200 chars (too long): 12
    """
    if not title or len(title) < 10:
        return 0
    if len(title) < 50:
        return 10
    if len(title) <= 200:
        return 15
    return 12


def _check_body(body: str) -> int:
    """检查 body 质量（0-30）。

    Scoring:
    - empty or <20 chars: 0
    - 20-99 chars: 8
    - 100-499 chars: 15
    - 500-1999 chars: 22
    - 2000-9999 chars (optimal): 30
    - >10000 chars (too long): 25
    """
    if not body or len(body) < 20:
        return 0
    if len(body) < 100:
        return 8
    if len(body) < 500:
        return 15
    if len(body) < 2000:
        return 22
    if len(body) <= 10000:
        return 30
    return 25


def _check_labels(labels: List[str]) -> int:
    """检查标签数量（0-15）。

    Scoring:
    - 0 labels: 0
    - 1 label: 5
    - 2 labels: 10
    - 3+ labels: 15
    """
    if not labels:
        return 0
    if len(labels) == 1:
        return 5
    if len(labels) == 2:
        return 10
    return 15


def _check_structure(body: str) -> int:
    """检查格式结构（0-20）。

    Scoring:
    - no structure: 0
    - lists only: 5
    - headers only: 10
    - headers + lists: 15
    - headers + lists + code blocks: 20
    """
    if not body:
        return 0
    has_headers = bool(re.search(r"^#{1,3}\s", body, re.MULTILINE))
    has_lists = bool(re.search(r"^[-*]\s", body, re.MULTILINE))
    has_code = bool(re.search(r"```", body))
    if has_headers and has_lists and has_code:
        return 20
    if has_headers and has_lists:
        return 15
    if has_headers:
        return 10
    if has_lists:
        return 5
    return 0


def _check_no_secrets(body: str) -> int:
    """检查无 secret（0-20）。"""
    if _detect_secrets(body):
        return 0
    return 20


# ============================================================
# 辅助函数 — 标签完整性
# ============================================================

def _check_labels_complete(labels: List[str], body: str) -> List[Dict]:
    """检查标签完整性。"""
    issues = []

    # 检查 intake 类型
    if "intake" in labels:
        if "pending-review" not in labels:
            issues.append({
                "severity": "medium",
                "message": "Intake issue missing 'pending-review' label",
                "fix": "Add 'pending-review' label",
            })

    # 检查 bug 类型
    if "bug" in labels:
        body_lower = body.lower()
        has_repro = any(kw in body_lower for kw in [
            "reproduce", "reproduction", "steps to", "复现",
            "1.", "2.", "step 1", "步骤",
        ])
        if not has_repro:
            issues.append({
                "severity": "medium",
                "message": "Bug issue missing reproduction steps",
                "fix": "Add reproduction steps to the issue body",
            })

    return issues


# ============================================================
# 辅助函数 — 风险计算
# ============================================================

def _calculate_risk(result: Dict) -> str:
    """计算风险等级。

    优先级：spam > high severity issues > score
    """
    if result["is_spam"]:
        return "critical"
    # 保留 high severity issues 的 risk（secret 泄露等）
    if any(i["severity"] in ("critical", "high") for i in result["issues"]):
        return "high"
    if result["score"] < 30:
        return "high"
    if result["score"] < 60:
        return "medium"
    return "low"


# ============================================================
# 辅助函数 — 等级映射
# ============================================================

def _grade(score: int) -> str:
    """评分转等级。"""
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    if score >= 40:
        return "D"
    return "F"


# ============================================================
# 辅助函数 — 建议生成
# ============================================================

def _generate_suggestions(result: Dict, labels: List[str]) -> List[str]:
    """生成改进建议。

    v1.1.1: 降低误报
    - score < 40 才建议 "Improve content quality"（之前 60 太激进）
    - 只有真正缺内容时才建议补充
    """
    suggestions = []

    if result["score"] < 40:
        suggestions.append("Improve issue content quality")

    if not result["is_crawler_friendly"]:
        suggestions.append(
            "Add crawler-friendly labels (agent-friendly, no-credentials, has-test)")

    for issue in result["issues"]:
        if issue.get("fix"):
            suggestions.append(issue["fix"])

    return suggestions
