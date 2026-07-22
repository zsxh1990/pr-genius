"""Check 7: policy freshness drift detection (v1.5.2, 2026-07-21).

Maintainer Policies (`docs/policies/<org>-<repo>.md`, type=Maintainer Policy)
and Repo Profiles (`<org>-<repo>/index.md`, type=Repo Profile) carry a date:
- policy: frontmatter `updated` (YYYY-MM-DD)
- profile: frontmatter `analyzed_at` (YYYY-MM-DD)

Any policy/profile whose date is older than POLICY_MAX_AGE_DAYS (default 90) is
flagged as stale — maintainer behavior changes (CONTRIBUTING.md is edited,
bots are added/removed, CLA requirements flip) and stale policies give bad
advice. This is a *warning*, not an error, so it doesn't fail --strict until
the maintainer has had time to re-verify.
"""
from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

POLICY_MAX_AGE_DAYS = 90


def _parse_date(value) -> date | None:
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(value[:19] if "T" in value or " " in value else value, fmt).date()
            except ValueError:
                continue
        try:
            return datetime.fromisoformat(value.replace("Z", "")).date()
        except (ValueError, AttributeError):
            return None
    return None


def check_policy_freshness(
    files: list[Path],
    parse_frontmatter,
    warnings: list[str],
    errors: list[str],
    ROOT: Path,
    today: date | None = None,
    max_age_days: int = POLICY_MAX_AGE_DAYS,
) -> None:
    """Flag policies/profiles older than max_age_days.

    - Missing date field → warning (can't verify freshness).
    - Date present but older than max_age_days → warning.
    - Malformed date → warning.
    - Fresh policy → silent.
    """
    print(f"[Check 7] Policy / profile freshness (warn if >{max_age_days}d old or undated)")
    today = today or date.today()
    stale = 0
    undated = 0
    fresh = 0
    for f in files:
        text = f.read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(text)
        if fm is None or "_error" in fm:
            continue
        t = fm.get("type")
        if t == "Maintainer Policy":
            date_field = "updated"
            kind = "policy"
        elif t == "Repo Profile":
            date_field = "analyzed_at"
            kind = "profile"
        else:
            continue
        raw = fm.get(date_field)
        d = _parse_date(raw)
        if d is None:
            undated += 1
            warnings.append(
                f"{f.relative_to(ROOT)}: {kind} missing/ill-formed `{date_field}`; cannot verify freshness"
            )
            continue
        age = (today - d).days
        if age > max_age_days:
            stale += 1
            warnings.append(
                f"{f.relative_to(ROOT)}: {kind} last updated {d} ({age}d > {max_age_days}d threshold); re-verify"
            )
        else:
            fresh += 1
    print(f"   policies/profiles scanned: fresh={fresh} stale={stale} undated={undated} (today={today.isoformat()})")
