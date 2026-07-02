#!/usr/bin/env python3
"""pr-genius Lesson Source Credibility Scorer

4 维度评分（per SCORING.md v0.1）：
1. 源可信度 (30)
2. 细节质量 (25)
3. 通用化 (25)
4. 脱敏度 (20)

Total 100. Grade: A=85+, B=75+, C=60+, D=<60.
"""

import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).parent.resolve()

# 已知组织名（减分项）
ORG_NAMES = ["小米", "阿里", "字节", "腾讯", "百度", "京东", "美团",
             "Xiaomi", "Alibaba", "Tencent", "Baidu", "ByteDance"]
INTERNAL_PRONOUNS = ["我们公司", "我们项目", "我们的项目", "本项目"]
INTERNAL_DOMAINS = [".internal", ".corp", ".local", ".lan"]


def detect_source_kind(source_url: str) -> tuple[str, int]:
    """Detect source kind and return (kind_name, base_score).

    Heuristic: if source URL points to a personal/small repo (e.g., pr-genius),
    it's likely own-experience → higher base score. Otherwise, classify by host.
    """
    if not source_url:
        return ("unknown", 5)

    parsed = urlparse(source_url)
    host = parsed.netloc.lower()
    path = parsed.path.lower()

    # Personal / small repos that are typically own-experience logs
    PERSONAL_REPOS = ["pr-genius", "MisakaNet", "agent-medici", "self-grow-wiki"]
    is_personal_repo = (
        "github.com" in host and any(r in path for r in PERSONAL_REPOS)
    )

    if is_personal_repo:
        # Personal / small repo source = first-hand experience by default
        return ("own-git-history", 28)

    # Natural-language source descriptions: "Real incident", "Real test output..."
    # These are first-hand reports even without explicit URL
    if re.match(r'^(Real incident|Real test|Real event|own|self)', source_url, re.I):
        return ("own-experience", 26)

    if "github.com" in host:
        if "/issues/" in path:
            return ("github-issue", 22)
        if "/discussions/" in path:
            return ("github-discussion", 21)
        if "/blob/" in path or "/tree/" in path:
            return ("github-docs", 23)
        if "/pull/" in path:
            return ("github-pr", 20)
        if "/commits/" in path:
            return ("github-commit-observation", 20)

    if "v2ex.com" in host:
        return ("v2ex-thread", 14)

    if "news.ycombinator.com" in host:
        return ("hn-thread", 16)

    if "reddit.com" in host:
        return ("reddit-thread", 14)

    if "stackoverflow.com" in host:
        return ("stackoverflow", 16)

    if "dev.to" in host or "medium.com" in host:
        return ("blog", 12)

    return ("other", 8)


def get_post_metric(url: str) -> int:
    """Estimate post metric (replies/upvotes) from cached metadata.
    Returns 0 if unknown — caller should pass metric manually."""
    # In real use, this would call an API or read from a cache.
    # For now, return 0; manual override via env var.
    return int(os.environ.get("POST_METRIC", "0"))


def score_source(source_url: str, content: str) -> tuple[int, list[str]]:
    """Score source credibility (max 30)."""
    notes = []
    kind, base = detect_source_kind(source_url)
    notes.append(f"source kind: {kind}")

    # Adjust by post metric for forum sources
    metric = get_post_metric(source_url)
    if kind in ("v2ex-thread", "hn-thread", "reddit-thread"):
        if metric >= 100:
            base = max(base, 22)
            notes.append(f"high metric ({metric}) → +score")
        elif metric >= 50:
            base = max(base, 18)
            notes.append(f"medium metric ({metric})")
        elif metric >= 20:
            base = max(base, 14)

    # Auto deductions — only on actual AI-generated markers, not on lesson topics
    # about AI. Lesson-01 to 05 discuss AI but aren't AI-generated.
    # Look for specific AI-GENERATED markers (e.g., "this article was AI-generated")
    if re.search(r'\b(this (article|post|comment) was (ai|generated))\b', content, re.I):
        base -= 5
        notes.append("explicit AI-generated marker → -5")
    if re.search(r'bot[\-:]\s*ai[\-_ ]?policy', content, re.I):
        base -= 5
        notes.append("contains bot:ai-policy-comment → -5")

    return max(0, min(30, base)), notes


