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
     directory);
  6. the published bundle is self-sufficient: every bare specifier the built
     ``dist/*.mjs`` actually imports must be a node builtin, an
     ``@deepseek-ai/*`` host package (DSH's runtime resolution supplies those),
     or a package declared in ``dependencies`` (issue #117 — ``react`` was
     peer-only, DSH never supplies it, so ``import("pr-genius")`` died with
     ERR_MODULE_NOT_FOUND before ``apply()``). Plus the DSH peer-dev pairing:
     every ``peerDependencies`` name also appears in ``devDependencies``.

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


def uses_node_test() -> bool:
    """node:test counts: it is the zero-dependency runner and this repo uses it."""
    for q in (ROOT / "test").glob("*.ts") if (ROOT / "test").is_dir() else []:
        if "node:test" in q.read_text(encoding="utf-8", errors="replace"):
            return True
    return False


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
    # 声明式（`export const name = …`）与再导出式（`export { name }` /
    # `export { name } from '…'`）都算 —— 契约要的是「入口导出 name」，
    # 运行时两者形状相同（`dist/index.mjs` 的 `export { … name … }`）。
    # 但只认这两种，不认 `export default` / 动态拼出来的名字。
    ok(
        re.search(r"export\s+(?:const|let|var)\s+name\s*=", entry) is not None
        or re.search(r"export\s*\{[^}]*\bname\b[^}]*\}", entry) is not None,
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
    # Config 可以住在 entry，也可以住在被 entry 再导出的模块里（我们放 src/config.ts）。
    # 扫整个 src/ 而不是只看 entry，否则会把「拆了文件」误判成「没声明」。
    src_files = [q for q in (ROOT / "src").rglob("*.ts")]
    src_text = "\n".join(q.read_text(encoding="utf-8", errors="replace") for q in src_files)
    has_iface = re.search(r"export\s+interface\s+Config\b", src_text) is not None
    has_schema = re.search(r"export\s+const\s+Config\s*[:=]", src_text) is not None
    ok(has_iface, "entry declares `export interface Config`")
    ok(has_schema, "entry declares same-named `Config` schema (Cordis convention)")
    if has_schema:
        uses_schema = re.search(r"Schema\.(object|string|number|boolean|array|union)", src_text) is not None
        ok(uses_schema, "Config is built from Schemastery, not a plain object")
        warns = "export const Config: Schema" in src_text or "Schema<Config>" in src_text
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
# 清单在子包里（prgenius/pyproject.toml，包名 prgenius-core），不在仓根 —— 只看根目录
# 会把「有清单」误判成「没清单」。
manifests = [n for n in ("prgenius/pyproject.toml", "pyproject.toml", "setup.py", "setup.cfg") if (ROOT / n).is_file()]
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
    any((ROOT / d).is_dir() for d in ("tests", "test", "src/tests")),
    "TypeScript tests directory exists",
)
ok(
    any((ROOT / n).is_file() for n in ("vitest.config.ts", "vitest.config.mts", "jest.config.js", "jest.config.ts"))
    or uses_node_test(),
    "TypeScript test runner configured (vitest/jest/node:test)",
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

# ── 4c. Runtime import surface (issue #117) ─────────────────────────────

# 判据来自真机探针，不是猜的：DSH 的 runtime resolution（dsh-app-boot 的
# collectInstallationScopePackages）在 npm 与 pnpm 两种安装布局下都只供
# @deepseek-ai/*，**从不提供 react**；dsh plugin add 走 pnpm，也不会把
# peerDependencies 装进 profile。所以产物运行时 import 的裸包名必须能在
# 插件自己的安装树里解析 —— 即写进 dependencies —— 或者是宿主保供的
# @deepseek-ai/*。缺一个就是 #117：import 阶段 ERR_MODULE_NOT_FOUND，
# loader 只报一句 "failed to import"，apply() 根本跑不到。
IMPORT_RE = re.compile(
    r"""(?:from|import|require)\s*\(?\s*["']([^"']+)["']"""
)
BARE_PACKAGE_RE = re.compile(r"^(@[^/]+/[^/]+|[^/@][^/]*)")


def iter_import_specs(text: str) -> set[str]:
    """Bare/relative module specifiers in ESM/CJS import positions.

    Excludes method calls like ``Array.from("…")`` / ``m.require("…")`` by
    rejecting a ``.`` (or word char) immediately before the keyword.
    """
    specs: set[str] = set()
    for m in IMPORT_RE.finditer(text):
        prev = text[m.start() - 1] if m.start() else ""
        if prev in (".", "$", "_") or prev.isalnum():
            continue
        specs.add(m.group(1))
    return specs


def bare_package(spec: str) -> str | None:
    """Package name of a bare specifier; None for relative/absolute/node: paths."""
    if spec.startswith((".", "/", "node:", "data:", "file:")):
        return None
    m = BARE_PACKAGE_RE.match(spec)
    return m.group(1) if m else None


if pkg_path.is_file():
    deps = set((pkg.get("dependencies") or {}).keys())
    peers = pkg.get("peerDependencies") or {}
    peer_names = set(peers.keys())
    dev_names = set((pkg.get("devDependencies") or {}).keys())

    # (a) DSH peer-dev rule: shared-instance peers also carry a devDependency
    #     copy for typecheck/tests (the pairing dsh-context and the harness
    #     packages use).
    unpaired = sorted(peer_names - dev_names)
    ok(not unpaired, f"every peerDependency also has a devDependency ({', '.join(sorted(peer_names)) or 'none'})")
    if unpaired:
        warn(f"peerDependencies without a devDependency twin: {unpaired}")

    # (b) built dist must only import what a consumer install + DSH host provide.
    dist_mjs = sorted((ROOT / "dist").rglob("*.mjs")) if (ROOT / "dist").is_dir() else []
    # 这一项是**条件性**的（要先 npm run build）。把它整条不计入 BLOCKING 会让分母
    # 随「跑没跑构建」在 28/29 之间浮动 —— 两台机器测同一个 commit 会数出不同的
    # 「总检查数」，于是文档里那个数字没有稳定值可写（实测：dist 在 → 29/29，
    # dist 无 → 28/28，都自称全绿）。修法：**分母固定、跳过显式** ——
    # 检查始终计入 BLOCKING，跑不了就记 skipped，绝不悄悄缩小分母。
    SKIPPED: list[str] = []
    if not dist_mjs:
        SKIPPED.append("runtime import surface (dist/ not built — run `npm run build`)")
        ok(False, "every dist/*.mjs bare import is a builtin, @deepseek-ai/* host package, or a dependency")
    else:
        specs: set[str] = set()
        for f in dist_mjs:
            specs.update(iter_import_specs(f.read_text(encoding="utf-8", errors="replace")))
        unresolvable = sorted(
            {
                s
                for s in map(bare_package, specs)
                if s is not None and s not in deps and not s.startswith("@deepseek-ai/")
            }
        )
        ok(
            not unresolvable,
            "every dist/*.mjs bare import is a builtin, @deepseek-ai/* host package, "
            f"or a dependency ({len([s for s in map(bare_package, specs) if s])} specs checked)",
        )
        if unresolvable:
            warn(
                "imported by dist but not in dependencies (peer-only is not enough: DSH "
                f"never installs or supplies these) → {unresolvable}"
            )

    # (c) client half: every `require("X")` the browser bundle issues must be a
    #     module the DSH web host actually provides. This is the check that
    #     would have caught the shape of bug in #163 before anyone opened a real
    #     browser: `exports["./client"]` can exist, the bundle can be well
    #     formed, and it can still die at `require()` time in the factory.
    #
    #     The authority is **not** a list we wrote. `docs/data/dsh-web-seed-table.json`
    #     is generated from npm packages we do not own — the `require()` surface of
    #     `@deepseek-ai/*/lib/client.js`, plus the `@deepseek-ai/*` module names in
    #     `@deepseek-ai/dsh-web-frontend`'s bundle. Provenance is recorded in the
    #     file. Using our own table would be the circular validation
    #     `docs/maturity-self-assessment.md` warns about.
    SEED_PATH = ROOT / "docs" / "data" / "dsh-web-seed-table.json"
    CLIENT_CJS = sorted((ROOT / "dist").rglob("client*.cjs")) if (ROOT / "dist").is_dir() else []
    if not CLIENT_CJS:
        SKIPPED.append("client require surface (dist/client*.cjs not built — run `npm run build`)")
        ok(False, "every require() in the browser bundle resolves in the DSH web seed table")
    elif not SEED_PATH.is_file():
        SKIPPED.append("client require surface (docs/data/dsh-web-seed-table.json missing)")
        ok(False, "every require() in the browser bundle resolves in the DSH web seed table")
    else:
        seed = json.loads(SEED_PATH.read_text(encoding="utf-8"))
        provided = set(seed.get("modules") or [])
        # 空表会让这条检查永远通过 —— 那是最坏的假绿，所以先钉住表本身。
        ok(bool(provided), f"the DSH web seed table is non-empty ({len(provided)} modules)")
        if not provided:
            warn(f"{SEED_PATH.relative_to(ROOT)} has no modules — the check cannot fail, which is not the same as passing")

        require_re = re.compile(r'\brequire\(\s*["\']([^"\']+)["\']\s*\)')
        needed: set[str] = set()
        for f in CLIENT_CJS:
            needed.update(require_re.findall(f.read_text(encoding="utf-8", errors="replace")))
        missing = sorted(s for s in needed if s not in provided)
        ok(
            not missing,
            f"every require() in the browser bundle resolves in the DSH web seed table "
            f"({len(needed)} specifiers, {len(provided)} modules available)",
        )
        if missing:
            warn(
                "required by the browser bundle but absent from the DSH web seed table — "
                "the factory will get `undefined` at require() time and fail in the browser "
                f"→ {missing}"
            )

# ── report ──────────────────────────────────────────────────────────────

passed = [m for c, m in BLOCKING if c]
# 跳过的项不是失败：它没跑，不是没通过。从 failed 里减掉，但**留在 BLOCKING 里**，
# 好让分母恒定 —— 这就是「28/28」与「29/29」两个都自称全绿却互相对不上的原因。
_skipped_names = set(SKIPPED)
failed = [m for m, c in [(m, c) for c, m in BLOCKING] if not c and m not in _skipped_names]
skipped = [m for m in _skipped_names]

payload = {
    "passed": passed,
    "failed": failed,
    "warnings": WARNINGS,
    "skipped": skipped,
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
    for m in skipped:
        print(f"  SKIP  {m}")
    print("-" * 60)
    # 分母恒定 = BLOCKING 的总数，不随构建状态变化。文档里写的应该是这个总数。
    print(f"  {len(passed)}/{len(BLOCKING)} blocking checks passed"
          + (f" ({len(skipped)} skipped)" if skipped else ""))
    print()
    print("NOTE: this validates structure only. Nothing here has been run inside")
    print("      a DeepSeek Harness runtime — no DEEPSEEK_API_KEY on this machine.")

sys.exit(1 if failed else 0)
