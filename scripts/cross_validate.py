#!/usr/bin/env python3
"""
PR Genius 交叉验证脚本

从 GitHub API 拉取 PR 数据，调用 evaluator 评估，统计准确率。

Usage:
    python3 scripts/cross_validate.py --repo langchain-ai/langchain --limit 10
    python3 scripts/cross_validate.py --all
    python3 scripts/cross_validate.py --all --json
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 添加项目根目录到 path（必须在最前面，覆盖已安装的包）
REPO_ROOT = Path(__file__).resolve().parent.parent
LOCAL_SRC = REPO_ROOT / "prgenius" / "src"

# 从 sys.path 中移除已安装的 prgenius，优先使用本地版本
sys.path = [p for p in sys.path if "prgenius" not in p.lower() or "site-packages" not in p]
sys.path.insert(0, str(LOCAL_SRC))

# 清除已缓存的模块
for mod_name in list(sys.modules.keys()):
    if "prgenius" in mod_name:
        del sys.modules[mod_name]

from prgenius.evaluator import (
    predict_success_rate,
    is_bot_author,
    LABEL_SIGNALS,
)


# ============================================================
# GitHub API
# ============================================================

def gh_api(url: str) -> Optional[dict]:
    """调用 GitHub API"""
    headers = {"Accept": "application/vnd.github.v3+json"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        # 尝试从 gh CLI 获取 token
        try:
            import subprocess
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
        print(f"Request error: {e}", file=sys.stderr)
        return None


def fetch_prs(repo: str, state: str = "all", limit: int = 50) -> List[dict]:
    """拉取 PR 列表"""
    url = f"https://api.github.com/repos/{repo}/pulls?state={state}&sort=updated&direction=desc&per_page={min(limit, 100)}"
    data = gh_api(url)
    if not data:
        return []
    return data[:limit]


def fetch_pr_detail(repo: str, pr_number: int) -> Optional[dict]:
    """拉取单个 PR 详情"""
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    return gh_api(url)


def fetch_pr_labels(repo: str, pr_number: int) -> List[str]:
    """拉取 PR 标签"""
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}"
    data = gh_api(url)
    if not data:
        return []
    return [label["name"] for label in data.get("labels", [])]


def fetch_repo_info(repo: str) -> Optional[dict]:
    """拉取仓库信息"""
    url = f"https://api.github.com/repos/{repo}"
    return gh_api(url)


# ============================================================
# 评估逻辑
# ============================================================

def evaluate_pr(pr: dict, repo: str, star_count: int, repo_merge_rate: float = 0.0) -> dict:
    """评估单个 PR"""
    title = pr.get("title", "")
    body = pr.get("body", "") or ""
    author = pr.get("user", {}).get("login", "")
    author_association = pr.get("author_association", "NONE")
    merged = pr.get("merged_at") is not None
    state = pr.get("state", "closed")

    # 获取标签
    pr_number = pr.get("number")
    labels = fetch_pr_labels(repo, pr_number) if pr_number else []

    # 调用 evaluator
    rate, level = predict_success_rate(
        title, body, repo, REPO_ROOT,
        body=body, labels=labels, author=author, star_count=star_count,
        repo_merge_rate=repo_merge_rate, author_association=author_association,
    )

    # 判断预测结果
    predicted_merged = rate >= 0.50  # 阈值：50% 以上预测 merged
    actual_merged = merged

    return {
        "pr_number": pr_number,
        "title": title[:80],
        "author": author,
        "author_association": author_association,
        "is_bot": is_bot_author(author),
        "labels": labels,
        "predicted_rate": rate,
        "predicted_level": level,
        "predicted_merged": predicted_merged,
        "actual_merged": actual_merged,
        "state": state,
        "correct": predicted_merged == actual_merged,
    }


def cross_validate_repo(repo: str, limit: int = 20, verbose: bool = False) -> dict:
    """对单个仓库进行交叉验证"""
    # 获取仓库信息
    repo_info = fetch_repo_info(repo)
    if not repo_info:
        return {"repo": repo, "error": f"Cannot fetch repo info: {repo}"}

    star_count = repo_info.get("stargazers_count", 0)

    # 拉取 PR
    prs = fetch_prs(repo, state="closed", limit=limit)
    if not prs:
        return {"repo": repo, "error": f"No PRs found: {repo}"}

    # 计算仓库 merge 率（用于动态基线）
    closed_prs = [pr for pr in prs if pr.get("state") == "closed"]
    merged_count = sum(1 for pr in closed_prs if pr.get("merged_at") is not None)
    repo_merge_rate = merged_count / len(closed_prs) if closed_prs else 0.0

    # 评估每个 PR
    results = []
    for pr in prs:
        # 只评估已关闭的 PR（merged 或 rejected）
        if pr.get("state") != "closed":
            continue
        result = evaluate_pr(pr, repo, star_count, repo_merge_rate=repo_merge_rate)
        results.append(result)

        if verbose:
            status = "✅" if result["correct"] else "❌"
            bot = "🤖" if result["is_bot"] else "  "
            print(f"  {status} {bot} #{result['pr_number']:>6} "
                  f"({result['predicted_rate']:.0%} {result['predicted_level']}) "
                  f"{'merged' if result['actual_merged'] else 'rejected':>8} "
                  f"| {result['title'][:50]}")

    # 统计
    total = len(results)
    correct = sum(1 for r in results if r["correct"])
    merged_results = [r for r in results if r["actual_merged"]]
    rejected_results = [r for r in results if not r["actual_merged"]]

    merged_correct = sum(1 for r in merged_results if r["correct"])
    rejected_correct = sum(1 for r in rejected_results if r["correct"])

    # 误报/漏报
    false_positive = [r for r in results if r["predicted_merged"] and not r["actual_merged"]]
    false_negative = [r for r in results if not r["predicted_merged"] and r["actual_merged"]]

    return {
        "repo": repo,
        "star_count": star_count,
        "total": total,
        "correct": correct,
        "accuracy": correct / total if total > 0 else 0,
        "merged_total": len(merged_results),
        "merged_correct": merged_correct,
        "merged_recall": merged_correct / len(merged_results) if merged_results else 0,
        "rejected_total": len(rejected_results),
        "rejected_correct": rejected_correct,
        "rejected_recall": rejected_correct / len(rejected_results) if rejected_results else 0,
        "false_positive": len(false_positive),
        "false_negative": len(false_negative),
        "results": results,
    }


# ============================================================
# 报告生成
# ============================================================

def print_report(stats: dict) -> None:
    """打印验证报告"""
    if "error" in stats:
        print(f"❌ {stats['repo']}: {stats['error']}")
        return

    print(f"\n## {stats['repo']} ({stats['star_count']:,} ⭐)")
    print(f"| 指标 | 结果 |")
    print(f"|------|------|")
    print(f"| 总计 | {stats['total']} PR |")
    print(f"| 准确率 | **{stats['accuracy']:.1%}** ({stats['correct']}/{stats['total']}) |")
    print(f"| Merged 召回率 | {stats['merged_recall']:.1%} ({stats['merged_correct']}/{stats['merged_total']}) |")
    print(f"| Rejected 召回率 | {stats['rejected_recall']:.1%} ({stats['rejected_correct']}/{stats['rejected_total']}) |")
    print(f"| 误报 | {stats['false_positive']} |")
    print(f"| 漏报 | {stats['false_negative']} |")


def print_summary(all_stats: List[dict]) -> None:
    """打印汇总报告"""
    total = sum(s["total"] for s in all_stats if "error" not in s)
    correct = sum(s["correct"] for s in all_stats if "error" not in s)
    merged_total = sum(s["merged_total"] for s in all_stats if "error" not in s)
    merged_correct = sum(s["merged_correct"] for s in all_stats if "error" not in s)
    rejected_total = sum(s["rejected_total"] for s in all_stats if "error" not in s)
    rejected_correct = sum(s["rejected_correct"] for s in all_stats if "error" not in s)
    fp = sum(s["false_positive"] for s in all_stats if "error" not in s)
    fn = sum(s["false_negative"] for s in all_stats if "error" not in s)

    print("\n" + "=" * 60)
    print("## 汇总")
    print(f"| 指标 | 结果 |")
    print(f"|------|------|")
    print(f"| 总计 | {total} PR ({len([s for s in all_stats if 'error' not in s])} 仓库) |")
    print(f"| **整体准确率** | **{correct/total:.1%}** ({correct}/{total}) |")
    print(f"| Merged 召回率 | {merged_correct/merged_total:.1%} ({merged_correct}/{merged_total}) |")
    print(f"| Rejected 召回率 | {rejected_correct/rejected_total:.1%} ({rejected_correct}/{rejected_total}) |")
    print(f"| 误报 | {fp} |")
    print(f"| 漏报 | {fn} |")


# ============================================================
# 预定义测试集
# ============================================================

DEFAULT_REPOS = [
    # Large
    ("langchain-ai/langchain", 20),
    ("yt-dlp/yt-dlp", 20),
    ("microsoft/markitdown", 20),
    # Medium
    ("langchain-ai/langgraph", 20),
    ("onyx-dot-app/onyx", 20),
    ("danny-avila/LibreChat", 20),
    # Small
    ("goreleaser/nfpm", 20),
    ("python-jsonschema/jsonschema", 20),
    ("woodruffw/zizmor", 20),
]


def main():
    parser = argparse.ArgumentParser(description="PR Genius 交叉验证")
    parser.add_argument("--repo", "-r", help="单个仓库 (org/repo)")
    parser.add_argument("--limit", "-l", type=int, default=20, help="每个仓库拉取的 PR 数")
    parser.add_argument("--all", action="store_true", help="运行所有预定义仓库")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示每个 PR 的详情")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    args = parser.parse_args()

    if args.repo:
        repos = [(args.repo, args.limit)]
    elif args.all:
        repos = DEFAULT_REPOS
    else:
        parser.print_help()
        return 1

    all_stats = []
    for repo, limit in repos:
        print(f"\n🔍 验证 {repo} (limit={limit})...")
        stats = cross_validate_repo(repo, limit=limit, verbose=args.verbose)
        all_stats.append(stats)

        if args.json:
            print(json.dumps(stats, indent=2, ensure_ascii=False))
        else:
            print_report(stats)

    if not args.json and len(all_stats) > 1:
        print_summary(all_stats)

    return 0


if __name__ == "__main__":
    sys.exit(main())