def score_detail(content: str) -> tuple[int, list[str]]:
    """Score detail quality (max 25)."""
    notes = []
    score = 0

    # 1. Specific error / log mentions (5)
    if re.search(r'(error|fail|exception|crash|timeout|traceback|报错|异常|崩溃)', content, re.I):
        score += 5
        notes.append("specific error/log mention → +5")

    # 2. Code blocks (8) — count fenced blocks
    code_blocks = re.findall(r'```[\w]*\n.*?\n```', content, re.DOTALL)
    inline_codes = re.findall(r'`[^`\n]+`', content)
    if len(code_blocks) >= 2:
        score += 8
        notes.append(f"multiple code blocks ({len(code_blocks)}) → +8")
    elif len(code_blocks) >= 1 or len(inline_codes) >= 3:
        score += 5
        notes.append(f"some code ({len(code_blocks)} blocks, {len(inline_codes)} inline) → +5")

    # 3. Specific log / config / SQL (5)
    if re.search(r'(SELECT|INSERT|UPDATE|import|from|class|function|def |sudo |curl |pip |npm )', content):
        score += 5
        notes.append("specific commands/SQL → +5")

    # 4. Root cause explanation (4)
    if re.search(r'(因为|due to|because|root cause|根因|cause is|reason:)', content, re.I):
        score += 4
        notes.append("root cause explanation → +4")

    # 5. Comparison table / alternatives (3)
    if re.search(r'^\s*\|.*\|.*\|', content, re.MULTILINE):
        score += 3
        notes.append("comparison table → +3")

    return min(25, score), notes


def score_generalization(content: str) -> tuple[int, list[str]]:
    """Score generalization (max 25)."""
    notes = []
    score = 25  # start full

    # Auto deductions
    for org in ORG_NAMES:
        if re.search(rf'\b{re.escape(org)}\b', content):
            score -= 5
            notes.append(f"contains org name `{org}` → -5")
            break

    for pronoun in INTERNAL_PRONOUNS:
        if pronoun in content:
            score -= 5
            notes.append(f"contains internal pronoun `{pronoun}` → -5")
            break

    # TODO v0.2: check duplicate against existing misakanet lessons
    # For now, simple heuristic: if content has too many specifics, lower score
    if re.search(r'2026-\d{2}-\d{2}', content):
        # Has a date — not auto-deduct, but note it
        notes.append("contains specific date (informational)")

    return max(0, score), notes


