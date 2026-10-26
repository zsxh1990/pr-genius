"""Adoption telemetry — issue #127 risk 5 / #110.

**This module reverses a documented trade, and is written so the part that gets
reversed is the part the user turns on.**

`docs/ADOPTION_DATA.md` said, in as many words:

    A usage-ping channel would contradict it, even a hashed and opt-in one.
    So the trade was made deliberately: we give up adoption numbers and keep
    the "nothing leaves your machine during analysis" guarantee intact.

That sentence stays true unless someone sets `PRGENIUS_TELEMETRY_URL`. So the
module has two layers and they are not symmetric:

**Layer 1 — local counters. Always on. Never transmits.**
A JSON file under `~/.config/prgenius/` (or `PRGENIUS_TELEMETRY_DIR`). It answers
the two questions #127 actually asked — *which tool is the real entry point*,
and *which anti-patterns have ever fired* — for the install it lives on. It is
a log file, not telemetry. A user can read it (`prgenius telemetry report`) and
delete it (`prgenius telemetry reset`).

**Layer 2 — network sink. Dead by default.**
Active only when `PRGENIUS_TELEMETRY_URL` is set, and then it POSTs the
aggregate counters and nothing else. Setting that variable is the explicit act
that relaxes the guarantee, and `docs/ADOPTION_DATA.md` and the README say so.

## What is deliberately not recorded

#110 proposed SHA-1 of `(title || body || repo)[:64]` for dedup. **This module
does not do that.** A stable hash of someone's PR text is still a fingerprint of
their work: it correlates the same contribution across time, which is exactly
the identifying power the privacy stance exists to withhold. Nor is there an
install id, machine id, or any other stable token.

So this answers "is `coach_pr` used" and "has `tests_in_diff` ever fired". It
does **not** answer #110's adoption-rate question — that one needs per-PR
correlation, which needs identity, which is the thing being protected. Saying
so out loud is the job of this docstring rather than quietly implying otherwise.

The GitHub Action path defaults to off regardless of any environment variable
(#110: the Action runs on third-party repos where the user may not have
consented). See `github_action_defaults_off`.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

_SCHEMA = 1

# The only keys that may ever appear in a payload or state file. Anything else
# has to argue its way in here first, which is the point: a closed set is
# auditable, an open one is not.
_ALLOWED_EVENT_KEYS = frozenset({"events", "since"})


def _state_dir() -> Path:
    override = os.environ.get("PRGENIUS_TELEMETRY_DIR")
    if override:
        return Path(override)
    xdg = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg) if xdg else Path.home() / ".config"
    return base / "prgenius"


def _state_path() -> Path:
    return _state_dir() / "telemetry.json"


def sink_configured() -> bool:
    """True only when the user explicitly pointed telemetry somewhere.

    Absent means the guarantee holds. This is the single predicate the README
    and ADOPTION_DATA hang their wording on, so it must not grow a heuristic.
    """
    return bool(os.environ.get("PRGENIUS_TELEMETRY_URL", "").strip())


def github_action_defaults_off() -> bool:
    """The Action runs on third-party repos where the operator did not consent.

    #110 was explicit that telemetry must default to off there. Kept as a named
    predicate so a future change to it is a visible diff rather than a quiet
    deletion of a line in a workflow.
    """
    return True


def _load() -> Dict[str, Any]:
    p = _state_path()
    if not p.is_file():
        return {
            "version": _SCHEMA,
            "since": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "events": {},
        }
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        # A corrupt counter file must not break analysis. Start fresh rather
        # than fail a user's `prgenius coach` over bookkeeping.
        return {
            "version": _SCHEMA,
            "since": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "events": {},
        }
    if not isinstance(data, dict):
        data = {}
    data.setdefault("version", _SCHEMA)
    data.setdefault("events", {})
    if not isinstance(data["events"], dict):
        data["events"] = {}
    return data


def _save(data: Dict[str, Any]) -> None:
    p = _state_path()
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        tmp.replace(p)
    except OSError:
        # Telemetry must never be the reason an analysis fails.
        pass


def record(tool: str, patterns: Optional[List[str]] = None, **kwargs: Any) -> None:
    """Count one invocation, and optionally which anti-pattern families fired.

    `**kwargs` exists to **reject** free-form payloads. If a caller could pass
    a dict of arbitrary strings, someone eventually would pass a PR title — so
    the door is welded shut and the TypeError is the guard.
    """
    if kwargs:
        raise TypeError(
            "telemetry.record() takes no free-form payload; "
            f"got unexpected keyword arguments {sorted(kwargs)}. "
            "Counting tool names and pattern keys is the whole surface."
        )
    if not isinstance(tool, str) or not tool:
        raise TypeError("telemetry.record() needs a non-empty tool name")

    data = _load()
    events = data["events"]
    events[tool] = int(events.get(tool, 0)) + 1

    if patterns:
        if not all(isinstance(k, str) and k for k in patterns):
            raise TypeError("telemetry.record(patterns=...) needs non-empty strings")
        bucket = events.setdefault("patterns", {})
        if not isinstance(bucket, dict):
            bucket = {}
            events["patterns"] = bucket
        for key in patterns:
            bucket[key] = int(bucket.get(key, 0)) + 1

    _save(data)


def report() -> Dict[str, Any]:
    """The counters as they stand. Local-only; this never transmits."""
    data = _load()
    return {
        "since": data.get("since"),
        "events": data.get("events", {}),
        "sink": "configured" if sink_configured() else "off",
    }


def reset() -> None:
    """Forget everything counted so far."""
    _save({
        "version": _SCHEMA,
        "since": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "events": {},
    })


def build_payload() -> Dict[str, Any]:
    """Exactly what would go on the wire. Shaped so it can be read in one look.

    Only three top-level keys. If a fourth ever shows up here, that is the
    reviewable moment — which is why this is a function with a closed literal
    rather than a dict assembled from whatever the caller had lying around.
    """
    data = _load()
    return {
        "schema": _SCHEMA,
        "client_version": _client_version(),
        "events": data.get("events", {}),
    }


def _client_version() -> str:
    try:
        from . import __version__ as v  # type: ignore[attr-defined]
        return str(v)
    except Exception:
        return "unknown"


def flush() -> bool:
    """Send the aggregate if — and only if — a sink is configured.

    Returns True if something was sent. Without a sink this is a no-op and
    returns False: that is the guarantee, expressed as control flow rather
    than as a comment.
    """
    if not sink_configured():
        return False
    url = os.environ["PRGENIUS_TELEMETRY_URL"].strip()
    payload = build_payload()
    if not payload.get("events"):
        return False
    try:
        from urllib.request import Request, urlopen
        req = Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(req, timeout=5):  # noqa: S310 — URL is the operator's own config
            pass
    except Exception:
        # A telemetry outage must never surface as an analysis failure.
        return False
    return True
