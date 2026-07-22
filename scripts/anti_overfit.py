#!/usr/bin/env python3
"""Anti-overfit holdout validation — LORO + time-split 双指标 (lesson-19 代码化)

35 期众测任务1 评测反哺 (husk2 verification/anti_overfit.log):
- in-sample 准确率必须配 holdout 才有可信度 (lesson-19 hard gate)
- 单 LORO 不足以验证: 还需 time-split 验证未来数据不漏
- 设计学自 husk2 scripts/anti_overfit.py (v1.5.2, 2026-07-21)

两个独立验证:
1. LORO (Leave-One-Repo-Out):
   - 每仓 >= MIN_REPO_CASES 时, 留该仓全做 holdout, 其他仓作 rest
   - delta = held_out_accuracy - rest_accuracy
   - |delta| > 0.15 = potential overfit / biased

2. Time-split (PR-number 时间分割):
   - 每仓按 pr_number 升序 (older→newer) 切 80/20
   - 验证 newer (未来 PR) 准确率不低于 older (历史 PR)
   - newer_acc - older_acc < -0.20 = future leak / 数据漂移

用法:
    python3 scripts/anti_overfit.py                        # 读 docs/coach_fit_report.json, markdown 输出
    python3 scripts/anti_overfit.py --json                 # JSON 输出
    python3 scripts/anti_overfit.py --threshold 0.15       # 自定义 overfit 阈值
    python3 scripts/anti_overfit.py --report path.json     # 自定义输入
    python3 scripts/anti_overfit.py --write                # 同时写 data/anti_overfit_report.json

退出码:
    0 = pass (无 overfit / 无 time-split leak)
    1 = 有 overfit warnings (CI gate 用)
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPORT = REPO_ROOT / "docs" / "coach_fit_report.json"
WRITE_PATH = REPO_ROOT / "data" / "anti_overfit_report.json"

MIN_REPO_CASES = 5
TIME_SPLIT_FRAC = 0.8
DEFAULT_THRESHOLD = 0.15


# ============================================================
# 数据加载 + 准确率计算
# ============================================================

def load_cases(report: dict) -> list[dict]:
    """从 coach_fit_report.json 提取 results 数组.

    若 report 无 results 字段 (pr-genius 当前 fit_report.json 结构),
    用 by_repo + counts 反推近似 (acceptable approximation).
    """
    if "results" in report:
        return report["results"]
    # fallback: 从 by_repo 推
    cases = []
    for repo, stats in report.get("by_repo", {}).items():
        for _ in range(stats.get("correct", 0)):
            cases.append({"repo": repo, "fit": "correct"})
        for _ in range(stats.get("close", 0)):
            cases.append({"repo": repo, "fit": "close"})
        for _ in range(stats.get("wrong", 0)):
            cases.append({"repo": repo, "fit": "wrong"})
    return cases


def accuracy(cases: list[dict]) -> tuple[float, int, int, dict]:
    """Return (correct_rate, n_exact_correct, n_usable, fit_breakdown).

    pr-genius 语义: 'correct'+'close' 都算对 (close 是 one-tier-off),
    'wrong' 算错. 'skip'/'n/a' 跳过.
    """
    usable = [c for c in cases if c.get("fit") in ("correct", "close", "wrong")]
    if not usable:
        return 0.0, 0, 0, {}
    right = sum(1 for c in usable if c["fit"] in ("correct", "close"))
    correct = sum(1 for c in usable if c["fit"] == "correct")
    counts: dict[str, int] = defaultdict(int)
    for c in usable:
        counts[c["fit"]] += 1
    return right / len(usable), correct, len(usable), dict(counts)


# ============================================================
# 1. Leave-One-Repo-Out (LORO)
# ============================================================

def leave_one_repo_out(cases: list[dict]) -> dict[str, Any]:
    by_repo: dict[str, list[dict]] = defaultdict(list)
    for c in cases:
        by_repo[c["repo"]].append(c)

    overall_acc, overall_correct, overall_n, _ = accuracy(cases)
    repo_evals = []

    for repo, rc in sorted(by_repo.items(), key=lambda kv: -len(kv[1])):
        if len(rc) < MIN_REPO_CASES:
            continue
        rest = [c for c in cases if c["repo"] != repo]
        in_acc, _, _, _ = accuracy(rest)
        held_acc, held_correct, held_n, held_fit = accuracy(rc)
        delta = held_acc - in_acc
        repo_evals.append({
            "repo": repo,
            "n_cases": len(rc),
            "held_out_accuracy": round(held_acc, 4),
            "held_out_correct_exact": held_correct,
            "held_out_usable": held_n,
            "rest_accuracy": round(in_acc, 4),
            "delta_vs_rest": round(delta, 4),
            "fit_breakdown": held_fit,
        })

    held_accs = [e["held_out_accuracy"] for e in repo_evals]
    deltas = [e["delta_vs_rest"] for e in repo_evals]
    worst = min(repo_evals, key=lambda e: e["held_out_accuracy"]) if repo_evals else None
    best = max(repo_evals, key=lambda e: e["held_out_accuracy"]) if repo_evals else None

    return {
        "overall_in_sample_accuracy": round(overall_acc, 4),
        "overall_usable_cases": overall_n,
        "overall_exact_correct": overall_correct,
        "n_repos_evaluated": len(repo_evals),
        "mean_held_out_accuracy": round(statistics.mean(held_accs), 4) if held_accs else 0,
        "stdev_held_out_accuracy": round(statistics.pstdev(held_accs), 4) if len(held_accs) > 1 else 0,
        "mean_delta_vs_rest": round(statistics.mean(deltas), 4) if deltas else 0,
        "worst_repo": worst,
        "best_repo": best,
        "per_repo": repo_evals,
    }


# ============================================================
# 2. Time-split (PR-number 时间分割)
# ============================================================

def time_split(cases: list[dict]) -> dict[str, Any]:
    """每仓按 pr_number 升序切 80/20, 验证 newer 不低于 older."""
    by_repo: dict[str, list[dict]] = defaultdict(list)
    for c in cases:
        by_repo[c["repo"]].append(c)
    repo_splits = []
    pool_older, pool_newer = [], []

    for repo, rc in by_repo.items():
        if len(rc) < MIN_REPO_CASES:
            continue
        # pr_number 缺时回退到 None 排序 (按插入顺序)
        rc_sorted = sorted(rc, key=lambda c: c.get("pr_number") or 0)
        cut = int(len(rc_sorted) * TIME_SPLIT_FRAC)
        older, newer = rc_sorted[:cut], rc_sorted[cut:]
        if not newer:
            continue
        pool_older.extend(older)
        pool_newer.extend(newer)
        oa, _, _, _ = accuracy(older)
        na, _, _, _ = accuracy(newer)
        repo_splits.append({
            "repo": repo,
            "n_total": len(rc),
            "n_older": len(older),
            "n_newer": len(newer),
            "older_accuracy": round(oa, 4),
            "newer_accuracy": round(na, 4),
            "delta_newer_minus_older": round(na - oa, 4),
        })

    oa, _, _, _ = accuracy(pool_older)
    na, _, _, _ = accuracy(pool_newer)
    repos_with_large_drop = [
        s for s in repo_splits if s["delta_newer_minus_older"] < -0.20
    ]

    return {
        "pooled_older_accuracy": round(oa, 4),
        "pooled_newer_accuracy": round(na, 4),
        "pooled_delta": round(na - oa, 4),
        "pooled_older_cases": len(pool_older),
        "pooled_newer_cases": len(pool_newer),
        "n_repos_evaluated": len(repo_splits),
        "repos_with_large_drop": repos_with_large_drop,
        "per_repo": repo_splits,
    }


# ============================================================
# 报告汇总 + Markdown 渲染
# ============================================================

def render_markdown(loro: dict, tslice: dict, warnings: list[str], threshold: float) -> str:
    lines = [
        "# Anti-Overfit Holdout Validation (lesson-19)",
        "",
        f"Total labeled cases: **{loro['overall_usable_cases']}** "
        f"(threshold: |held-out drop| > {threshold:.0%} flags warning)",
        "",
        f"Overall in-sample accuracy (correct+close): **{loro['overall_in_sample_accuracy']:.1%}** "
        f"({loro['overall_exact_correct']} exact / {loro['overall_usable_cases']} usable)",
        "",
        "## 1. Leave-One-Repo-Out (LORO)",
        "",
        f"- Repos evaluated (>= {MIN_REPO_CASES} cases): **{loro['n_repos_evaluated']}**",
        f"- Mean held-out accuracy: **{loro['mean_held_out_accuracy']:.1%}** "
        f"(stdev {loro['stdev_held_out_accuracy']:.1%})",
        f"- Mean Δ held-out − rest: {loro['mean_delta_vs_rest']:+.1%}",
    ]
    if loro["worst_repo"]:
        w = loro["worst_repo"]
        lines.append(
            f"- Worst held-out: `{w['repo']}` = {w['held_out_accuracy']:.1%} "
            f"(rest = {w['rest_accuracy']:.1%}, Δ = {w['delta_vs_rest']:+.1%})"
        )
    if loro["best_repo"]:
        b = loro["best_repo"]
        lines.append(
            f"- Best held-out: `{b['repo']}` = {b['held_out_accuracy']:.1%}"
        )

    lines.extend([
        "",
        "## 2. Time-Split (PR-number 80/20)",
        "",
        f"- Pooled older accuracy: **{tslice['pooled_older_accuracy']:.1%}** ({tslice['pooled_older_cases']} cases)",
        f"- Pooled newer accuracy: **{tslice['pooled_newer_accuracy']:.1%}** ({tslice['pooled_newer_cases']} cases)",
        f"- Pooled Δ newer − older: {tslice['pooled_delta']:+.1%}",
        f"- Repos with |Δ| > 20%: {len(tslice['repos_with_large_drop'])}",
    ])
    if tslice["repos_with_large_drop"]:
        lines.append("- Time-split repos with large drop (>20%):")
        for r in tslice["repos_with_large_drop"]:
            lines.append(f"  - `{r['repo']}` Δ = {r['delta_newer_minus_older']:+.1%}")

    lines.extend([
        "",
        "## 3. Per-Repo Summary",
        "",
        "| repo | LORO held-out | rest | Δ | time-split newer | older | Δ new−old | verdict |",
        "|---|---|---|---|---|---|---|---|",
    ])
    # 把 LORO + time-split 按 repo 合并
    loro_by_repo = {e["repo"]: e for e in loro["per_repo"]}
    tslice_by_repo = {s["repo"]: s for s in tslice["per_repo"]}
    all_repos = sorted(set(loro_by_repo) | set(tslice_by_repo))
    for repo in all_repos:
        le = loro_by_repo.get(repo)
        te = tslice_by_repo.get(repo)
        loro_held = f"{le['held_out_accuracy']:.1%}" if le else "—"
        loro_rest = f"{le['rest_accuracy']:.1%}" if le else "—"
        loro_d = f"{le['delta_vs_rest']:+.1%}" if le else "—"
        t_new = f"{te['newer_accuracy']:.1%}" if te else "—"
        t_old = f"{te['older_accuracy']:.1%}" if te else "—"
        t_d = f"{te['delta_newer_minus_older']:+.1%}" if te else "—"

        verdict = "✅"
        if le and abs(le["delta_vs_rest"]) > threshold:
            verdict = "⚠️ LORO"
        if te and te["delta_newer_minus_older"] < -0.20:
            verdict = "⚠️ time"
        lines.append(f"| {repo} | {loro_held} | {loro_rest} | {loro_d} | {t_new} | {t_old} | {t_d} | {verdict} |")

    lines.extend([
        "",
        "## 4. Warnings",
        "",
    ])
    if warnings:
        for w in warnings:
            lines.append(f"- ⚠️ {w}")
    else:
        lines.append("- ✅ no overfit / no time-split leak detected")

    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description="pr-genius anti-overfit holdout (LORO + time-split)")
    p.add_argument("--report", type=Path, default=DEFAULT_REPORT,
                   help=f"coach_fit_report.json path (default: {DEFAULT_REPORT})")
    p.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD,
                   help=f"overfit drop threshold (default {DEFAULT_THRESHOLD})")
    p.add_argument("--json", action="store_true", help="JSON output instead of markdown")
    p.add_argument("--write", action="store_true",
                   help=f"also write {WRITE_PATH.relative_to(REPO_ROOT)}")
    args = p.parse_args()

    if not args.report.exists():
        print(f"ERROR: report not found: {args.report}", file=sys.stderr)
        return 2

    report = json.loads(args.report.read_text(encoding="utf-8"))
    cases = load_cases(report)
    loro = leave_one_repo_out(cases)
    tslice = time_split(cases)

    # 汇总 warnings
    warnings: list[str] = []
    thresh = args.threshold
    if loro["worst_repo"] and -loro["worst_repo"]["delta_vs_rest"] > thresh:
        w = loro["worst_repo"]
        warnings.append(
            f"LORO: repo {w['repo']} held-out accuracy drops "
            f"{-w['delta_vs_rest']:.1%} below rest (threshold {thresh:.0%})"
        )
    if tslice["pooled_delta"] < -thresh:
        warnings.append(
            f"Time-split: pooled newer accuracy drops {-tslice['pooled_delta']:.1%} below older"
        )
    for r in tslice["repos_with_large_drop"]:
        warnings.append(
            f"Time-split: {r['repo']} newer accuracy drops {-r['delta_newer_minus_older']:.1%}"
        )

    if args.json:
        payload = {
            "schema_version": "anti-overfit-v1",
            "generated_from": str(args.report.relative_to(REPO_ROOT)),
            "n_cases_total": len(cases),
            "threshold_for_warning": thresh,
            "pass": len(warnings) == 0,
            "warnings": warnings,
            "leave_one_repo_out": loro,
            "time_split": tslice,
        }
        out_text = json.dumps(payload, indent=2, ensure_ascii=False)
    else:
        out_text = render_markdown(loro, tslice, warnings, thresh)

    if args.write:
        payload = {
            "schema_version": "anti-overfit-v1",
            "generated_from": str(args.report.relative_to(REPO_ROOT)),
            "n_cases_total": len(cases),
            "threshold_for_warning": thresh,
            "pass": len(warnings) == 0,
            "warnings": warnings,
            "leave_one_repo_out": loro,
            "time_split": tslice,
        }
        WRITE_PATH.parent.mkdir(parents=True, exist_ok=True)
        WRITE_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Wrote {WRITE_PATH}")

    print(out_text)
    return 0 if not warnings else 1


if __name__ == "__main__":
    sys.exit(main())
