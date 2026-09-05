"""Tests for validate.py OKF validator integration.

Uses subprocess to run validate.py as a script.
Tests each mode (normal, strict, enforce-evidence) and exit codes.

Note: validate.py sets ROOT = Path(__file__).parent.resolve() at module level,
so subprocess tests copy validate.py into tmp_path and run from there.
Direct function tests monkeypatch the module's ROOT to point at tmp_path.
"""

import importlib.util
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

VALIDATE_SCRIPT = Path(__file__).resolve().parents[2] / "validate.py"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def write_md(directory: Path, name: str, content: str) -> Path:
    """Write a markdown file with optional frontmatter."""
    p = directory / name
    p.write_text(textwrap.dedent(content), encoding="utf-8")
    return p


def setup_isolated_validate(tmp_path: Path) -> Path:
    """Copy validate.py into tmp_path so ROOT resolves to tmp_path."""
    dest = tmp_path / "validate.py"
    shutil.copy2(VALIDATE_SCRIPT, dest)
    return dest


def run_validate(tmp_path: Path, *args: str) -> subprocess.CompletedProcess:
    """Copy validate.py into tmp_path and run it as its working directory."""
    setup_isolated_validate(tmp_path)
    script = tmp_path / "validate.py"
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )


def load_validate_module(tmp_path: Path):
    """Load validate.py as a module, with ROOT patched to tmp_path."""
    spec = importlib.util.spec_from_file_location(
        "validate", str(tmp_path / "validate.py")
    )
    mod = importlib.util.module_from_spec(spec)
    mod.__name__ = "validate"
    spec.loader.exec_module(mod)
    # Patch ROOT so relative_to() calls work with tmp_path files
    mod.ROOT = tmp_path
    return mod


@pytest.fixture()
def isolated_validate(tmp_path: Path):
    """Copy validate.py + load it as a module with ROOT patched."""
    setup_isolated_validate(tmp_path)
    return load_validate_module(tmp_path)


# ---------------------------------------------------------------------------
# 1. Normal mode -- runs without error
# ---------------------------------------------------------------------------

class TestNormalMode:
    """Tests for validate.py running in normal (default) mode."""

    def test_runs_without_crash(self, tmp_path: Path):
        """Normal mode should not crash (exit code 0 or 1, no exception)."""
        write_md(
            tmp_path,
            "lesson-01-example.md",
            "---\ntype: Lesson\ntitle: Test\n---\n# Example\n",
        )
        result = run_validate(tmp_path)
        assert result.returncode in (0, 1)
        assert "Traceback" not in result.stderr

    def test_stdout_has_header(self, tmp_path: Path):
        """Should print the OKF validator header."""
        write_md(
            tmp_path,
            "lesson-01-example.md",
            "---\ntype: Lesson\ntitle: Test\n---\n# Example\n",
        )
        result = run_validate(tmp_path)
        assert "OKF" in result.stdout or "validator" in result.stdout


# ---------------------------------------------------------------------------
# 2. Strict mode -- runs without error
# ---------------------------------------------------------------------------

class TestStrictMode:
    """Tests for validate.py --strict."""

    def test_strict_runs(self, tmp_path: Path):
        """--strict mode should not crash."""
        write_md(
            tmp_path,
            "lesson-01.md",
            "---\ntype: Lesson\ntitle: Test\n---\nok\n",
        )
        result = run_validate(tmp_path, "--strict")
        assert result.returncode in (0, 1)
        assert "Traceback" not in result.stderr


# ---------------------------------------------------------------------------
# 3. Enforce-evidence mode -- runs without error
# ---------------------------------------------------------------------------

class TestEnforceEvidenceMode:
    """Tests for validate.py --enforce-evidence."""

    def test_enforce_evidence_runs(self, tmp_path: Path):
        """--enforce-evidence mode should not crash."""
        write_md(
            tmp_path,
            "pr-001-fix.md",
            """\
            ---
            type: PR Case Study
            schema_version: rounds-v0.5.0
            title: Fix something
            close_decision:
              status: merged
            evidence_urls:
              - https://example.com/evidence
            rounds:
              - round: 1
                action: open
                delta:
                  kind: code_change
                  value: "+10 -2"
            ---
            # PR #1 Fix
            """,
        )
        result = run_validate(tmp_path, "--enforce-evidence")
        assert result.returncode in (0, 1)
        assert "Traceback" not in result.stderr


# ---------------------------------------------------------------------------
# 4. Exit codes
# ---------------------------------------------------------------------------

