#!/usr/bin/env python3
"""Structural conformance check for the DSH plugin — the part we can verify
without a DeepSeek Harness runtime.

This machine has no ``DEEPSEEK_API_KEY``, so nothing here has been exercised
inside DSH. What *can* be checked without a runtime is whether the package is
shaped the way the platform contract and the benchmark plugin (dsh-context)
require:

  1. the Cordis entry exports ``name`` / ``inject`` / ``apply`` and a
     same-named ``Config`` that is a Schemastery schema, not a plain object;
  2. no hard-coded tunable parameter — every tunable lives in the Config
     schema, which is the only place ``cordis.yml`` can reach;
  3. config errors are loud — the schema declares a default for each field and
     rejects bad values at load;
  4. the assembly file is real (not a three-line stub) and matches the
     package's ``dsh.bundle`` pointer;
  5. the engineering toolchain is present at the benchmark's level
     (strict tsconfig, a test runner, a bundler, a linter, i18n in its own
     directory).

Exit 0 when every blocking check passes. Exit 1 otherwise, listing what is
missing. Warnings do not fail the run.

Usage:  python3 scripts/check_dsh_plugin_contract.py [--json]
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BLOCKING: list[tuple[bool, str]] = []
WARNINGS: list[str] = []


def ok(cond: bool, msg: str) -> None:
    BLOCKING.append((bool(cond), msg))


def warn(msg: str) -> None:
    WARNINGS.append(msg)


# ── 1. Cordis entry point ────────────────────────────────────────────────

ENTRY_CANDIDATES = ["src/index.ts", "src/index.tsx", "src/index.js", "index.ts"]


def read_entry() -> tuple[Path | None, str]:
    for rel in ENTRY_CANDIDATES:
        p = ROOT / rel
        if p.is_file():
            return p, p.read_text(encoding="utf-8", errors="replace")
    return None, ""


entry_path, entry = read_entry()
ok(entry_path is not None, f"Cordis entry exists ({' / '.join(ENTRY_CANDIDATES)})")
if entry_path is None:
    entry = ""

if entry:
    ok(
        re.search(r"export\s+(?:const|let|var)\s+name\s*=", entry) is not None,
        "entry exports `name`",
    )
    ok(
        re.search(r"export\s+(?:async\s+)?function\s+apply\s*\(", entry) is not None,
        "entry exports `apply(ctx, config)`",
    )
    ok(
        re.search(r"export\s+(?:const|let|var)\s+inject\b", entry) is not None,
        "entry exports `inject` (what it needs)",
    )

    # Config must be BOTH a TS interface and a same-named Schemastery schema.
    has_iface = re.search(r"export\s+interface\s+Config\b", entry) is not None
    has_schema = re.search(r"export\s+const\s+Config\s*[:=]", entry) is not None
    ok(has_iface, "entry declares `export interface Config`")
    ok(has_schema, "entry declares same-named `Config` schema (Cordis convention)")
    if has_schema:
        uses_schema = re.search(r"Schema\.(object|string|number|boolean|array)", entry) is not None
        ok(uses_schema, "Config is built from Schemastery, not a plain object")
        warns = "export const Config: Schema" in entry or "Schema<Config>" in entry
        ok(warns, "Config schema is typed as Schema<Config>")

# ── 2 & 3. Config discipline ────────────────────────────────────────────

if entry:
    # Every declared config field should carry a default.
    fields = re.findall(
        r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*Schema\.[a-zA-Z]+\(\)", entry, re.M
    )
    defaulted = re.findall(r"\.default\(", entry)
    if fields:
        ratio = len(defaulted) / max(len(fields), 1)
        ok(ratio >= 0.9, f"config fields carry .default() ({len(defaulted)}/{len(fields)})")
        if ratio < 1.0:
            warn(f"{len(fields) - len(defaulted)} config field(s) lack an explicit default")

    # Heuristic: a tunable that is NOT in Config is a hard-coded parameter.
    suspicious = []
    for m in re.finditer(
        r"(?:timeout|threshold|limit|retries|max[A-Z]\w*|interval|window)\s*[:=]\s*(\d+)", entry
    ):
        # ignore obvious non-tunables
        line = entry[entry.rfind("\n", 0, m.start()) + 1 : entry.find("\n", m.end())]
        if ".default(" in line or "Schema." in line or line.strip().startswith(("//", "*")):
            continue
        suspicious.append(line.strip()[:100])
    if suspicious:
        warn(
            "possible hard-coded tunable(s) outside Config — each must pass the "
            f"'can it change in cordis.yml without touching code?' test: {suspicious[:5]}"
        )

# ── 4. Assembly + packaging ─────────────────────────────────────────────

patch = ROOT / "cordis.patch.yml"
ok(patch.is_file(), "cordis.patch.yml exists")
if patch.is_file():
    txt = patch.read_text(encoding="utf-8", errors="replace")
    ok("insert" in txt, "cordis.patch.yml has an insert directive")
    ok(
        len([l for l in txt.splitlines() if l.strip() and not l.strip().startswith("#")]) >= 4,
        "cordis.patch.yml is a real assembly, not a stub",
    )
    ok("config" in txt, "cordis.patch.yml demonstrates a config block")

pkg_path = ROOT / "package.json"
ok(pkg_path.is_file(), "package.json exists")
if pkg_path.is_file():
    try:
        pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        ok(False, f"package.json parses: {exc}")
        pkg = {}
    dsh = (pkg.get("dsh") or {})
    ok(bool(dsh), "package.json declares a `dsh` block")
    if dsh:
        bundle = dsh.get("bundle") or {}
        ok("patch" in bundle or "plugins" in bundle, "dsh.bundle points at the assembly")
    kws = pkg.get("keywords") or []
    ok("dsh-plugin" in kws, "keywords include `dsh-plugin`")
    lic = (pkg.get("license") or "").upper()
    ok(bool(lic), f"license declared ({lic or 'none'})")
    eng = (pkg.get("engines") or {}).get("node")
    ok(bool(eng), f"engines.node declared ({eng or 'none'}) — DSH wants ^22.19 || >=24")

# ── 4b. Publishability ──────────────────────────────────────────────────

# A package nobody can install without cloning is not converged. dshfind
# currently ships pr-genius from git source for exactly this reason.
manifests = [n for n in ("pyproject.toml", "setup.py", "setup.cfg") if (ROOT / n).is_file()]
ok(bool(manifests), f"a Python packaging manifest exists ({', '.join(manifests) or 'none found'})")
if not manifests:
    warn(
        "no pyproject.toml / setup.py / setup.cfg — the Python half cannot be "
        "published to PyPI, which is why dshfind installs from git source"
    )

# ── 5. Engineering convergence toolchain ────────────────────────────────

tsconfig = ROOT / "tsconfig.json"
ok(tsconfig.is_file(), "tsconfig.json exists")
if tsconfig.is_file():
    t = tsconfig.read_text(encoding="utf-8", errors="replace")
    ok(
        re.search(r'"strict"\s*:\s*true', t) is not None,
        "tsconfig enables strict",
    )

ok(
    any((ROOT / d).is_dir() for d in ("tests", "src/tests")),
    "TypeScript tests directory exists",
)
ok(
    any((ROOT / n).is_file() for n in ("vitest.config.ts", "vitest.config.mts", "jest.config.js", "jest.config.ts")),
    "TypeScript test runner configured (vitest/jest — the plugin is TS)",
)
ok(
    any((ROOT / n).is_file() for n in ("tsdown.config.ts", "tsup.config.ts", "rollup.config.js", "vite.config.ts", "esbuild.config.js")),
    "a bundler/build step is configured",
)
ok(
    any((ROOT / n).is_file() for n in (".oxlintrc.json", ".eslintrc.json", ".eslintrc.js", "eslint.config.js", ".oxlintrc.jsonc")),
    "a linter is configured",
)
ok((ROOT / "locale").is_dir() or (ROOT / "src/locale").is_dir(), "i18n lives in its own directory")
ok((ROOT / "README.md").is_file(), "README.md exists")

# i18n strings must not be hard-coded in components (soft signal).
if entry:
    cjk = re.findall(r"[一-鿿]{2,}", entry)
    if cjk:
        warn(
            f"{len(cjk)} CJK literal(s) inline in the entry — move them to locale/ so "
            "the EN/zh surface stays one source"
        )

# ── report ──────────────────────────────────────────────────────────────

passed = [m for c, m in BLOCKING if c]
failed = [m for m, c in [(m, c) for c, m in BLOCKING] if not c]

payload = {
    "passed": passed,
    "failed": failed,
    "warnings": WARNINGS,
    "score": f"{len(passed)}/{len(BLOCKING)}",
}

if "--json" in sys.argv:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
else:
    print("DSH plugin structural conformance")
    print("=" * 60)
    for m in passed:
        print(f"  PASS  {m}")
    for m in failed:
        print(f"  FAIL  {m}")
    for w in WARNINGS:
        print(f"  warn  {w}")
    print("-" * 60)
    print(f"  {len(passed)}/{len(BLOCKING)} blocking checks passed")
    print()
    print("NOTE: this validates structure only. Nothing here has been run inside")
    print("      a DeepSeek Harness runtime — no DEEPSEEK_API_KEY on this machine.")

sys.exit(1 if failed else 0)
