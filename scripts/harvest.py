#!/usr/bin/env python3
"""
PR Failure Harvester — 从被拒 PR 中提取反模式/lesson draft

Usage:
    python3 scripts/harvest.py https://github.com/org/repo/pull/123
    python3 scripts/harvest.py org/repo 123
    python3 scripts/harvest.py org/repo 123 --type lesson
    python3 scripts/harvest.py org/repo 123 --type anti-pattern

输出: Markdown 文件，可直接放入 anti-patterns/ 或 misakanet-50/
"""
from __future__ import annotations
import argparse
import json
import os
import re
import subprocess
import sys
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
from typing import Optional


def gh_api(url: str) -> Optional[dict]:
    headers = {"Accept": "application/vnd.github.v3+json"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        try:
            result = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                token = result.stdout.strip()
        except Exception:
            pass
    if token:
        headers["Authorization"] = f"token {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"API error {e.code}: {url}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return None


def fetch_pr(repo: str, pr_number: int) -> Optional[dict]:
    return gh_api(f"https://api.github.com/repos/{repo}/pulls/{pr_number}")


def fetch_comments(repo: str, pr_number: int) -> list:
    data = gh_api(f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments")
    return data if data else []


def fetch_reviews(repo: str, pr_number: int) -> list:
    data = gh_api(f"https://api.github.com/repos/{repo}/pulls/{pr_number}/reviews")
    return data if data else []


def fetch_labels(repo: str, pr_number: int) -> list:
    data = gh_api(f"https://api.github.com/repos/{repo}/issues/{pr_number}")
    if not data:
        return []
    return [l["name"] for l in data.get("labels", [])]


def fetch_events(repo: str, pr_number: int) -> list:
    data = gh_api(f"https://api.github.com/repos/{repo}/issues/{pr_number}/events")
    return data if data else []


def extract_close_reason(pr: dict, comments: list, reviews: list, events: list = None) -> str:
    """从 PR 数据中提取关闭原因"""
    reasons = []
    if events is None:
        events = []

    # 检查是否作者自己关闭 (通过 events API)
    pr_author = pr.get("user", {}).get("login", "")
    for event in events:
        if event.get("event") == "closed":
            closer = event.get("actor", {}).get("login", "")
            if closer == pr_author:
                return f"作者 @{pr_author} 自己关闭了 PR"

    # 检查标签
    labels = [l["name"] for l in pr.get("labels", [])]
    label_reasons = {
        "ai-policy-violation": "AI 生成内容违反仓库 AI 使用政策",
        "missing-issue-link": "缺少 Issue 关联",
        "invalid": "PR 无效",
        "wontfix": "维护者不打算修复",
        "duplicate": "重复 PR",
        "stale": "长时间无活动被关闭",
        "spam": "垃圾内容",
    }
    for label in labels:
        if label in label_reasons:
            reasons.append(f"标签 `{label}`: {label_reasons[label]}")

    # 检查 maintainer 评论
    for comment in comments:
        body = (comment.get("body") or "").lower()
        author = comment.get("user", {}).get("login", "")
        assoc = comment.get("author_association", "")
        if assoc in ("OWNER", "MEMBER", "COLLABORATOR"):
            # 提取关键句子
            for line in (comment.get("body") or "").split("\n"):
                line = line.strip()
                if any(kw in line.lower() for kw in ["declined", "rejected", "closing", "won't merge", "not accepting", "already implemented"]):
                    reasons.append(f"维护者 @{author}: {line[:100]}")

    # 检查 review
    for review in reviews:
        if review.get("state") == "CHANGES_REQUESTED":
            body = review.get("body") or ""
            if body:
                reasons.append(f"Review 要求修改: {body[:100]}")

    return reasons[0] if reasons else "未明确"


def generate_anti_pattern_draft(repo: str, pr: dict, close_reason: str, comments: list) -> str:
    """生成反模式 draft"""
    pr_number = pr["number"]
    title = pr["title"]
    author = pr["user"]["login"]
    body = (pr.get("body") or "")[:500]
    labels = [l["name"] for l in pr.get("labels", [])]

    # 从标题/描述中提取 key
    key_slug = re.sub(r'[^a-z0-9]+', '-', title.lower())[:50].strip('-')

    today = datetime.now().strftime("%Y-%m-%d")

    return f"""---
type: Anti-Pattern
key: {key_slug}
description: "{title[:80]}"
symptom: "{close_reason[:100]}"
trigger_keywords:
  - "{title.split(':')[0].strip().lower() if ':' in title else title.split(' ')[0].lower()}"
fix_action: "TODO: 从 maintainer 评论中提取具体修复步骤"
source_pr: "{repo}#{pr_number}"
severity: medium
evidence:
  - "{repo}#{pr_number}: {close_reason[:80]}"
learned_at: {today}
---

## 反模式说明

**PR**: [{repo}#{pr_number}]({pr["html_url"]})
**作者**: @{author}
**标签**: {', '.join(labels) or '无'}
**关闭原因**: {close_reason}

### PR 描述

{body}

### Maintainer 关键评论

{_extract_key_comments(comments)}

### 如何避免

TODO: 从上述评论中总结具体避免步骤

### 历史案例

- {repo}#{pr_number}: {close_reason[:60]}
"""


def generate_lesson_draft(repo: str, pr: dict, close_reason: str, comments: list) -> str:
    """生成 lesson draft (MisakaNet 风格)"""
    pr_number = pr["number"]
    title = pr["title"]
    author = pr["user"]["login"]
    body = (pr.get("body") or "")[:500]

    today = datetime.now().strftime("%Y-%m-%d")
    lesson_slug = re.sub(r'[^a-z0-9]+', '-', title.lower())[:40].strip('-')

    return f"""---
type: Lesson
title: "{title[:80]}"
source: "{repo}#{pr_number}"
source_url: "{pr['html_url']}"
category: pr-failure
severity: medium
learned_at: {today}
---

## Problem

PR [{repo}#{pr_number}]({pr["html_url"]}) 被拒绝。

**标题**: {title}
**作者**: @{author}
**关闭原因**: {close_reason}

## Root Cause

{_extract_key_comments(comments)}

## What Happened

{body}

## Lesson

TODO: 从上述信息中提炼可复用的教训

## Solution

TODO: 如果有修复方案，在此记录

## Verification

TODO: 如何验证教训已内化
"""


def _extract_key_comments(comments: list) -> str:
    """提取 maintainer 的关键评论"""
    lines = []
    for comment in comments:
        assoc = comment.get("author_association", "")
        if assoc in ("OWNER", "MEMBER", "COLLABORATOR"):
            author = comment["user"]["login"]
            body = (comment.get("body") or "").strip()
            if body and len(body) > 10:
                # 只取前3行
                preview = "\n".join(body.split("\n")[:3])
                if len(preview) > 200:
                    preview = preview[:200] + "..."
                lines.append(f"> @{author}: {preview}")
    return "\n\n".join(lines) if lines else "无 maintainer 评论"


def main():
    parser = argparse.ArgumentParser(description="PR Failure Harvester")
    parser.add_argument("url_or_repo", help="PR URL 或 org/repo")
    parser.add_argument("number", nargs="?", type=int, help="PR number (如果第一个参数是 org/repo)")
    parser.add_argument("--type", "-t", choices=["anti-pattern", "lesson"], default="anti-pattern",
                        help="输出类型")
    parser.add_argument("--output", "-o", help="输出文件路径 (默认打印到 stdout)")
    args = parser.parse_args()

    # 解析 repo 和 pr_number
    if args.number:
        repo = args.url_or_repo
        pr_number = args.number
    else:
        # 从 URL 解析
        m = re.match(r'https?://github\.com/([^/]+/[^/]+)/pull/(\d+)', args.url_or_repo)
        if not m:
            print(f"无法解析: {args.url_or_repo}", file=sys.stderr)
            return 1
        repo = m.group(1)
        pr_number = int(m.group(2))

    print(f"🔍 获取 {repo}#{pr_number}...", file=sys.stderr)

    pr = fetch_pr(repo, pr_number)
    if not pr:
        print(f"无法获取 PR 数据", file=sys.stderr)
        return 1

    comments = fetch_comments(repo, pr_number)
    reviews = fetch_reviews(repo, pr_number)
    labels = fetch_labels(repo, pr_number)
    events = fetch_events(repo, pr_number)

    # 补充 labels 到 pr
    pr["labels"] = [{"name": l} for l in labels]

    close_reason = extract_close_reason(pr, comments, reviews, events)

    print(f"📋 关闭原因: {close_reason}", file=sys.stderr)

    if args.type == "anti-pattern":
        content = generate_anti_pattern_draft(repo, pr, close_reason, comments)
        default_name = f"anti-patterns/{repo.replace('/', '-')}-pr-{pr_number}.md"
    else:
        content = generate_lesson_draft(repo, pr, close_reason, comments)
        default_name = f"misakanet-50/lesson-draft-{repo.replace('/', '-')}-pr-{pr_number}.md"

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8")
        print(f"✅ 已保存到 {out_path}", file=sys.stderr)
    else:
        print(content)

    return 0


if __name__ == "__main__":
    sys.exit(main())