class TestExitCodes:
    """Test that exit codes are correct for different scenarios."""

    def test_validate_runs_without_crash(self):
        """validate.py should run to completion without crashing."""
        result = subprocess.run(
            [sys.executable, str(VALIDATE_SCRIPT)],
            capture_output=True,
            text=True,
            cwd=VALIDATE_SCRIPT.parent,
        )
        # It may exit 0 or 1 depending on repo state, but must not crash
        assert result.returncode in (0, 1)
        assert "❌" in result.stdout or "✅" in result.stdout or "OK" in result.stdout

    def test_missing_frontmatter_exits_nonzero(self, tmp_path: Path):
        """A file missing frontmatter should produce an error (exit 1)."""
        write_md(tmp_path, "bare.md", "# No frontmatter here\n")
        result = run_validate(tmp_path)
        assert result.returncode == 1
        assert "missing frontmatter" in result.stdout

    def test_missing_type_field_exits_nonzero(self, tmp_path: Path):
        """Frontmatter without `type` field should produce an error."""
        write_md(
            tmp_path,
            "no-type.md",
            "---\ntitle: No type\n---\nContent.\n",
        )
        result = run_validate(tmp_path)
        assert result.returncode == 1
        assert "missing `type` field" in result.stdout


# ---------------------------------------------------------------------------
# 5. Importable functions -- direct unit tests
# ---------------------------------------------------------------------------

class TestParseFrontmatter:
    """Test parse_frontmatter function directly."""

    def test_valid_frontmatter(self, isolated_validate):
        """Should parse valid YAML frontmatter."""
        text = "---\ntype: Lesson\ntitle: Test\n---\nBody text."
        fm, body = isolated_validate.parse_frontmatter(text)
        assert fm is not None
        assert fm["type"] == "Lesson"
        assert fm["title"] == "Test"
        assert "Body text." in body

    def test_missing_frontmatter(self, isolated_validate):
        """Should return None for text without frontmatter."""
        fm, body = isolated_validate.parse_frontmatter("# Just a heading\n")
        assert fm is None

    def test_unclosed_frontmatter(self, isolated_validate):
        """Should return None when frontmatter is not closed."""
        fm, body = isolated_validate.parse_frontmatter("---\ntype: Lesson\n")
        assert fm is None

    def test_invalid_yaml(self, isolated_validate):
        """Should return dict with _error for invalid YAML."""
        fm, body = isolated_validate.parse_frontmatter(
            "---\ntype: [unclosed\n---\nBody"
        )
        assert fm is not None
        assert "_error" in fm


class TestFindMdFiles:
    """Test find_md_files function directly."""

    def test_skips_hidden_dirs(self, isolated_validate, tmp_path: Path):
        """Should skip .git, .venv, __pycache__ etc."""
        write_md(tmp_path, "valid.md", "---\ntype: Lesson\n---\nok")
        (tmp_path / ".git").mkdir()
        write_md(tmp_path / ".git", "hidden.md", "should be skipped")
        (tmp_path / "__pycache__").mkdir(exist_ok=True)
        write_md(tmp_path / "__pycache__", "cached.md", "should be skipped")
        (tmp_path / ".venv").mkdir()
        write_md(tmp_path / ".venv", "venv.md", "should be skipped")

        files = isolated_validate.find_md_files(tmp_path)
        names = [f.name for f in files]
        assert "valid.md" in names
        assert "hidden.md" not in names
        assert "cached.md" not in names
        assert "venv.md" not in names

    def test_returns_sorted(self, isolated_validate, tmp_path: Path):
        """Should return files in sorted order."""
        write_md(tmp_path, "z-last.md", "---\ntype: Lesson\n---\nok")
        write_md(tmp_path, "a-first.md", "---\ntype: Lesson\n---\nok")
        write_md(tmp_path, "m-middle.md", "---\ntype: Lesson\n---\nok")

        files = isolated_validate.find_md_files(tmp_path)
        names = [f.name for f in files]
        assert names == sorted(names)


