#!/usr/bin/env python3
"""Coach all cases — compare PR Genius predictions vs actual outcomes.

Runs pr-genius eval on each case, then compares the predicted risk level
(🟢low / 🟡medium / 🔴high) against the actual outcome (merged / closed / open).

Usage:
    python3 scripts/coach_cases.py
    python3 scripts/coach_cases.py --json
    python3 scripts/coach_cases.py --limit 20
"""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def _get_merge_rate(repo: str) -> float:
    """Read external_merge_rate from repo profile."""
    profile_dir = REPO / repo.replace("/", "-")
    index_file = profile_dir / "index.md"
    if not index_file.exists():
        return 0.0
    try:
        import re
        text = index_file.read_text()
        m = re.search(r'external_merge_rate:\s*([\d.]+)', text)
        return float(m.group(1)) if m else 0.0
    except (ValueError, AttributeError):
        return 0.0


def _get_star_count(repo: str) -> int:
    """Read star count from repo profile."""
    profile_dir = REPO / repo.replace("/", "-")
    index_file = profile_dir / "index.md"
    if not index_file.exists():
        return 0
    try:
        import re
        text = index_file.read_text()
        m = re.search(r'^star:\s*(\d+)', text, re.MULTILINE)
        return int(m.group(1)) if m else 0
    except (ValueError, AttributeError):
        return 0


def _run_eval(title: str, repo: str, body: str = "") -> dict:
    """Run pr-genius eval and return parsed result."""
    merge_rate = _get_merge_rate(repo)
    star_count = _get_star_count(repo)
    cmd = ["python3", "-m", "prgenius", "eval", title, "--repo", repo]
    if merge_rate > 0:
        cmd += ["--repo-merge-rate", str(merge_rate)]
    if star_count > 0:
        cmd += ["--star-count", str(star_count)]
    if body:
        cmd += ["--description", body[:500]]

    try:
        import os
        env = os.environ.copy()
        env["PYTHONPATH"] = str(REPO / "prgenius" / "src") + ":" + env.get("PYTHONPATH", "")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15, cwd=REPO, env=env)
        output = result.stdout + result.stderr

        # Parse risk level from output
        # Format 1: "成功率预测: 50% (中)"
        # Format 2: "🟡 风险等级: 中风险"
        import re
        risk = "unknown"
        success_rate = None

        rate_match = re.search(r'成功率预测:\s*(\d+)%', output)
        if rate_match:
            success_rate = int(rate_match.group(1))
            if success_rate >= 70:
                risk = "low"
            elif success_rate >= 40:
                risk = "medium"
            else:
                risk = "high"

        # Format 2: check risk level icons
        if risk == "unknown":
            if "🟢" in output or "低风险" in output:
                risk = "low"
            elif "🟡" in output or "中风险" in output:
                risk = "medium"
            elif "🔴" in output or "高风险" in output:
                risk = "high"

        # Extract anti-pattern hits
        anti_hits = []
        if "命中" in output:
            for line in output.split("\n"):
                if "命中" in line and "✅" not in line:
                    anti_hits.append(line.strip("- "))

        # Extract success pattern matches
        success_hits = []
        if "匹配" in output:
            for line in output.split("\n"):
                if "匹配" in line and "❌" not in line:
                    success_hits.append(line.strip("- "))

        return {
            "predicted_risk": risk,
            "predicted_rate": success_rate,
            "anti_pattern_hits": anti_hits,
            "success_pattern_hits": success_hits,
            "raw_output": output[:400],
        }
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return {"predicted_risk": "error", "predicted_rate": None, "anti_pattern_hits": [], "success_pattern_hits": [], "raw_output": str(e)[:200]}


def _actual_outcome(case: dict) -> str:
    """Map case category to outcome."""
    cat = case.get("category", "")
    if cat.startswith("merged"):
        return "merged"
    elif cat.startswith("closed"):
        return "closed"
    else:
        return "open"


def _outcome_risk(outcome: str) -> str:
    """Map actual outcome to risk level for comparison."""
    if outcome == "merged":
        return "low"      # merged = good outcome
    elif outcome == "closed":
        return "high"     # closed without merge = bad outcome
    else:
        return "medium"   # open/pending = uncertain


def _fit_score(predicted: str, actual_outcome: str) -> str:
    """Score the prediction fit."""
    actual = _outcome_risk(actual_outcome)

    if predicted == "unknown" or predicted == "error":
        return "skip"

    # Perfect fit
    if predicted == actual:
        return "correct"

    # Close fit (off by one level)
    if (predicted == "low" and actual == "medium") or (predicted == "medium" and actual == "low"):
        return "close"
    if (predicted == "high" and actual == "medium") or (predicted == "medium" and actual == "high"):
        return "close"

    # Wrong (predicted low but actually closed, or predicted high but actually merged)
    return "wrong"


