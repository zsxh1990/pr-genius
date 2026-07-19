#!/usr/bin/env python3
"""Merge contribai_replay.py results into docs/coach_fit_report.json.

克莱恩 v1.4.0 收尾 B: coach fit 226 → 241 cases (+15 contribai scenarios).

Mapping:
- contribai_replay scenario tier (high/medium/low) → predicted_risk
- anti_patterns_hit 含 contribai-* → "correct" catch (fit=correct)
- 没有命中 → "wrong" (fit=wrong)
- 当前 15/15 = 100% 命中, 所以 15 correct.

更新:
- total_cases: 226 → 241
- counts.correct: 89 → 104 (+15)
- accuracy_pct: 重新算 (104 / 241 = 43.2% — 注意 226→241, 分母变大, 率会降)
- by_repo: 加 4 个 contribai 测试仓库 (pallets/flask / pandas-dev/pandas /
  marimo-team/marimo / astral-sh/ty — 加 django / OpenBSD / HolmesGPT / maigret / MisakaNet)
- results: append 15 entries

Run:
    python3 scripts/merge_coach_fit_report.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

CONTIBAI_TO_ACTUAL_RISK = {
    "contribai-duplicate-pr": "high",
    "contribai-out-of-scope": "high",
    "contribai-not-a-real-bug": "high",
    "contribai-missing-tests": "high",
    "contribai-archived-repo": "high",
    "contribai-docs-pr-missing-quickstart": "high",
    "contribai-design-philosophy-mismatch": "high",
    "contribai-incomplete-readme-contributing": "high",
    "contribai-first-time-large-repo": "high",
    "contribai-breaking-change-no-migration": "high",
    "contribai-performance-benchmark-missing": "high",
    "contribai-ethical-review-failed": "high",
    "contribai-site-tos-violation": "high",
    "contribai-auto-generated-trash": "high",
    "contribai-needs-rfc-first": "high",
}


def _tier_to_risk(tier: str) -> str:
    """Map analyze_pr tier → fit report risk bucket."""
    return {
        "high_risk": "high",
        "medium_risk": "medium",
        "low_risk": "low",
    }.get(tier, "medium")


def _fit_score(predicted: str, actual: str) -> str:
    """3-bucket scoring — match coach_cases.py._fit_score logic."""
    if predicted == actual:
        return "correct"
    if {predicted, actual} == {"medium", "low"}:
        return "close"
    return "wrong"


def main():
    cf_path = REPO / "docs" / "coach_fit_report.json"
    cr_path = REPO / "docs" / "contribai_replay_report.json"

    cf = json.loads(cf_path.read_text(encoding="utf-8"))
    cr = json.loads(cr_path.read_text(encoding="utf-8"))

    contribai_results = cr.get("results", [])
    print(f"Existing coach_fit: {cf['total_cases']} cases, accuracy {cf['accuracy_pct']}%")
    print(f"ContribAI replay: {cr['total']} scenarios, {cr['hits']} hits ({cr['hit_rate']*100:.0f}%)")

    # Build key -> scenario lookup (because results from contribai_replay
    # don't include the repo field — need to map via the REPLAY_SCENARIOS)
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import contribai_replay  # noqa: E402
    scenarios_by_key = {s["key"]: s for s in contribai_replay.REPLAY_SCENARIOS}

    # 把 contribai scenario 转成 coach_fit 格式
    new_entries = []
    by_repo_updates = {}

    for i, scenario in enumerate(contribai_results):
        if "error" in scenario:
            continue
        scenario_key = scenario["key"]
        scenario_def = scenarios_by_key.get(scenario_key)
        if not scenario_def:
            print(f"⚠️  unknown key: {scenario_key}, skip")
            continue
        repo = scenario_def["repo"]
        tier = scenario.get("tier", "medium_risk")
        predicted_risk = _tier_to_risk(tier)
        # 实际风险应该是 high (每个 contribai 都是已知 close 原因)
        actual_risk = "high"
        # contribai scenario 是反模式回归测试, 不是真实 fit test:
        # fit='n/a' 不计入 accuracy (避免污染 83.2% 基线)
        # 但 by_repo total 仍然增加 (反映测试覆盖)
        fit = "n/a"
        # predicted_rate: high_risk → 0.30 (低), medium → 0.50, low → 0.70
        predicted_rate = {"high": 0.30, "medium": 0.50, "low": 0.70}[predicted_risk]

        new_entries.append({
            "id": f"contribai-replay-{i+1:02d}",
            "repo": repo,
            "pr_number": None,
            "title": scenario_key,
            "actual_outcome": "closed-not-merged",
            "predicted_risk": predicted_risk,
            "predicted_rate": predicted_rate,
            "actual_risk": actual_risk,
            "fit": fit,
            "anti_pattern_hits": scenario.get("anti_patterns_hit", []),
            "success_pattern_hits": [],
            "source": "contribai_replay_v1.4.0",
        })

        # 更新 by_repo (contribai 不计 correct/close/wrong, 但 total 增加)
        if repo not in by_repo_updates:
            by_repo_updates[repo] = {
                "correct": 0, "close": 0, "wrong": 0, "skip": 0, "total": 0
            }
        by_repo_updates[repo]["total"] += 1
        # fit='n/a' 不计 correct/close/wrong

    # 加到 results
    cf["results"].extend(new_entries)

    # 合并 by_repo
    for repo_key, counts in by_repo_updates.items():
        if repo_key not in cf["by_repo"]:
            cf["by_repo"][repo_key] = {
                "correct": 0, "close": 0, "wrong": 0, "skip": 0, "total": 0
            }
        for k, v in counts.items():
            cf["by_repo"][repo_key][k] = cf["by_repo"][repo_key].get(k, 0) + v

    # 更新 totals
    cf["total_cases"] = len(cf["results"])
    counts = cf["counts"]
    counts["correct"] = sum(1 for r in cf["results"] if r["fit"] == "correct")
    counts["close"] = sum(1 for r in cf["results"] if r["fit"] == "close")
    counts["wrong"] = sum(1 for r in cf["results"] if r["fit"] == "wrong")
    counts["skip"] = sum(1 for r in cf["results"] if r["fit"] == "skip")

    # 重新算 accuracy (跟 README metric 一致)
    # 公式: (correct + close) / (correct + close + wrong), skip 跳过
    # n/a (反模式回归测试) 不计入, 避免污架主 metric
    scorable = [r for r in cf["results"] if r["fit"] != "n/a"]
    correct_count = sum(1 for r in scorable if r["fit"] == "correct")
    close_count = sum(1 for r in scorable if r["fit"] == "close")
    wrong_count = sum(1 for r in scorable if r["fit"] == "wrong")
    denom = correct_count + close_count + wrong_count
    cf["accuracy_pct"] = round((correct_count + close_count) / denom * 100, 1) if denom else 0

    # 写回
    cf_path.write_text(json.dumps(cf, ensure_ascii=False, indent=2), encoding="utf-8")

    print()
    print(f"✅ Merged: {cf['total_cases']} cases (was 226, +15 contribai)")
    print(f"  counts: {counts}")
    print(f"  accuracy_pct: {cf['accuracy_pct']}%")
    print(f"  by_repo: {len(cf['by_repo'])} repos (was 28)")
    print(f"  written to: {cf_path.relative_to(REPO)}")


if __name__ == "__main__":
    main()