class TestCheckFrontmatter:
    """Test check_frontmatter function directly."""

    def test_catches_missing_frontmatter(self, isolated_validate, tmp_path: Path):
        """Should append errors for missing frontmatter."""
        isolated_validate.errors.clear()
        isolated_validate.warnings.clear()
        bare = write_md(tmp_path, "bare.md", "# No frontmatter\n")
        isolated_validate.check_frontmatter([bare])
        assert any("missing frontmatter" in e for e in isolated_validate.errors)

    def test_catches_missing_type(self, isolated_validate, tmp_path: Path):
        """Should catch frontmatter without type."""
        isolated_validate.errors.clear()
        isolated_validate.warnings.clear()
        f = write_md(tmp_path, "no-type.md", "---\ntitle: No type\n---\nContent\n")
        isolated_validate.check_frontmatter([f])
        assert any("missing `type` field" in e for e in isolated_validate.errors)

    def test_warns_unknown_type(self, isolated_validate, tmp_path: Path):
        """Unknown type should produce a warning, not an error."""
        isolated_validate.errors.clear()
        isolated_validate.warnings.clear()
        f = write_md(tmp_path, "weird.md", "---\ntype: WeirdType\n---\nContent\n")
        isolated_validate.check_frontmatter([f])
        assert not any("WeirdType" in e for e in isolated_validate.errors)
        assert any("WeirdType" in w for w in isolated_validate.warnings)

    def test_accepts_valid_type(self, isolated_validate, tmp_path: Path):
        """Valid known type should produce no errors or warnings."""
        isolated_validate.errors.clear()
        isolated_validate.warnings.clear()
        f = write_md(tmp_path, "lesson.md", "---\ntype: Lesson\n---\nContent\n")
        isolated_validate.check_frontmatter([f])
        assert not any("Lesson" in e for e in isolated_validate.errors)
        assert not any("Lesson" in w for w in isolated_validate.warnings)


class TestCheckInternalLinks:
    """Test check_internal_links function directly."""

    def test_catches_dead_link(self, isolated_validate, tmp_path: Path):
        """Should detect dead internal links."""
        isolated_validate.errors.clear()
        isolated_validate.warnings.clear()
        f = write_md(
            tmp_path,
            "index.md",
            "---\ntype: Index\n---\n[click me](./nonexistent.md)\n",
        )
        isolated_validate.check_internal_links([f])
        assert any("dead link" in e for e in isolated_validate.errors)

    def test_passes_on_existing_link(self, isolated_validate, tmp_path: Path):
        """Should pass when linked files exist."""
        isolated_validate.errors.clear()
        isolated_validate.warnings.clear()
        target = write_md(tmp_path, "target.md", "---\ntype: Lesson\n---\nok")
        source = write_md(
            tmp_path,
            "source.md",
            "---\ntype: Index\n---\n[see target](./target.md)\n",
        )
        isolated_validate.check_internal_links([source, target])
        assert not any("dead link" in e for e in isolated_validate.errors)


class TestCheckRoundsSchema:
    """Test check_rounds_schema function directly."""

    def test_valid_case_study(self, isolated_validate, tmp_path: Path):
        """Valid PR Case Study should produce no errors."""
        isolated_validate.errors.clear()
        isolated_validate.warnings.clear()
        f = write_md(
            tmp_path,
            "pr-001.md",
            """\
            ---
            type: PR Case Study
            rounds:
              - round: 1
                action: open
                delta:
                  kind: code_change
                  value: "+10"
            ---
            Content.
            """,
        )
        isolated_validate.check_rounds_schema([f])
        assert not any("round" in e.lower() for e in isolated_validate.errors)

    def test_bad_action_strict(self, isolated_validate, tmp_path: Path):
        """Invalid action in rounds should produce error in strict mode."""
        isolated_validate.errors.clear()
        isolated_validate.warnings.clear()
        f = write_md(
            tmp_path,
            "pr-002.md",
            """\
            ---
            type: PR Case Study
            rounds:
              - round: 1
                action: invalid_action
            ---
            Content.
            """,
        )
        isolated_validate.check_rounds_schema([f], strict=True)
        assert any("action" in e for e in isolated_validate.errors)

    def test_bad_action_warns_nonstrict(self, isolated_validate, tmp_path: Path):
        """Invalid action in non-strict should produce warning not error."""
        isolated_validate.errors.clear()
        isolated_validate.warnings.clear()
        f = write_md(
            tmp_path,
            "pr-003.md",
            """\
            ---
            type: PR Case Study
            rounds:
              - round: 1
                action: bogus_action
            ---
            Content.
            """,
        )
        isolated_validate.check_rounds_schema([f], strict=False)
        assert not any("action" in e for e in isolated_validate.errors)
        assert any("action" in w for w in isolated_validate.warnings)

    def test_enforce_evidence_flags_missing(self, isolated_validate, tmp_path: Path):
        """--enforce-evidence should flag missing case-level evidence."""
        isolated_validate.errors.clear()
        isolated_validate.warnings.clear()
        f = write_md(
            tmp_path,
            "pr-004.md",
            """\
            ---
            type: PR Case Study
            rounds:
              - round: 1
                action: open
                delta:
                  kind: code_change
                  value: "+5"
            ---
            Content.
            """,
        )
        isolated_validate.check_rounds_schema([f], enforce_evidence=True)
        flagged = isolated_validate.errors + isolated_validate.warnings
        assert any("enforce-evidence" in m for m in flagged)
