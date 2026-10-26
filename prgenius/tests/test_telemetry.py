"""Adoption telemetry — issue #127 risk 5 / #110.

This is a **reversal** of a documented trade, so the tests here are mostly
about the promise that is *not* broken. `docs/ADOPTION_DATA.md` said:

    A usage-ping channel would contradict it, even a hashed and opt-in one.
    So the trade was made deliberately: we give up adoption numbers and keep
    the "nothing leaves your machine during analysis" guarantee intact.

The design keeps that sentence true by default and makes relaxing it an
explicit, separate act:

* **Layer 1 — local counters.** Always on. Answers "which tools are used, which
  anti-patterns have ever fired" for *this* install. Nothing is transmitted,
  ever. This is not telemetry in the network sense; it is a log file.
* **Layer 2 — network sink.** Dead unless `PRGENIUS_TELEMETRY_URL` is set.
  Absent by default, and configuring it is what relaxes the guarantee.

Nothing recorded carries user content: no PR title, body, repo, author, diff,
and no hash of any of them. #110 proposed SHA-1 of the input args for dedup;
this deliberately does not, because a stable hash of someone's PR text is still
a fingerprint of their work.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from prgenius import telemetry


@pytest.fixture(autouse=True)
def isolated_state(tmp_path, monkeypatch):
    """Point every layer at a scratch dir so tests never touch a real install."""
    monkeypatch.setenv("PRGENIUS_TELEMETRY_DIR", str(tmp_path))
    monkeypatch.delenv("PRGENIUS_TELEMETRY_URL", raising=False)
    yield tmp_path


class TestTheGuaranteeStillHolds:
    def test_no_network_sink_by_default(self):
        assert telemetry.sink_configured() is False, (
            "docs/ADOPTION_DATA.md promised nothing leaves the machine; "
            "a default-on sink would reverse that promise silently"
        )

    def test_flush_is_a_noop_without_a_sink(self):
        telemetry.record("analyze_pr")
        telemetry.flush()  # must not raise, must not send
        assert telemetry.sink_configured() is False

    def test_analysing_records_locally_and_sends_nothing(self):
        telemetry.record("coach_pr", patterns=["tests_in_diff"])
        st = telemetry.report()
        assert st["events"]["coach_pr"] >= 1
        assert "tests_in_diff" in st["events"]["patterns"]
        # The only artifact is a file on this machine.
        assert set(p.name for p in Path(str(telemetry._state_dir())).iterdir()) <= {"telemetry.json"}


class TestNothingRecordedIsUserContent:
    def test_record_rejects_freeform_payloads(self):
        # The API must make it hard to smuggle a PR title in. If someone can
        # pass arbitrary strings, someone eventually will.
        with pytest.raises(TypeError):
            telemetry.record("analyze_pr", payload={"title": "fix: secrets in prod"})

    def test_the_state_file_carries_no_pr_identifiers(self, tmp_path):
        telemetry.record("analyze_pr", patterns=["pip install"])
        raw = (tmp_path / "telemetry.json").read_text(encoding="utf-8")
        blob = json.loads(raw)
        flat = json.dumps(blob)
        for forbidden in ("title", "body", "repo", "author", "diff", "sha1", "hash", "user_id"):
            assert forbidden not in flat.lower(), (
                f"state file must not carry {forbidden!r}: {flat}"
            )

    def test_pattern_keys_are_recorded_not_pattern_content(self):
        telemetry.record("analyze_pr", patterns=["install_surface", "secret_shaped"])
        st = telemetry.report()
        assert set(st["events"]["patterns"]) <= {"install_surface", "secret_shaped"}


class TestTheOptInIsExplicit:
    def test_setting_a_sink_is_what_relaxes_the_guarantee(self, monkeypatch):
        monkeypatch.setenv("PRGENIUS_TELEMETRY_URL", "https://example.invalid/collect")
        assert telemetry.sink_configured() is True

    def test_the_payload_is_the_aggregate_and_nothing_else(self, monkeypatch):
        monkeypatch.setenv("PRGENIUS_TELEMETRY_URL", "https://example.invalid/collect")
        telemetry.record("analyze_pr", patterns=["install_surface"])
        telemetry.record("analyze_pr", patterns=["install_surface"])
        telemetry.record("coach_pr")
        body = telemetry.build_payload()
        assert set(body.keys()) <= {"schema", "client_version", "events"}, body.keys()
        assert body["events"]["analyze_pr"] == 2
        assert body["events"]["coach_pr"] == 1
        assert body["events"]["patterns"]["install_surface"] == 2

    def test_no_identifier_is_sent(self, monkeypatch):
        monkeypatch.setenv("PRGENIUS_TELEMETRY_URL", "https://example.invalid/collect")
        telemetry.record("analyze_pr")
        flat = json.dumps(telemetry.build_payload()).lower()
        for forbidden in ("user", "install_id", "machine", "uuid", "email", "token"):
            assert forbidden not in flat, f"payload must not identify anyone: {flat}"

    def test_the_github_action_defaults_to_off(self):
        # #110 was explicit: the Action runs on third-party repos where the
        # user may not have consented, so it must default to no telemetry.
        assert telemetry.github_action_defaults_off() is True


class TestTheUserCanSeeAndClearIt:
    def test_report_is_readable(self):
        telemetry.record("analyze_pr")
        st = telemetry.report()
        assert "events" in st and "since" in st

    def test_reset_clears_the_counters(self):
        telemetry.record("analyze_pr")
        telemetry.reset()
        assert telemetry.report()["events"] == {}
