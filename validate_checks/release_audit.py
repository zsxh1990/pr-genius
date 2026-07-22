"""Check 8: release audit — version alignment across metadata files.

When shipping a release, the version string must agree in:
  - prgenius/pyproject.toml       [project].version
  - prgenius/src/prgenius/__init__.py   __version__
  - glama.json                    top-level "version"
  - Dockerfile                    LABEL version="..."
  - CHANGELOG.md                  most-recent non-Unreleased [x.y.z] heading

Drift between these (e.g. pyproject says 1.2.0 but Dockerfile says 1.3.0) has
historically caused Glama deploys to ship the wrong image tag and README to
advertise an unreleased version. This check makes that drift a CI-visible error.

If CHANGELOG has only [Unreleased] and no [x.y.z] headings, that's a warning
rather than an error (early in a release cycle). If all four metadata files
agree, pass silently.
"""
from __future__ import annotations

import re
from pathlib import Path


def _read_version_pyproject(text: str) -> str | None:
    m = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    return m.group(1) if m else None


def _read_version_init(text: str) -> str | None:
    m = re.search(r'^__version__\s*=\s*"([^"]+)"', text, re.MULTILINE)
    return m.group(1) if m else None


def _read_version_glama(text: str) -> str | None:
    m = re.search(r'^\s*"version"\s*:\s*"([^"]+)"', text, re.MULTILINE)
    return m.group(1) if m else None


def _read_version_dockerfile(text: str) -> str | None:
    m = re.search(r'^LABEL\s+version\s*=\s*"([^"]+)"', text, re.MULTILINE | re.IGNORECASE)
    return m.group(1) if m else None


def _read_changelog_latest(text: str) -> str | None:
    """Return the most recent [x.y.z] heading, skipping [Unreleased]."""
    for m in re.finditer(r'^##\s*\[([^\]]+)\]', text, re.MULTILINE):
        v = m.group(1).strip()
        if v.lower() == "unreleased":
            continue
        return v
    return None


def check_release_audit(
    files: list[Path],  # unused, we look at fixed paths
    parse_frontmatter,
    warnings: list[str],
    errors: list[str],
    ROOT: Path,
) -> None:
    print(f"[Check 8] Release audit (version alignment across pyproject/init/glama/Dockerfile/changelog)")
    sources = {
        "pyproject.toml": (ROOT / "prgenius" / "pyproject.toml", _read_version_pyproject),
        "__init__.py":   (ROOT / "prgenius" / "src" / "prgenius" / "__init__.py", _read_version_init),
        "glama.json":    (ROOT / "glama.json", _read_version_glama),
        "Dockerfile":    (ROOT / "Dockerfile", _read_version_dockerfile),
    }
    versions: dict[str, str] = {}
    missing = []
    for label, (path, reader) in sources.items():
        if not path.exists():
            missing.append(f"{label} missing ({path.relative_to(ROOT)})")
            continue
        v = reader(path.read_text(encoding="utf-8"))
        if v is None:
            missing.append(f"{label}: cannot parse version")
        else:
            versions[label] = v
    for m in missing:
        errors.append(f"release audit: {m}")

    changelog_path = ROOT / "CHANGELOG.md"
    changelog_latest = None
    if not changelog_path.exists():
        warnings.append("release audit: CHANGELOG.md not found")
    else:
        changelog_latest = _read_changelog_latest(changelog_path.read_text(encoding="utf-8"))
        if changelog_latest is None:
            warnings.append("release audit: CHANGELOG.md has no released [x.y.z] heading (only [Unreleased])")

    if not versions:
        return

    unique = set(versions.values())
    if len(unique) > 1:
        drift = ", ".join(f"{k}={v}" for k, v in sorted(versions.items()))
        errors.append(f"release audit: version drift across metadata files: {drift}")

    # Changelog should match the metadata version (if changelog has a release)
    if changelog_latest and versions:
        meta_v = next(iter(versions.values()))
        if changelog_latest != meta_v:
            warnings.append(
                f"release audit: CHANGELOG latest [{changelog_latest}] != metadata version {meta_v}"
            )

    if len(unique) <= 1 and not missing:
        v = next(iter(versions.values()))
        print(f"   aligned on {v}" + (f", CHANGELOG [{changelog_latest}]" if changelog_latest else ""))