def score_sanitization(content: str) -> tuple[int, list[str]]:
    """Score sanitization (max 20)."""
    notes = []
    score = 20  # start full

    # Detect secrets patterns (require ≥20 chars after prefix to avoid false positives)
    if re.search(r'ghp_[a-zA-Z0-9]{20,}', content):
        score -= 10
        notes.append("contains GitHub PAT → -10")
    if re.search(r'sk-[a-zA-Z0-9]{20,}', content):
        score -= 10
        notes.append("contains OpenAI sk key → -10")
    if re.search(r'AKIA[A-Z0-9]{16}', content):
        score -= 10
        notes.append("contains AWS access key → -10")
    if re.search(r'AIza[A-Za-z0-9_-]{35}', content):
        score -= 10
        notes.append("contains GCP API key → -10")

    # Educational/example mentions of secrets are OK (e.g., in lesson about PAT security)
    # Check if content has explicit "example" / "demo" / "教学" / "demo" markers
    is_educational = bool(re.search(r'(example|demo|教学|示例|illustrate)', content, re.I))
    if is_educational and score < 20:
        # Restore some points for clearly educational content
        score = max(score + 5, 15)
        notes.append("educational example → +5 (partial credit)")
    if re.search(r'1[3-9]\d{9}', content):
        # Verify it's actually a phone (look for context like "tel:" or "phone:" or "电话:")
        phone_match = re.search(r'(tel[:.]?\s*|phone[:.]?\s*|电话[:.]?\s*|手机[:.]?\s*)1[3-9]\d{9}', content, re.I)
        if phone_match:
            score -= 10
            notes.append("contains Chinese phone number → -10")
        # else: false positive, skip
    if re.search(r'[\w.+-]+@[\w-]+\.[a-z]{2,}', content, re.I):
        # Exclude common false positives: markdown image syntax, @-mention, or @example.com
        email_match = re.findall(r'(?<![!`\[])[\w.+-]+@[\w-]+\.[a-z]{2,}', content, re.I)
        real_emails = [e for e in email_match if 'example.com' not in e.lower()
                       and 'example.org' not in e.lower()
                       and 'placeholder' not in e.lower()]
        if real_emails:
            score -= 5
            notes.append(f"contains email pattern ({real_emails[:2]}) → -5")
    for dom in INTERNAL_DOMAINS:
        if dom in content:
            score -= 5
            notes.append(f"contains internal domain {dom} → -5")
            break

    return max(0, score), notes


def grade(score: int) -> str:
    if score >= 85:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    return "D"


def score_lesson_file(filepath: Path) -> dict:
    """Score a single lesson .md file. Returns full breakdown."""
    content = filepath.read_text(encoding="utf-8")

    # Extract source URL from frontmatter (if any)
    source_url = ""
    if content.startswith("---"):
        try:
            frontmatter = content.split("---", 2)[1]
            m = re.search(r'"source"\s*:\s*"([^"]+)"', frontmatter)
            if m:
                source_url = m.group(1)
        except IndexError:
            pass

    src_score, src_notes = score_source(source_url, content)
    det_score, det_notes = score_detail(content)
    gen_score, gen_notes = score_generalization(content)
    sen_score, sen_notes = score_sanitization(content)

    total = src_score + det_score + gen_score + sen_score
    return {
        "file": filepath.name,
        "total": total,
        "grade": grade(total),
        "breakdown": {
            "source": src_score,
            "detail": det_score,
            "general": gen_score,
            "sensitive": sen_score,
        },
        "notes": {
            "source": src_notes,
            "detail": det_notes,
            "general": gen_notes,
            "sensitive": sen_notes,
        },
        "pass": total >= 75,
    }


def main():
    md_files = sorted(ROOT.glob("lesson-*.md"))
    if not md_files:
        print("No lesson files found.")
        return 1

    print(f"pr-genius Lesson Source Scorer — {len(md_files)} files\n")
    print(f"{'File':<55} {'Src':>4} {'Det':>4} {'Gen':>4} {'Sen':>4} {'Total':>6} {'Grade':>5}")
    print("-" * 90)

    passed = 0
    for f in md_files:
        r = score_lesson_file(f)
        b = r["breakdown"]
        marker = "✅" if r["pass"] else "❌"
        print(f"{r['file']:<55} {b['source']:>4} {b['detail']:>4} {b['general']:>4} {b['sensitive']:>4} {r['total']:>6} {r['grade']:>5} {marker}")
        if r["pass"]:
            passed += 1

    print("-" * 90)
    print(f"Passed (≥75): {passed}/{len(md_files)}")

    if "--verbose" in sys.argv:
        print("\n=== Detailed Notes ===")
        for f in md_files:
            r = score_lesson_file(f)
            print(f"\n[{r['grade']}] {r['file']} ({r['total']}/100)")
            for dim, ns in r["notes"].items():
                if ns:
                    print(f"  {dim}: {'; '.join(ns)}")

    return 0 if passed == len(md_files) else 1


if __name__ == "__main__":
    sys.exit(main())