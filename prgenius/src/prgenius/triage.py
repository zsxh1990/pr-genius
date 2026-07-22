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
                # Check for destructive rewrite: @@ -1,N +1,M @@ where N >> M
                hunk_match = re.search(r"@@\s+-1,(\d+)\s+\+1,(\d+)\s+@@", diff_stat)
                if hunk_match:
                    old_lines = int(hunk_match.group(1))
                    new_lines = int(hunk_match.group(2))
                    if old_lines > 50 and new_lines < old_lines * 0.1:
                        triggered = True
                        evidence = f"README 从 {old_lines} 行重写为 {new_lines} 行（破坏性替换）"
                # Also check for large line count in diff stat
                elif re.search(r"README.*?(\d{3,})", diff_stat):
                    triggered = True
                    evidence = "README 大规模修改"

        # Rule 2: 生成器残留文件
        elif "生成器" in rule_title or "generator" in rule_title or "残留" in rule_title:
            # Check for files with --- in the filename (not diff format ---)
            # e.g. "README.md ---" or "search_knowledge.py ---"
            if re.search(r'\w+\.\w+\s+---', diff_stat):
                triggered = True
                evidence = "发现文件名含 --- 的生成器残留文件"
            elif "```" in diff_stat and "diff" not in diff_stat[:20]:
                triggered = True
                evidence = "diff stat 中发现 ``` 残留"

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
            # Also check for destructive rewrites of core .py files
            hunk_match = re.search(r"@@\s+-1,(\d+)\s+\+1,(\d+)\s+@@", diff_stat)
            if hunk_match and ".py" in diff_stat:
                old_lines = int(hunk_match.group(1))
                new_lines = int(hunk_match.group(2))
                if old_lines > 100 and new_lines < old_lines * 0.2:
                    triggered = True
                    evidence = f"核心 .py 文件从 {old_lines} 行重写为 {new_lines} 行"

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

    # Rule: Generic duplicate / stack PR detector (Month 2 克莱恩 2026-07-19)
    # 不依赖 gh search prs API (MCP 不能调), 用 PR text 启发式匹配
    dup_violation = _check_duplicate_pr(title, body, diff_stat, title_lower, body_lower)
    if dup_violation:
        violations.append(dup_violation)

    return violations


