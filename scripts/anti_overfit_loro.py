#!/usr/bin/env python3
"""Anti-overfit LORO (Leave-One-Repo-Out) 验证 — lesson-19 代码化

35 期众测任务1 评测反哺 (husk2 verification/anti_overfit.log):
- in-sample 83.7% 必须配 LORO holdout 才有可信度
- 单 repo holdout accuracy drops > 15% = potential overfit
- 输出 4 类: mean / stdev / min / max + 已知偏差仓清单

用法:
    python3 scripts/anti_overfit_loro.py                    # 读默认 docs/coach_fit_report.json
    python3 scripts/anti_overfit_loro.py --json             # JSON 输出
    python3 scripts/anti_overfit_loro.py --threshold 0.15   # 自定义 overfit 阈值
    python3 scripts/anti_overfit_loro.py --report path.json # 自定义输入

输出:
- stdout: 表格 (markdown 格式)
- data/anti_overfit_loro_report.json (机器可读, 仅当 --json 或自动写入)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPORT = REPO_ROOT / "docs" / "coach_fit_report.json"


def loro_per_repo(report: dict) -> list[dict]:
    """每仓 leave-one-repo-out holdout accuracy.

    Args:
        report: coach_fit_report.json dict, 必含 by_repo.<repo>.{correct, close, wrong, total}

    Returns:
        list of {repo, total, accuracy_pct, holdout_accuracy_pct, drop_pct}
    """
    by_repo = report.get("by_repo", {})
    grand_total = report.get("total_cases", sum(
        v.get("total", 0) for v in by_repo.values()
    ))
    # pr-genius 语义: "correct" = 预测 pass + 真 merged
    #              "close"  = 预测 close + 真 closed  ← 也是对的
    #              "wrong"  = 预测错 (pass+close / close+pass / etc.)
    # in-sample accuracy_pct = (correct + close) / total
    # 跟 coach_fit_report.json 的 accuracy_pct 字段计算一致
    counts = report.get("counts", {})
    grand_correct = counts.get("correct", 0) + counts.get("close", 0)
    in_sample_acc = (grand_correct / grand_total * 100) if grand_total else 0

    rows = []
    for repo, stats in sorted(by_repo.items(), key=lambda kv: -kv[1].get("total", 0)):
        total = stats.get("total", 0)
        # 该仓 in-sample accuracy_pct: (correct + close) / total
        repo_correct = stats.get("correct", 0) + stats.get("close", 0)
        # holdout 视角: 把该仓 PR 排除后,其他仓整体 (correct+close)/total
        other_total = grand_total - total
        other_correct = grand_correct - repo_correct
        holdout_acc = (other_correct / other_total * 100) if other_total else 0
        drop = in_sample_acc - holdout_acc
        rows.append({
            "repo": repo,
            "total": total,
            "correct": repo_correct,
            "accuracy_pct": round(repo_correct / total * 100, 1) if total else 0,
            "holdout_accuracy_pct": round(holdout_acc, 1),
            "drop_pct": round(drop, 1),
        })
    return rows


def summarize(rows: list[dict], threshold: float = 15.0) -> dict:
    """汇总 LORO 结果 + 判定 overfit 风险."""
    if not rows:
        return {"mean_drop_pct": 0, "stdev_drop_pct": 0, "overfit_repos": [], "biased_repos": []}

    drops = [r["drop_pct"] for r in rows]
    n = len(drops)
    mean = sum(drops) / n
    variance = sum((d - mean) ** 2 for d in drops) / n
    stdev = variance ** 0.5

    # drop > threshold = potential overfit
    overfit_repos = [r["repo"] for r in rows if r["drop_pct"] > threshold]
    # drop < -threshold = 这个仓风格特殊 (biased)
    biased_repos = [r["repo"] for r in rows if r["drop_pct"] < -threshold]

    return {
        "mean_drop_pct": round(mean, 1),
        "stdev_drop_pct": round(stdev, 1),
        "max_drop_pct": round(max(drops), 1),
        "min_drop_pct": round(min(drops), 1),
        "overfit_repos": overfit_repos,
        "biased_repos": biased_repos,
        "threshold_pct": threshold,
    }


def render_markdown(rows: list[dict], summary: dict, in_sample: float) -> str:
    """生成 markdown 表格."""
    lines = [
        f"# Anti-Overfit LORO Report (lesson-19)",
        f"",
        f"in-sample accuracy: **{in_sample:.1f}%**",
        f"holdout threshold: drop > **{summary['threshold_pct']}%** = potential overfit",
        f"",
        f"## Summary",
        f"",
        f"| metric | value |",
        f"|---|---|",
        f"| mean_drop_pct | {summary['mean_drop_pct']}% |",
        f"| stdev_drop_pct | {summary['stdev_drop_pct']}% |",
        f"| max_drop_pct | {summary['max_drop_pct']}% |",
        f"| min_drop_pct | {summary['min_drop_pct']}% |",
        f"| overfit_repos ({len(summary['overfit_repos'])}) | {', '.join(summary['overfit_repos']) or 'none'} |",
        f"| biased_repos ({len(summary['biased_repos'])}) | {', '.join(summary['biased_repos']) or 'none'} |",
        f"",
        f"## Per-Repo Holdout",
        f"",
        f"| repo | total | correct | in-sample % | holdout % | drop % | verdict |",
        f"|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        verdict = "⚠️ OVERFIT" if r["drop_pct"] > summary["threshold_pct"] else (
            "🔵 biased" if r["drop_pct"] < -summary["threshold_pct"] else "✅ ok"
        )
        lines.append(
            f"| {r['repo']} | {r['total']} | {r['correct']} | "
            f"{r['accuracy_pct']:.1f} | {r['holdout_accuracy_pct']:.1f} | "
            f"{r['drop_pct']:+.1f} | {verdict} |"
        )
    lines.extend([
        "",
        f"## How to read",
        f"",
        f"- `in-sample %`: 该仓内 PR evaluator 自身判断的准确率",
        f"- `holdout %`: 把该仓 PR 排除后,其他仓整体正确率(leave-one-repo-out 估计)",
        f"- `drop %`: in-sample - holdout. 正数 = overfit (该仓表现拉高整体); "
        f"负数 = biased (该仓风格特殊)",
        f"- overfit_repos 应进 `data/known_biased_repos.json` 显式声明",
        f"- biased_repos 同样进,但属\"已知风险\"而非\"失败\"",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description="Anti-overfit LORO (lesson-19)")
    p.add_argument("--report", type=Path, default=DEFAULT_REPORT,
                   help=f"coach_fit_report.json path (default: {DEFAULT_REPORT})")
    p.add_argument("--threshold", type=float, default=15.0,
                   help="overfit drop threshold in pct (default: 15)")
    p.add_argument("--json", action="store_true", help="JSON output instead of markdown")
    p.add_argument("--out", type=Path, default=None,
                   help="write report to this file (default: stdout)")
    args = p.parse_args()

    if not args.report.exists():
        print(f"ERROR: report not found: {args.report}", file=sys.stderr)
        return 2

    report = json.loads(args.report.read_text(encoding="utf-8"))
    rows = loro_per_repo(report)
    summary = summarize(rows, threshold=args.threshold)

    grand_total = report.get("total_cases", 0)
    # pr-genius accuracy_pct = (correct + close) / total
    counts = report.get("counts", {})
    grand_correct = counts.get("correct", 0) + counts.get("close", 0)
    in_sample = (grand_correct / grand_total * 100) if grand_total else 0

    if args.json:
        payload = {
            "in_sample_accuracy_pct": round(in_sample, 1),
            "summary": summary,
            "per_repo": rows,
        }
        out_text = json.dumps(payload, indent=2, ensure_ascii=False)
    else:
        out_text = render_markdown(rows, summary, in_sample)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(out_text, encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        print(out_text)

    # exit code: 0 = 无 overfit, 1 = 有 overfit repo (供 CI gate)
    return 1 if summary["overfit_repos"] else 0


if __name__ == "__main__":
    sys.exit(main())
