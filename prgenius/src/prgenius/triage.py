"""PR Triage — Policy-aware PR screening.

Reads maintainer policy from docs/policies/<repo>.md and checks
the PR against hard/soft rules. Returns a structured triage brief.

Usage:
    from prgenius.triage import triage_pr
    result = triage_pr("feat: add feature", "org/repo", body="...", diff_stat=...)
"""

import re
from pathlib import Path
from typing import Optional


def _load_policy(repo: str, repo_root: Path) -> Optional[dict]:
    """Load maintainer policy from docs/policies/<org>-<repo>.md."""
    policy_dir = repo_root / "docs" / "policies"
    policy_file = policy_dir / f"{repo.replace('/', '-')}.md"
    if not policy_file.exists():
        return None

    content = policy_file.read_text(encoding="utf-8")

    # Parse frontmatter
    fm = {}
    m = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if m:
        for line in m.group(1).split("\n"):
            if ":" in line:
                key, _, val = line.partition(":")
                fm[key.strip()] = val.strip()

    # Extract rules with section-aware type detection
    rules = []
    current_rule = None
    current_section = "unknown"  # Track ## Hard Rejections / ## Soft Warnings

    for line in content.split("\n"):
        # Detect section headers
        if line.startswith("## Hard Rejections"):
            current_section = "hard"
            continue
        elif line.startswith("## Soft Warnings"):
            current_section = "soft"
            continue

        # Match rule headers: ### 1. Rule Title
        rule_match = re.match(r"^###\s+(\d+)\.\s+(.+)$", line)
        if rule_match:
            if current_rule:
                rules.append(current_rule)
            current_rule = {
                "number": int(rule_match.group(1)),
                "title": rule_match.group(2).strip(),
                "type": current_section,
                "description": "",
                "anchors": [],
            }
            continue

        if current_rule:
            if "**规则：**" in line or "**Rule:**" in line:
                current_rule["description"] = line.split("**：")[-1].split("**:")[-1].strip()
            # Override type if explicitly stated in the rule
            if "Hard" in line and "直接关闭" in line:
                current_rule["type"] = "hard"
            elif "Soft" in line and "review 时关注" in line:
                current_rule["type"] = "soft"
            # Extract anchor PRs
            anchors = re.findall(r"#(\d+)", line)
            if anchors:
                current_rule["anchors"].extend(int(a) for a in anchors)

    if current_rule:
        rules.append(current_rule)

    return {
        "repo": repo,
        "file": str(policy_file),
        "frontmatter": fm,
        "rules": rules,
    }


def _check_policy_rules(title: str, body: str, diff_stat: str, policy: dict) -> list[dict]:
    """Check PR against policy rules. Returns list of violations."""
    violations = []
    title_lower = title.lower()
    body_lower = body.lower()

    for rule in policy.get("rules", []):
        rule_title = rule["title"].lower()
        triggered = False
        evidence = ""

        # Rule 1: 破坏性 README 重写
        if "readme" in rule_title and ("重写" in rule_title or "rewrite" in rule_title):
            if "readme" in diff_stat.lower():
                # Check if it's a large change (heuristic: more than 50 lines changed in README)
                readme_match = re.search(r"README.*?(\d+)", diff_stat)
                if readme_match and int(readme_match.group(1)) > 50:
                    triggered = True
                    evidence = f"README 修改超过 50 行"

        # Rule 2: 生成器残留文件
        elif "生成器" in rule_title or "generator" in rule_title or "残留" in rule_title:
            if "---" in diff_stat or "```" in diff_stat:
                triggered = True
                evidence = "diff stat 中发现 --- 或 ``` 残留"

        # Rule 3: 粘贴 patch 到源码
        elif "粘贴" in rule_title or "paste" in rule_title or "patch" in rule_title:
            if ".py" in diff_stat and ("diff" in body_lower or "patch" in body_lower or "```" in body):
                triggered = True
                evidence = "PR body 包含 diff/patch 内容，且修改了 .py 文件"

        # Rule 4: 核心文件大删
        elif "核心" in rule_title or "大删" in rule_title or "core" in rule_title:
            # Check for large deletions in core files
            deletions = re.findall(r"(\d+)\s*deletions?", diff_stat, re.I)
            if deletions and int(deletions[0]) > 100:
                triggered = True
                evidence = f"删除超过 100 行"

        # Rule 5: docs-only PR 不应改代码
        elif "docs" in rule_title and "代码" in rule_title:
            if any(w in title_lower for w in ["docs", "readme", "documentation"]):
                if ".py" in diff_stat or ".ts" in diff_stat or ".js" in diff_stat:
                    triggered = True
                    evidence = "标题含 docs 但修改了代码文件"

        # Rule 6: Worker/API PR 需设计审查
        elif "worker" in rule_title or "api" in rule_title:
            if "workers/" in diff_stat or "/api/" in diff_stat:
                triggered = True
                evidence = "修改了 workers/ 或 API 文件"

        # Rule 7: star/fork 证明
        elif "star" in rule_title or "fork" in rule_title:
            if any(w in body_lower for w in ["stars", "forks", "clone"]):
                triggered = True
                evidence = "PR body 中使用了 star/fork/clone 作为证明"

        # Rule 8: helpful=0 宣称 adoption
        elif "helpful" in rule_title or "adoption" in rule_title:
            if any(w in body_lower for w in ["adopted", "community", "users", "adoption"]):
                if "helpful" in body_lower and "0" in body:
                    triggered = True
                    evidence = "宣称 adoption 但 helpful=0"

        # Rule 9: bounty contributor
        elif "bounty" in rule_title:
            if "bounty" in body_lower:
                triggered = True
                evidence = "PR 来自 bounty 任务"

        if triggered:
            violations.append({
                "rule_number": rule["number"],
                "rule_title": rule["title"],
                "rule_type": rule["type"],
                "evidence": evidence,
                "anchors": rule.get("anchors", []),
            })

    return violations


def triage_pr(
    title: str,
    repo: str,
    body: str = "",
    diff_stat: str = "",
    repo_root: Optional[Path] = None,
) -> dict:
    """Triage a PR against maintainer policy.

    Args:
        title: PR title
        repo: target repo (org/repo)
        body: PR body/description
        diff_stat: git diff --stat output (or similar summary)
        repo_root: path to pr-genius repo root

    Returns:
        dict with verdict, violations, policy_loaded, etc.
    """
    root = repo_root or Path(__file__).resolve().parent.parent.parent

    policy = _load_policy(repo, root)
    if not policy:
        return {
            "verdict": "no_policy",
            "repo": repo,
            "policy_loaded": False,
            "message": f"No maintainer policy found for {repo}",
            "violations": [],
        }

    violations = _check_policy_rules(title, body, diff_stat, policy)

    hard_violations = [v for v in violations if v["rule_type"] == "hard"]
    soft_violations = [v for v in violations if v["rule_type"] == "soft"]

    if hard_violations:
        verdict = "reject"
        message = f"❌ REJECT — {len(hard_violations)} hard rule(s) violated"
    elif soft_violations:
        verdict = "warn"
        message = f"⚠️ WARN — {len(soft_violations)} soft rule(s) triggered"
    else:
        verdict = "pass"
        message = "✅ PASS — no policy violations"

    return {
        "verdict": verdict,
        "repo": repo,
        "policy_loaded": True,
        "policy_file": policy["file"],
        "message": message,
        "violations": violations,
        "hard_violations": len(hard_violations),
        "soft_violations": len(soft_violations),
        "rules_checked": len(policy["rules"]),
    }