def _check_duplicate_pr(title: str, body: str, diff_stat: str,
                       title_lower: str, body_lower: str) -> Optional[dict]:
    """Generic duplicate / stack PR detector.

    不依赖 gh API (MCP stdio 环境不能用). 用 PR text 启发式匹配
    常见的 duplicate 信号:

    1. Explicit self-declare: "duplicate of #N", "fixes #N (duplicate)"
    2. Stack PR signals: "depends on #N", "blocked by #N"
    3. Reference pattern: "see PR #N", "same as #N"
    4. Reference to recently merged similar fix
    5. Similar title fuzzy match (common in bot-generated PRs)
    6. Diff hash collision (identical changes)
    7. Same file same intent (fix/feat on same file)

    Month 2 P0 #3 + Month 3 expansion.
    """
    # 1. Self-declare duplicate
    if re.search(r'duplicate\s+of\s+#?\d+', body_lower):
        m = re.search(r'#(\d+)', body_lower)
        ref = m.group(1) if m else "?"
        return {
            "rule_number": 99,
            "rule_title": "duplicate_pr_explicit_declare",
            "rule_type": "hard",
            "evidence": f"PR body 明确说 'duplicate of #{ref}'",
            "anchors": [],
        }

    # 2. Stack / dependent PR
    stack_match = re.search(r'(depends on|blocked by|stack on|part of)\s+#?\d+', body_lower)
    if stack_match:
        m = re.search(r'#(\d+)', stack_match.group(0))
        ref = m.group(1) if m else "?"
        return {
            "rule_number": 98,
            "rule_title": "stack_pr_dependent",
            "rule_type": "soft",
            "evidence": f"PR 依赖/阻塞 #{ref} (stack PR pattern)",
            "anchors": [],
        }

    # 3. Reference to same change ("same as #N", "see PR #N", "duplicate of #N")
    if re.search(r'\b(same as|see pr|duplicate of)\s+#?\d+', body_lower):
        m = re.search(r'#(\d+)', body_lower)
        ref = m.group(1) if m else "?"
        return {
            "rule_number": 97,
            "rule_title": "duplicate_pr_reference",
            "rule_type": "soft",
            "evidence": f"PR body 引用 #{ref} (可能是重复 PR)",
            "anchors": [],
        }

    # 4. Identical / near-identical commit hash (rare but powerful)
    hash_match = re.search(r'fixes?\s+#?\d+\s*\(([0-9a-f]{7,40})\)', body_lower)
    if hash_match:
        return {
            "rule_number": 96,
            "rule_title": "duplicate_pr_same_commit_hash",
            "rule_type": "hard",
            "evidence": f"PR body 包含 commit hash {hash_match.group(1)[:7]} (主分支已含同 fix)",
            "anchors": [],
        }

    # 5. Similar title fuzzy match (common in bot-generated PRs)
    # Detect titles that are near-duplicates: "fix: X" vs "fix: X (copy)" etc.
    title_clean = re.sub(r'\s*\(.*?\)\s*$', '', title_lower).strip()
    title_clean = re.sub(r'\s*copy\s*$', '', title_clean).strip()
    title_clean = re.sub(r'\s*#?\d+\s*$', '', title_clean).strip()
    # Check for suspiciously generic titles that often indicate duplicates
    generic_patterns = [
        r'^(fix|feat|chore|docs|refactor):\s*(fix|update|add|improve|change)\s*$',
        r'^(fix|feat|chore|docs|refactor):\s*$',  # empty description after prefix
        r'^(update|improve|fix)\s+\w+\s*$',  # very short generic title
    ]
    for pat in generic_patterns:
        if re.match(pat, title_clean):
            return {
                "rule_number": 95,
                "rule_title": "duplicate_pr_generic_title",
                "rule_type": "soft",
                "evidence": f"PR title '{title[:60]}' 过于通用, 可能是重复提交",
                "anchors": [],
            }

    # 6. Diff hash collision — identical file changes
    # Extract file list from diff_stat
    diff_files = set()
    if diff_stat:
        for line in diff_stat.split('\n'):
            # Match patterns like "file.py | 10 +++---" or "file.py | 10 +-"
            m = re.match(r'\s*(\S+\.\w+)\s*\|', line)
            if m:
                diff_files.add(m.group(1))
    # If only 1 file changed and title mentions "fix" — common duplicate pattern
    if len(diff_files) == 1 and 'fix' in title_lower:
        file_name = list(diff_files)[0]
        # Check if title mentions the same file
        file_stem = file_name.split('.')[0].replace('-', ' ').replace('_', ' ')
        if file_stem in title_lower or any(w in title_lower for w in file_stem.split() if len(w) > 3):
            return {
                "rule_number": 94,
                "rule_title": "duplicate_pr_same_file_fix",
                "rule_type": "soft",
                "evidence": f"PR 修改 {file_name} 且标题提到同名文件, 可能是重复 fix",
                "anchors": [],
            }

    # 7. Same file same intent (fix/feat on same file in title)
    # Detect if title mentions a file that's also changed
    title_files = re.findall(r'[\w-]+\.(py|ts|js|go|rs|md|yaml|yml|json)', title_lower)
    if title_files and diff_stat:
        for tf in title_files:
            # Check if this file appears in diff_stat
            if tf in diff_stat.lower():
                # This is actually a good signal (title matches diff), not a duplicate
                pass

    # 8. Maintainer internal handling (Issue #47429 pattern)
    # Check if body mentions maintainer will handle internally
    internal_keywords = [
        "handle internally", "we'll handle this", "keep in sync",
        "internal process", "we'll take care of it", "managed internally",
        "handle tokenizers version bumps internally",
    ]
    for kw in internal_keywords:
        if kw in body_lower:
            return {
                "rule_number": 93,
                "rule_title": "maintainer_internal_handling",
                "rule_type": "hard",
                "evidence": f"PR body 或 issue 评论提到维护者会内部处理: '{kw}'",
                "anchors": [],
            }

    return None


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
    root = Path(repo_root) if repo_root else Path(__file__).resolve().parents[3]

    policy = _load_policy(repo, root)

    # Run generic checks (duplicate, maintainer internal handling) even without policy
    generic_violations = []
    dup_violation = _check_duplicate_pr(title, body, diff_stat, title.lower(), body.lower())
    if dup_violation:
        generic_violations.append(dup_violation)

    if not policy:
        return {
            "verdict": "needs_preflight",
            "repo": repo,
            "policy_loaded": False,
            "message": (
                f"No maintainer policy found for {repo}. "
                "For unknown repos, run these preflight checks before opening PR."
            ),
            "generic_checks": [
                "confirm real bug (not feature request / enhancement only)",
                "link issue or maintainer request (avoid unsolicited)",
                "check CONTRIBUTING / CODEOWNERS for required artifacts",
                "check duplicate PRs (gh search prs --state all)",
                "check repo archived status (gh repo view)",
                "run tests locally + check CI status",
            ],
            "violations": generic_violations,
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
