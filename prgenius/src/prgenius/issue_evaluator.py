"""Issue Evaluator — 自动化 issue 质量审核

v1.0.0: 从 PR evaluator 扩展到 issue 审核
- 核心接口: analyze_issue() → 结构化信号 + 可操作建议 + 风险等级
- 支持: 内容质量、格式规范、标签完整性、spam 检测、intake 质量
- 降级: 静默跳过无法解析的 issue
"""
from __future__ import annotations
import re
from typing import Any, Dict, List, Optional

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

# 爬虫友好标签（至少需要 3 个）
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

# Spam 关键词
SPAM_KEYWORDS = [
    "buy now", "click here", "free money", "casino", "viagra",
    "crypto pump", "limited time offer", "act now", "congratulations",
    "you won", "claim your", "double your",
]

# Secret 模式
SECRET_PATTERNS = [
    re.compile(r"(?:ghp|gho|ghu|ghs|ghr|github_pat)_[a-zA-Z0-9]{10,}"),
    re.compile(r"xox[bpras]-[a-zA-Z0-9\-]{10,}"),
    re.compile(r"(?:AKIA|ABIA|ACCA|ASIA)[A-Z0-9]{16}"),
    re.compile(r"(?:sk|pk|rk|ak)[_-][a-zA-Z0-9]{10,}"),
    re.compile(r"(?:password|secret|token|api[_-]?key)\s*[:=]\s*\S+", re.IGNORECASE),
]


# ============================================================
# 核心函数
# ============================================================

def analyze_issue(issue: Dict[str, Any]) -> Dict[str, Any]:
    """分析单个 issue，返回结构化评估结果。

    Args:
        issue: GitHub issue 对象（通过 API 获取）

    Returns:
        {
            "score": int (0-100),
            "risk": "low" | "medium" | "high" | "critical",
            "issues": [{"severity": str, "message": str, "fix": str}],
            "suggestions": [str],
            "is_crawler_friendly": bool,
            "is_spam": bool,
            "quality_grade": "A" | "B" | "C" | "D" | "F",
        }
    """
    result = {
        "score": 0,
        "risk": "low",
        "issues": [],
        "suggestions": [],
        "is_crawler_friendly": False,
        "is_spam": False,
        "quality_grade": "F",
    }

    title = issue.get("title", "")
    body = issue.get("body", "") or ""
    labels = [l.get("name", "") for l in issue.get("labels", [])]

    # 1. Spam 检测
    if _is_spam(title, body):
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
        result["risk"] = "high"
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
    result["is_crawler_friendly"] = crawler_count >= 3

    # 6. 风险等级
    result["risk"] = _calculate_risk(result)

    # 7. 质量等级
    result["quality_grade"] = _grade(result["score"])

    # 8. 建议
    result["suggestions"] = _generate_suggestions(result, labels)

    return result


def analyze_issues_batch(issues: List[Dict[str, Any]]) -> Dict[str, Any]:
    """批量分析 issues，返回汇总结果。"""
    results = [analyze_issue(issue) for issue in issues]

    total = len(results)
    spam_count = sum(1 for r in results if r["is_spam"])
    high_risk = sum(1 for r in results if r["risk"] in ("high", "critical"))
    avg_score = sum(r["score"] for r in results) / total if total else 0
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
# 辅助函数
# ============================================================

def _is_spam(title: str, body: str) -> bool:
    """检测 spam。"""
    text = (title + " " + body).lower()
    return any(kw in text for kw in SPAM_KEYWORDS)


def _detect_secrets(text: str) -> List[str]:
    """检测 secret 泄露。"""
    found = []
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            found.append(pattern.pattern[:30])
    return found


def _check_title(title: str) -> int:
    """检查标题质量。"""
    if not title or len(title) < 10:
        return 0
    if len(title) > 200:
        return 5
    return 10


def _check_body(body: str) -> int:
    """检查 body 质量。"""
    if not body or len(body) < 20:
        return 0
    if len(body) < 100:
        return 10
    if len(body) > 10000:
        return 15
    return 20


def _check_labels(labels: List[str]) -> int:
    """检查标签。"""
    if not labels:
        return 0
    if len(labels) >= 3:
        return 10
    return 5


def _check_structure(body: str) -> int:
    """检查格式结构。"""
    if not body:
        return 0
    # 检查是否有 markdown 标题
    if re.search(r"^#{1,3}\s", body, re.MULTILINE):
        return 10
    # 检查是否有列表
    if re.search(r"^[-*]\s", body, re.MULTILINE):
        return 5
    return 0


def _check_no_secrets(body: str) -> int:
    """检查无 secret。"""
    if _detect_secrets(body):
        return 0
    return 15


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

    # 检查爬虫友好度
    crawler_count = len(set(labels) & CRAWLER_LABELS)
    if crawler_count < 3:
        issues.append({
            "severity": "low",
            "message": f"Only {crawler_count}/3 crawler-friendly labels",
            "fix": "Add agent-friendly, no-credentials, has-test labels",
        })

    return issues


def _calculate_risk(result: Dict) -> str:
    """计算风险等级。"""
    if result["is_spam"]:
        return "critical"
    if result["score"] < 30:
        return "high"
    if result["score"] < 60:
        return "medium"
    return "low"


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


def _generate_suggestions(result: Dict, labels: List[str]) -> List[str]:
    """生成改进建议。"""
    suggestions = []

    if result["score"] < 60:
        suggestions.append("Improve issue content quality")

    if not result["is_crawler_friendly"]:
        suggestions.append("Add crawler-friendly labels (agent-friendly, no-credentials, has-test)")

    for issue in result["issues"]:
        if issue["fix"]:
            suggestions.append(issue["fix"])

    return suggestions