def main():
    json_mode = "--json" in sys.argv
    limit = 100
    for i, arg in enumerate(sys.argv):
        if arg == "--limit" and i + 1 < len(sys.argv):
            limit = int(sys.argv[i + 1])

    # Load all cases
    cases = []
    for subdir in ["success-patterns", "anti-patterns", "review-cases"]:
        dir_path = REPO / subdir
        if not dir_path.exists():
            continue
        for f in sorted(dir_path.glob("*.json"))[:limit]:
            try:
                case = json.loads(f.read_text())
                case["_source_dir"] = subdir
                cases.append(case)
            except (json.JSONDecodeError, KeyError):
                continue

    if not json_mode:
        print(f"PR Genius Coach — Predicted vs Actual")
        print(f"Cases: {len(cases)}")
        print()

    results = []
    counts = {"correct": 0, "close": 0, "wrong": 0, "skip": 0}
    by_repo = {}

    for i, case in enumerate(cases):
        title = case.get("title", "")
        repo = case.get("repo", "")
        actual = _actual_outcome(case)

        eval_result = _run_eval(title, repo)
        fit = _fit_score(eval_result["predicted_risk"], actual)

        counts[fit] = counts.get(fit, 0) + 1

        entry = {
            "id": case.get("id", ""),
            "repo": repo,
            "pr_number": case.get("pr_number", 0),
            "title": title[:60],
            "actual_outcome": actual,
            "predicted_risk": eval_result["predicted_risk"],
            "predicted_rate": eval_result.get("predicted_rate"),
            "actual_risk": _outcome_risk(actual),
            "fit": fit,
            "anti_pattern_hits": eval_result.get("anti_pattern_hits", []),
            "success_pattern_hits": eval_result.get("success_pattern_hits", []),
        }
        results.append(entry)

        # Track by repo
        if repo not in by_repo:
            by_repo[repo] = {"correct": 0, "close": 0, "wrong": 0, "skip": 0, "total": 0}
        by_repo[repo][fit] = by_repo[repo].get(fit, 0) + 1
        by_repo[repo]["total"] += 1

        if not json_mode:
            marker = {"correct": "✅", "close": "🟡", "wrong": "❌", "skip": "⏭️"}.get(fit, "?")
            print(f"  {marker} [{actual:>6}] predicted={eval_result['predicted_risk']:>6} | {repo[:25]:25} #{case.get('pr_number', '?'):>6} {title[:45]}")

    # Summary
    total_scored = counts["correct"] + counts["close"] + counts["wrong"]
    accuracy = (counts["correct"] + counts["close"]) / total_scored * 100 if total_scored else 0

    if not json_mode:
        print(f"\n{'='*70}")
        print(f"Fit Summary")
        print(f"{'='*70}")
        print(f"  ✅ Correct:   {counts['correct']:>3} ({counts['correct']/max(total_scored,1)*100:.0f}%)")
        print(f"  🟡 Close:     {counts['close']:>3} ({counts['close']/max(total_scored,1)*100:.0f}%)")
        print(f"  ❌ Wrong:     {counts['wrong']:>3} ({counts['wrong']/max(total_scored,1)*100:.0f}%)")
        print(f"  ⏭️  Skip:      {counts['skip']:>3}")
        print(f"\n  Accuracy (correct+close): {accuracy:.0f}%")

        # By repo
        print(f"\n--- By Repo ---")
        print(f"  {'Repo':30} {'Total':>5} {'✅':>3} {'🟡':>3} {'❌':>3} {'Acc':>5}")
        print(f"  {'-'*30} {'-'*5} {'-'*3} {'-'*3} {'-'*3} {'-'*5}")
        for repo, stats in sorted(by_repo.items(), key=lambda x: -x[1]["total"]):
            scored = stats["correct"] + stats["close"] + stats["wrong"]
            acc = (stats["correct"] + stats["close"]) / max(scored, 1) * 100
            print(f"  {repo[:30]:30} {stats['total']:>5} {stats['correct']:>3} {stats['close']:>3} {stats['wrong']:>3} {acc:>4.0f}%")

    report = {
        "total_cases": len(cases),
        "counts": counts,
        "accuracy_pct": round(accuracy, 1),
        "by_repo": {k: v for k, v in sorted(by_repo.items(), key=lambda x: -x[1]["total"])},
        "results": results,
    }

    if json_mode:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        report_path = REPO / "docs" / "coach_fit_report.json"
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
        print(f"\nReport: {report_path}")


if __name__ == "__main__":
    main()
