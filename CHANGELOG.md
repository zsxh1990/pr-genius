---
type: Community Resource
description: Changelog following Keep a Changelog format + GitHub compare links
---

# Changelog


## [Unreleased]

### Changed — this reverses a documented trade

- **Adoption counters ship (#127 risk 5), and the "no telemetry" promise is
  retired.** For as long as this project has existed, `README.md` said *"It will
  not phone home… There is no telemetry"* and
  [`docs/ADOPTION_DATA.md`](docs/ADOPTION_DATA.md) said a usage-ping channel
  would contradict the local-only positioning *"even a hashed and opt-in one"*,
  so the trade was made deliberately: adoption numbers were given up to keep
  "nothing leaves your machine during analysis" intact.

  **That trade is now reversed.** #127 risk 5 reopened it and the maintainer
  chose numbers. This entry exists because a change of mind about a public
  promise should be visible in the changelog and not only in a rewritten
  paragraph.

  What shipped is asymmetric, so only one half can give anything up:

  - **Local counters are on and never transmit.** Per-tool invocation counts and
    per anti-pattern *family* that fired. A file on your machine —
    `prgenius telemetry` reads it, `prgenius telemetry reset` deletes it. No PR
    title, body, repo, author or diff is recorded in any form, hashed or not,
    and there is no install id. `telemetry.record()` accepts no free-form
    payload so that nobody can smuggle one in later.
  - **A network sink exists and is off.** It activates only when
    `PRGENIUS_TELEMETRY_URL` is set, and then posts those counts and nothing
    else. Setting that variable is what gives up the guarantee. The GitHub
    Action never sets it — it runs on third-party repos whose users have not
    consented (#110).

  Conditions this page's predecessor set for such a change, kept: announced
  here, documented in [`SECURITY.md`](SECURITY.md), and **off by default
  everywhere**.

  **What this still cannot do:** measure an adoption rate. That needs per-PR
  correlation, which needs a stable identifier. #110 proposed SHA-1 of the
  input arguments for it; this deliberately does not, because a stable hash of
  someone's PR text is still a fingerprint of their work.

### Fixed

- **The panel's default seat was a key the SDK deleted (#150).**
  `ADVISOR_PANEL_SLOT` was `details`, and `SURFACE_PLAN`'s panel seat declared
  `kind: 'single'` to match. In `@deepseek-ai/dsh-cordis-client-runner@0.2.1-rc.3`
  that key is gone: `CLIENT_SLOT_API` drops `details`, `conversation`,
  `conversation.details.tool` and `settings.plugin.item`, and adds
  `sidebar.right.pane.tab` / `.title` (42 → 103 keys). The default is now the
  keyed seat that 0.2.1 declares, and `details` is kept only as a legacy
  fallback candidate so a host still on the 0.0.1 surface can land on it.

  Probe order flipped to try the live key first (#142): `apply()` breaks on the
  first accepted candidate, so a dead key listed first burns a failed inject on
  every launch and shows up in the release-smoke ledger as
  `C1.slot-key-not-in-catalog` — which is how #145 stayed red while the code was
  correct and only the pinned SDK was stale.

- **README claimed the DSH slot catalog is unobtainable. It is obtainable.**
  The note cited `gh api repos/deepseek-ai/deepseek-harness-sdk` 404 as proof —
  but that is a typo'd repository name. `deepseek-ai/deepseek-harness` is public
  and `…/src/client/slot-catalog.ts` fetches (289,726 bytes at `master`);
  `scripts/release-smoke/slot-catalog.mjs` already used the right name. What is
  actually true is narrower: the *host's installed* SDK version is unknown at
  build time, and that is what the probing defends against. (CI still cannot
  fetch the cross-check source — it passes no `GH_TOKEN`; #149.)

### Changed

- **`@deepseek-ai/*` devDependencies move to `0.2.1-rc.3`.** These are the npm
  `next` dist-tag, not `latest` — for most of the family `latest` is still
  `0.0.1-rc.x`, so this is an opt-in to the prerelease line, not a routine bump.
  `dsh.compatibility.dshReleases`/`dshOperations` record `0.2.1-rc.3` as
  **`unknown`**, not `compatible`: no real DSH web host has been run against it
  (`validate.py` Check 4c says those values must reflect 实测, and this is not
  one). `docs/compatibility.md` is unchanged for the same reason — it has no
  row that is verified.

### Note on counts

Earlier drafts of this change wrote "45 → 106 keys" as measured. Those numbers
did not reproduce: a `key:` regex counts nested `key:` fields and inflates each
version by 3. The bracket-matched `CLIENT_SLOT_API` element count is 42 and 103,
which is also what `npm run smoke:release` reports (`catalog keys=103`) and what
README/CHANGELOG already said for the pinned side. The qualitative claims —
`details` removed, `sidebar.right.pane.tab`/`.title` added, 4 dropped / 65 added
— reproduce either way.


## [2.2.5] - 2026-10-21

> The point of this release is one thing: 2.2.4 shipped before the fix for
> "installs but registers nothing, and says so quietly" landed. If you are
> debugging an empty DSH sidebar on 2.2.4, the error you want is in here.

### Fixed

- **A DSH install that registers no surface now says so out loud (#131).** When
  the host provides `slots` but accepts none of the four UI surfaces, `apply()`
  logs an **error** naming each surface and the candidate slots that were tried,
  instead of a warn per surface. A warn per surface is how "registered
  everything" and "registered nothing" looked almost identical from outside —
  which is how "empty shell install" shipped eight times in five weeks
  (#86, #90, #95, #97, #98, #100, #101, #117).

  The slash command is deliberately **not** counted in that test: it runs on
  `ctx.command`, not a slot, so a working `/prgenius` must not be able to hide
  "all four UI surfaces went missing".

  Registration outcome is now readable without scraping logs: `describe().surfaces`
  reports `expected` / `registered[]` / `failed[]`, with the seat each surface
  landed on and the candidate slots the host refused.

  **2.2.4 does not have this.** The fix (`a2bf946`) landed after the 2.2.4 tag
  was cut, so the published package predates it — the same shape as #129. This
  release is that gap closed. Verified against the published tarball, not against
  a checkout.

- **The issue #68 contract lock is a test again (#125).** PR #124 replaced the
  `def` line of `test_url_string_rate_is_not_treated_as_measured` and left the old
  body behind, so the code sat at the tail of `test_strict_gates_…` where it was
  evaluated and discarded. pytest never runs orphaned statements, so the suite
  stayed green while the regression guard was gone. Restored as its own test.

### Docs

- The README no longer claims the wheel ships no knowledge — `prgenius-core` has
  bundled the decision-relevant corpus since #116. A checkout and
  `PRGENIUS_REPO_ROOT` are overrides, not prerequisites.

## [2.2.4] - 2026-10-20

> Action comments get shorter by default. The detail never left — it moved to
> the run page, which is where the compact comment points.

### Added

- **`comment_format` Action input — `compact` (default) or `verbose`.**
  `compact` posts a short bullet list: risk tier, the finding counts, the
  analyzer's one-line summary, and a link to the action run. `verbose` is the
  previous full table and is unchanged byte for byte (`render_comment` is not
  touched). Any other value falls back to `compact` and emits a `::warning::`
  on the run instead of failing.

- **`docs/ADOPTION_DATA.md`** — states plainly that there is no adoption
  telemetry and why, lists what is measured instead (all of it inside this
  repository, all of it re-runnable), and separates that from what is genuinely
  unknown. Linked from the README's corpus count so the pattern/repo number is
  not mistaken for a usage number. Closes the documentation half of #110.

### Changed

- **Behavior change: comments are now `compact` by default.** Workflows that
  set `comment_mode` but not `comment_format` will post a much shorter comment
  than before. Set `comment_format: verbose` to restore the old output. Long
  analysis stays available on the run page and in `$GITHUB_STEP_SUMMARY`.

  This is the one user-visible default change in this release and it is called
  out here rather than left to be discovered from shorter comments.

- `SECURITY.md` gains a **Privacy** section (what leaves your machine, and the
  fact that nothing does during analysis) and a **Dependency pinning** section
  that documents the `>=2.0,<2.99` tripwire — the `action.yml` comment has
  pointed at this policy since the pin landed, and it did not exist until now.

### Fixed

- **`react` / `react-dom` ship as runtime dependencies (#117, #129).** They were
  declared only as `peerDependencies`, and pnpm does not install peers in a DSH
  profile — so the external `import ... from "react"` at the top of
  `dist/index.mjs` resolved to nothing and every `dsh plugin add pr-genius` died
  at the `import()` step with `ERR_MODULE_NOT_FOUND`, before `apply()` could
  register a single surface. The four surfaces were never "missing"; the module
  never loaded.

  The source fix (`ec1b7da`) landed on `main` on 2026-10-17, thirteen days after
  the `v2.2.3` tag was cut, and **no release carried it** — 2.2.3 on npm is still
  the pre-fix manifest. This is that release. **If you installed 2.2.3, upgrade.**

- **`prgenius-core`'s wheel now ships its memory (issue #116).** The knowledge
  corpus lived only at the repository root, so `pip install prgenius-core`
  produced an amnesiac dashboard: `doctor` resolved `repo_root_source: none`
  and reported 0 anti-patterns, 0 profiles, 0 case studies, 0 policies until
  someone pointed it at a git clone. The build now bundles the
  decision-relevant subset (`anti-patterns/`, `profiles/`, `pr-observations/`,
  `docs/policies/`, `locale/`) as `prgenius/data/`, and root resolution finds
  it as `package-data` — after `PRGENIUS_REPO_ROOT` and a checkout above the
  package, before the npm `node_modules/pr-genius` fallback.

  `success-patterns/` (~2.7 MB) is deliberately still not bundled: it is a
  retrieval/reference corpus the scorer never consults (issue #69), so it
  would triple the wheel without changing a single decision. `doctor` now
  reports `success_patterns_installed: false` and names where to get it
  instead of printing a bare 0.

### Docs

- README documents `comment_format` next to `comment_mode`, including the
  default-change note above.

## [2.2.3] - 2026-10-04

> Harvest was writing "failure" into records of PRs that merged cleanly.

### Fixed

- **`harvest` no longer stamps successful PRs as `pr-failure`.** Both draft
  templates hardcoded the category, so a merged PR with zero maintainer
  feedback came out as a `pr-failure` anti-pattern with
  Lesson/Solution/Verification left for a human to fill in. Four such shells
  had accumulated in `anti-patterns/`; three of them were merged PRs whose own
  record said "已合并 by @维护者" and "Root Cause: 无 maintainer 评论".

  `classify_outcome()` now decides, and a `merged-clean` draft says plainly
  that there is no signal and asks **not** to be filled in — inviting a Lesson
  for a failure that never happened is worse than leaving it blank.

- **One document could contradict itself.** The classifier counted *any* comment
  as feedback while `Root Cause` only quotes OWNER/MEMBER/COLLABORATOR ones, so
  a PR with only a DCO bot comment was labelled "has feedback" and printed
  "无 maintainer 评论". Both now use the same filter.

The three mislabeled records are corrected in place. `test_harvest.py` covers
the classification and asserts the honesty property directly.

698 pytest green (was 689); `validate` ×3 exit 0.


## [2.2.2] - 2026-10-04

> Follow-up to 2.2.1: the crash was gone, the message was still wrong.

### Fixed

- **`doctor` now names the path that is actually wrong.** With
  `--repo-root /tmp/nonexistent`, 2.2.1 printed the "wheel ships code only"
  text and then called that path "where the package is installed" — it is what
  the *user* passed. `repo_root_source` describes the module's auto-resolution
  and has nothing to do with `--repo-root`, so checking it first routed an
  explicitly passed bad path into the auto-detect branch.

  Existence checks now come first, since they describe the root actually in
  use: `does not exist` / `is not a directory` / `anti-patterns/ missing`, and
  only then the wheel-ships-code message — which is accurate when it fires,
  because in that case the path really is the install location.

All four input cases verified. 689 pytest green, `validate --strict` exit 0.


## [2.2.1] - 2026-10-04

> **The #103 fix was committed to `main` after `v2.2.0` was tagged, so 2.2.0
> still shipped the crash.** Caught only by walking the new-user path against
> the *published* wheel — running the same command from the working tree
> printed the fixed behaviour and looked done. That is the third time in this
> series a fix has been "verified" somewhere the user cannot reach.

### Fixed

- **A bad `--repo-root` no longer raises a traceback** (issue #103). `iter_profiles`
  called `root.iterdir()` directly, so `prgenius-core --repo-root /nonexistent doctor`
  ended in `FileNotFoundError` out of the middle of the parser. `parser.py` now
  has `_iter_dir()` which returns an empty list when the directory is missing,
  unreadable, or not a directory; all three traversals go through it. `doctor`
  then distinguishes the three bad-input cases (`does not exist` / `is not a
  directory` / `anti-patterns/ missing`) instead of blaming the markers for all
  of them.

### Process note

Issue #103 was closed on the strength of a `PYTHONPATH=src` run. The wheel was
never checked. "Fixed in commit X" and "fixed in the version you install" are
different claims, and only the second one is what a user experiences — so the
fix is in **2.2.1**, not 2.2.0. Anyone who hit the traceback on 2.2.0 should
upgrade.

## [2.2.0] - 2026-10-04

> Two pieces of convergence work: make the corpus's own rules enforceable, and
> let the `mcp` extra install on either generation of the SDK.

### Added

- **Check 4b — pattern loader visibility.** `load_anti_patterns` reads only
  frontmatter, but nothing checked that the fields it consumes were actually
  written there. Two pattern files carried `trigger_keywords:` *in the body*,
  after the closing `---`, with the placeholder value `no-keywords` — so those
  patterns loaded with zero keywords and could never fire, and no tool said so.
  The check reports three classes: a loader-consumed field sitting in the body,
  a placeholder value (`no-keywords` / `TODO` / `tbd` / …), and a file whose
  `type` is not `Anti-Pattern` while living in `anti-patterns/`.

  Each class was verified by injecting it and watching the counter move, not by
  reading the code and believing it.

- **mcp 2.x support.** The `mcp` extra now installs on `mcp>=1.0,<3.0`.
  Dependabot opened exactly this widening (PR #88) and it broke every install,
  because mcp 2.x renames `FastMCP` to `MCPServer` — the widening was right and
  the migration was missing. `mcp.py` now imports whichever generation is
  installed; the API surface we use (constructor, `@tool(annotations=…)`,
  `run(transport=…)`) is identical across both. `_tool_manager._tools` is still
  a plain dict in 2.x, so `doctor`'s introspection needed no fork.

### Fixed

- **Five pattern files carried the wrong `type`.** `anti-patterns/` holds 56
  files typed `Anti-Pattern`; five said `Lesson` or `Case Study`. The loader
  counts every file in that directory as an anti-pattern and the case studies
  reference these keys as anti-patterns, so the mismatch inflated the coverage
  denominator and made "anti-pattern" mean two things. Normalised.

- **Two pattern files leaked a malformed frontmatter block into the body**,
  including a `---` glued onto the placeholder value. Removed. No keywords were
  invented to replace them — the honest state is "no keyword detector", and
  fabricating values to lift coverage is what the evidence gate forbids
  elsewhere.

### Not fixed (recorded so it is not forgotten)

- `punkpeye-fastmcp-282-too-large` describes a real observed pattern whose
  actual signal is PR **size**. There is no size detector: `structural.py`
  checks content, not diff volume. It remains documentation, not a firing rule.
  `pr_size` is already computed, so a size detector is feasible — it needs a
  threshold someone will defend, which is a separate decision.

### Known limits

- The plugin **has** been run in a live DSH web host — that is how issues #100, #101 and #103 were found. What is unverified is the *current* fixes: 2.1.5 and later have not been re-verified in a host. Issue #102 recruits for that.

## [2.1.8] - 2026-10-04

> Found by actually walking the new-user path against the **published** wheel,
> not the working tree — which is the only way this class of defect shows up.

### Fixed

- **`prgenius-core doctor` no longer invents a repo root.** `_find_repo_root()`
  had a legacy dev-layout step (`here.parents[3]`) that was supposed to be a
  shortcut for `prgenius/src/prgenius/utils.py` → repo root. On a wheel install
  that expression evaluates to the virtualenv's `lib/` directory — a
  plausible-looking path that is not a repo root at all. A user who ran
  `pip install prgenius-core` and then `doctor` was told their knowledge base
  was missing "at /…/lib", which is not actionable and not true.

  The dev-layout step now only applies if that directory actually carries the
  knowledge-bundle markers. When nothing is found, the resolution source is
  reported as `none` and the warning says the real cause and the real fix: the
  `prgenius-core` **wheel ships code only**, the corpus lives in the git repo,
  and you point at it with `--repo-root <clone>` or `PRGENIUS_REPO_ROOT`.

### Changed

- **Quick Start now matches what a new user actually has to do.** It said
  `pip install prgenius-core` and then showed commands that need the corpus.
  It now covers the `[mcp]` extra (without it `doctor` reports the MCP surface
  unusable and `overall: NOT OK`), the clone step, and the `PRGENIUS_REPO_ROOT`
  export, with a note that `overall: NOT OK` after a bare install is the wheel
  containing code only rather than a broken install.

Verified end-to-end against a freshly built wheel in an empty venv:

```
$ pip install "prgenius-core[mcp]"
$ PRGENIUS_REPO_ROOT=<clone> prgenius-core doctor
knowledge:   readable — 251 anti-patterns, 692 success-patterns,
             67 profiles, 53 case studies, 5 policies
mcp:         ✓ 14 tools
overall:     OK
```

Both journeys were re-run against the release: the developer path (install from
PyPI → `doctor` → analyze/coach/triage) and the maintainer path (version-sync
gate → `validate` ×3 → DSH contract 27/27 → tsc → 68 tests → release smoke
gate).

### Known limits

- The plugin **has** been run in a live DSH web host — that is how issues #100, #101 and #103 were found. What is unverified is the *current* fixes: 2.1.5 and later have not been re-verified in a host. Issue #102 recruits for that.

## [2.1.7] - 2026-10-04

> Cut to close two documentation gaps and — more importantly — to be the first
> version published **from CI over npm Trusted Publishing (OIDC)**. Until now
> every npm publish was a manual `npm publish` with a one-time password, which
> is exactly how 2.1.2 through 2.1.5 quietly never reached npm at all.

### Added

- **A CLI reference covering all 20 subcommands** (issue #58). The README's Quick
  Start showed 5 commands; `issue` and `issue-batch` (shipped in v1.6.3) had
  never been mentioned, and 13 others were discoverable only by running
  `--help`. Every row is taken from the real parser, and the two `issue*`
  examples were executed against a live repo before being documented.

- **A "For Contributors" walkthrough for `contributor_view`** (issue #57).
  Previously there was one table row. Now there is the decision the tool answers
  ("should I submit this PR yet, and what is blocking me?"), the five outcomes
  with a next move each, and the four signals that actually move you from
  `FIX_BEFORE_SUBMIT` to `READY_TO_SUBMIT`. Enum values were checked against
  `contributor_view.py` rather than retyped from memory — an earlier draft of
  this section spelled `NEEDS_DISCUSSION` wrong.

### Changed

- **npm publishes via Trusted Publishing (OIDC) instead of a long-lived
  `NPM_TOKEN`.** GitHub mints a short-lived token, the npm CLI exchanges it, and
  nothing secret is stored in the repo. Provenance attestation comes free.
  The job requires `id-token: write`, runs Node 24 and **fails loudly** if the
  npm on PATH is older than 11.5.1 (Node 22 ships npm 10.x) rather than
  silently not publishing.

### Known limits

- The plugin **has** been run in a live DSH web host — that is how issues #100, #101 and #103 were found. What is unverified is the *current* fixes: 2.1.5 and later have not been re-verified in a host. Issue #102 recruits for that.

## [2.1.6] - 2026-10-04

> **Two release-pipeline holes found by asking "did the thing users install
> actually get updated?"** Neither was visible from inside the repo: both only
> showed up by checking the registries and the packed artifact.

### Fixed

- **React is no longer bundled into the plugin (issue #101).** `tsdown.config.ts`
  had no `external` list, so `react` — a `devDependency` — was inlined into
  `dist/index.mjs`. A DSH web host brings its own React, and two copies of React
  break hooks (`useState` et al. read a dispatcher off "the" React instance), so
  3 of the 4 sidebar surfaces threw "Invalid hook call" in any host with its own
  React. `react` / `react-dom` / `react/jsx-runtime` are now external and
  declared as `peerDependencies`; `dist/index.mjs` drops from 109,936 to ~38,900
  bytes and contains zero React internals (`ReactCurrentDispatcher`,
  `react.production*` — grepped, 0 in every chunk).
  Note the one package that must **stay** bundled: `@deepseek-ai/schemastery` is
  the only runtime `@deepseek-ai` import and is only a devDependency, so
  externalizing it (a blanket `/^@deepseek-ai\//` rule) made the unpacked
  artifact die with `Cannot find package`. The rule is now explicit.

- **The release gate now models a host that provides peers.** It unpacks the
  tarball and imports it from a temp dir, which has no `node_modules` — so with
  React externalized it would have failed for the wrong reason. The gate now
  links the host's `node_modules` into the extract dir before importing, which
  is what a real host does. It does not re-bundle React to make the gate pass.

### Changed

- **Added the missing `publish-npm.yml`.** `pr-genius` on npm was still at
  **2.1.1** — 2.1.2, 2.1.3, 2.1.4 and 2.1.5 never got there, because there was
  no npm publish workflow at all (only `publish-pypi` and `publish-ghcr`).
  `dsh plugin add pr-genius` is the DSH install path, so anyone installing the
  plugin was getting the version with invented slot names and null components.
  Publishing is now tag-driven like the PyPI one.

### Known limits

- Same as 2.1.5: the plugin has run in a real DSH host (source of #100/#101/#103), but these fixes have not been re-verified there.
  Issue #102 recruits testers. The React fix is verifiable without a host —
  the bundle no longer contains a second React — but "the surfaces render in a
  host that has its own React" still needs someone with a host.

## [2.1.5] - 2026-10-04

> **Cut to make the DSH web sidebar actually reach a real host — and to stop two
> more "verified locally" claims from shipping.**
>
> Three separate defects sat between `apply()` and a live DSH web host. The first
> is issue #100. The second and third were found by reading the shipped guard and
> then **disproving the mock** rather than trusting it. Every fix below is backed
> by a test that was shown to go red when the fix is reverted (negative test), and
> by `npm run smoke:release` against the packed tarball.

### Fixed

- **The four UI surfaces now reach `ctx.slots` in a real host (issue #100).**
  The registration probe used `Reflect.has(ctx, 'slots')`. On the DSH dynamic
  facade that is a proxy `has` trap answering `declared.has(name)`, and with
  `inject: []` it is **always false — it does not throw**. The `&&` chain
  therefore short-circuited and **no surface ever registered**, behind a
  reassuring warn line. Issue #100's report said the guard throws and proposed
  `inject: ['slots', …]`; both are wrong — the throw only happens on a *direct*
  `ctx.slots` read, and cordis `Plugin.Base.inject` is a hard load gate
  ("it only loads while all are available"), so declaring `slots` would make the
  plugin not load on any non-web host. Probing now goes through
  `ctx.get(name)`, which cordis documents as "without the inject requirement".
  `inject` stays `[]`. See the CORRECTION note under the 2.1.3 entry.

- **`apply()` no longer dies on `ctx.logger` before it can probe anything.**
  `logger` is **not** in the guard's `CTX_VERBS` (checked in the shipped
  `client.js` *and* upstream `deepseek-harness` `guard.ts`, where `logger` is
  mentioned zero times), and `LoggerService` is not in the cordis service store
  (`Context` sets `this.logger = new LoggerService(self)` as a plain property;
  it never calls `provide()`). So `ctx.logger(…)` — the first statement of
  `apply()` — hits `denyRead` and throws, which would have cancelled the
  `ctx.get` fix above entirely. `inject: ['logger']` is *not* an option either:
  `_checkImpl` finds no provider, `_refresh` marks the fiber INACTIVE, and the
  plugin never loads. `apply()` now resolves a logger via `Reflect.has(ctx,
  'logger')` (true on a plain cordis Context, false-and-not-throwing on the
  guard facade) and falls back to a console-backed logger, so missing logging
  can never take the plugin down.

- **`PREFERENCES_SLOT` named the wrong seat.** The constant said
  `sidebar.footer.action`, which is the *dashboard* seat; it is rendered as a
  `data-slot` attribute, so the shipped markup mis-stated where Preferences sits.
  The real seat is `settings.section` (that is what `SURFACE_PLAN` registers).
  Verified against the gate ledger: `settings.section` is accepted.

- **`details` registration sent options the SDK does not accept.** `details` is
  `single` cardinality; the pinned `CLIENT_SLOT_API` declares only `name` for
  that cardinality, but we sent `{ name, id, label }`. The gate reported this as
  `C4.unknown-register-option`. `single` seats now emit `{ name }` only.

### Changed

- **The release smoke gate now mocks the guard instead of bypassing it.**
  Previously the mocked host attached `slots` as a literal property, which made
  `Reflect.has` true and `ctx.slots` readable — exactly the code path the real
  guard denies. The gate has a denyRead-semantics host (direct read throws with
  the guard's own message, `Reflect.has` answers `declared.has`, `ctx.get` is the
  optional lookup) and **does not whitelist `logger`**, matching the real
  `CTX_VERBS`. It captures the plugin's console fallback instead of pretending
  the facade has a logger. Reintroducing `Reflect.has` + direct-read probing, or
  a bare `ctx.logger`, turns the gate red.

- **`scripts/sync_version.py` covers two version sites it was missing.**
  `prgenius/src/prgenius/__init__.py` (`__version__`, the value the wheel and the
  PyPI smoke step print) and the newest release heading in `CHANGELOG.md` were
  not checked, even though `CLAUDE.md`'s release process names the first as a
  file to bump by hand. Drift in either now fails the dry-run that CI already
  runs. The CHANGELOG check is **check-only** under `--apply`: a missing release
  heading means the entry was never written, and inventing one would be a false
  record.

- **`prgenius doctor` stopped understating its own gap by 30×.** It reported
  "6/251 anti-patterns have no trigger_keywords", which reads as "2.4% are
  broken". The real split: 6 of **61** keyword-based patterns are missing
  keywords (those genuinely can never match), and 190 of 251 are imported JSON
  records that are deliberately keyword-free and skipped by the matcher
  (`load_anti_patterns`: "JSON patterns 不提取 keywords — 避免假阳性"). Both
  facts are now stated with their correct denominators, and the JSON set is
  labelled as reference-only by design rather than as a defect.

- `CHANGELOG.md`'s two duplicate `## [Unreleased]` sections in the modern block
  were merged into one (Added → Changed → Fixed → Known limits, content kept).
  The spliced-in pre-2.0 history is now fenced with an explicit marker so its
  stale `## [Unreleased]` cannot be mistaken for current work.

### Known limits

- **The fixes still need re-verification in a live DSH web host.** The plugin itself has run in one — that is how #100/#101/#103 were reported — but this release's changes have not been re-tested there. There is no `DEEPSEEK_API_KEY`
  on this machine. What is proven: `apply()` emits registrations that land on
  SDK-declared seats with non-null components, under both a permissive host and a
  denyRead-semantics host, against the packed tarball. What is not: that anything
  renders. Issue #102 recruits testers with a real DSH host.
- **The two slot catalogs still disagree** (pinned SDK 42 keys vs upstream
  master 92; `details` vs `sidebar.right.pane.tab`). The gate validates against
  the **pinned** one, because that is what a user installs, and reports the drift
  as a warning. Registration probes candidates at runtime and degrades rather
  than guessing.
- `prgenius doctor` still reports `692/692 success-patterns are not consulted by
  the scorer`. That is a declared product decision (issue #69), not a defect.

## [2.1.4] - 2026-10-03

> **Cut for one reason: so the claim "a runtime gate signed off on this" becomes true in CI.**
>
> 2.1.3 carried that line, and it was only half accurate. The gate passed locally
> and in `prepublishOnly`, but the CI leg never ran — `actions/setup-node` with
> `cache: pnpm` was ordered before `pnpm/action-setup`, so it died with
> "Unable to locate executable file: pnpm" before the gate started. That order is
> fixed on `main` (`ac8ab6a`), and this tag is what exercises it.

### Fixed
- `release-smoke.yml` installs pnpm before `setup-node`'s pnpm cache. `setup-node`
  shells out to `pnpm` to resolve the lockfile; when it is not on PATH yet the
  workflow fails at setup and the gate never runs. The gate was never the problem
  — the workflow never reached it.

### No behavioural change

The plugin code is identical to 2.1.3. This release exists so that the next
"gate signed off" claim is checkable in the Actions tab rather than only on my
machine.

### Still true

The gate proves `apply()` emits calls that land on SDK-declared seats with a
non-null component. It does **not** prove anything renders — no `DEEPSEEK_API_KEY`
here. (pr-genius *has* been mounted in a real DSH web host — that is where #100/#101/#103 came from — but not since these fixes.)


## [2.1.3] - 2026-10-03

> First release that a **runtime gate** signed off on. Everything before this was
> verified by compiling or by grepping, and three of those releases shipped
> claims that did not hold.

### Added
- **Release runtime smoke gate** (`npm run smoke:release`, wired into
  `prepublishOnly` and `.github/workflows/release-smoke.yml`). Packs a real
  tarball, unpacks it, imports the artifact entry, calls `apply()`, and compares
  the calls it emits against DSH SDK's own `CLIENT_SLOT_API`. Exit 0 = the
  release claims hold, 1 = they do not, 2 = unverifiable. (issue #96)
- **Runtime slot probing.** The panel seat carries a candidate list and `apply()`
  tries each key, keeping whichever the host accepts. If none is accepted the
  surface is not registered — 宁缺勿假. No static slot name survives in the
  registration path. (issue #97)
- **Surfaces render real data.** Knowledge-base counts come from the corpus, the
  advisor surfaces show real `coach` output, preferences show the 12 Config
  fields' current values. Data reaches the UI through the MCP bridge; nothing is
  reimplemented in TypeScript. (issue #98)

### Fixed
- `register` options for list slots carry `id`, not `kind` — the gate caught both.

### What the gate found and what it means

Two catalogs disagree, and the disagreement is not academic:

| source | keys | `details` | `sidebar.right.pane.tab` |
|---|---|---|---|
| pinned npm package (what a user installs) | 42 | present | absent |
| upstream `deepseek-harness@master` | 92 | absent | present |

A user installs the pinned package. Rather than pick a side, the plugin probes.
The gate's output after the change:

```
  ✓ sidebar.footer.action   list     root     required=[id]
  ✓ conversation.view       list     session  required=[id]
  ✓ details                 single   session  required=[]   ← probe chose the pinned key
  ✓ settings.section        list     root     required=[id]
  VERDICT: PASS_WITH_WARNINGS   exit 0   FAIL=0
```

The 2 warnings are the 50-key catalog drift (reported, never merged into one
list — merging would validate against a catalogue no host has) and the
degradation path the gate also exercises.

### Honest boundary

The gate proves `apply()` emits calls that land on SDK-declared seats with a
non-null component. **It does not prove anything renders.** There is no
`DEEPSEEK_API_KEY` on this machine and pr-genius has never loaded in a real DSH
web host. Host-mounting behaviour still needs a real runtime.

## [Shipped in 2.1.3] — staging notes kept for the gate-findings narrative

> **⚠️ 这不是待发布块。** 下面这批条目当年写在 `## [Unreleased]` 里，实际已经
> 随 **2.1.3** 发布（smoke gate / issue #96、#97、#98 在上面的 2.1.3 小节里有正式
> 条目），但暂存块本身没被清掉，一直夹在 2.1.3 与 2.1.2 之间，看起来像还有未发布
> 的工作。现在改掉标题，内容原样保留 —— 尤其是下面「gate 在 v2.1.2 上报了什么」
> 那段，是当时翻车的现场记录，不该随清理丢掉。
>
> 新的待发布条目请写在文档**最上方**的 `## [Unreleased]`（若有），不要写在本节。

### Added
- **Release runtime smoke gate** (`scripts/release-smoke/`, `npm run smoke:release`,
  `.github/workflows/release-smoke.yml`, wired into `prepublishOnly`). Packs a real
  tarball, unpacks it, imports the artifact entry, calls `apply()`, and compares the
  slot keys it actually registers against DSH SDK's own `CLIENT_SLOT_API`. Human- and
  machine-readable output; exit 0 = the release claims hold, 1 = they don't,
  2 = unverifiable. (issue #96)
- The gate's slot list is **not** written anywhere in this repo. It is read from
  `@deepseek-ai/dsh-cordis-client-runner`'s compiled `CLIENT_SLOT_API` (the build of
  `packages/extensions/cordis-client-runner/src/client/slot-catalog.ts`), version-pinned
  by `package.json`, with `gh api` against `deepseek-ai/deepseek-harness@master` as a
  cross-check. If neither resolves the gate reports "authoritative catalog unavailable"
  and exits 2 rather than substituting a built-in list. A self-check scans the gate's own
  source for planted slot names and fails on any hit — a hardcoded list is circular
  validation: it can confirm errors but cannot falsify them.

### Reported by the gate on v2.1.2 as it stands (not fixed here)

The gate is **red** on the current registration, which is the point. Against the pinned
SDK catalog (`@deepseek-ai/dsh-cordis-client-runner@0.0.1-rc.3`, 42 keys — what a user
actually installs):

| Finding | What `apply()` does | What the SDK catalog says |
|---|---|---|
| `C1` | `inject('sidebar.right.pane.tab', …)` | that key does not exist in the pinned catalog |
| `C4` | `register({ name, kind }, …)` on `sidebar.footer.action` / `conversation.view` | list slots require `id`; `kind` is not a register option |

Also recorded: the pinned catalog and upstream `master` have drifted (42 vs 92 keys).
Upstream has `sidebar.right.pane.tab` (`keyed`/`session`) but **not** `details`; the
pinned version has `details` (`single`/`session`, occupied by `client-ui-conversation`
`DetailsPanel`, `packages/client/ui-layout/src/client/index.ts:72`) but **not**
`sidebar.right.pane.tab`. A release claim written against upstream will not land on the
host a user actually runs. The gate validates against the pinned version and reports the
drift as a warning.

Nothing in the plugin's registration is changed by this entry — that is separate work.
The gate's job is to stop a claim like these from shipping unchallenged again.

### Fixed
- **The four surfaces render real data instead of `null` / placeholder copy.**
  (issue #98) Dashboard shows knowledge-base scale and install health from
  `prgenius_doctor` (numbers come from the analyzer, never typed into the UI),
  in-flight PR rows from `status_prs` when an author is configured, Advisor runs
  `coach_pr` and projects tier / signals / checklist / merge probability /
  coverage, Preferences is a live readout of `service.describe()`. Every value is
  fetched through `service.callTool` over the real MCP transport and verified in
  `test/surface-data.test.ts` against a direct Python call plus a
  `renderToStaticMarkup` assertion.
- **Slot contracts now match the authoritative slot-catalog, and registration
  degrades conservatively.** Declarations claimed `conversation.view` and
  `sidebar.right.pane.tab` were `single`; the catalog says `list` and `keyed`.
  Registration now uses the catalog's `register({ name, id | key })` shape,
  Preferences lands on `settings.plugins.tab`, and any slot not verified against
  the catalog snapshot is skipped with a warning instead of registered on a
  guessed key. `docs/slot-catalog-evidence.json` freezes the fetched catalog
  (92 keys from `deepseek-ai/deepseek-harness`, 2026-10-03). Note: there is no
  slot key named `details` — that is an AppFrame seat name inside `root`'s docs.

  > **⚠️ CORRECTION (2026-10-04)** — two claims in the bullet above are wrong.
  >
  > 1. **"Preferences lands on `settings.plugins.tab`"** — no. `SURFACE_PLAN`
  >    seats Preferences on `settings.section`, and the release gate's ledger
  >    records the host accepting `settings.section` (list/root). The constant
  >    `PREFERENCES_SLOT` also wrongly read `sidebar.footer.action` (the
  >    dashboard seat) — fixed in 2.1.5.
  > 2. **"there is no slot key named `details`"** — that is only true of
  >    **upstream master**. The **pinned** SDK a user actually installs
  >    (`@deepseek-ai/dsh-cordis-client-runner@0.0.1-rc.3`, 42 keys) *does*
  >    declare `details` (`single`/`session`), and the 2.1.5 gate registers the
  >    panel into it successfully. The two catalogs disagree; the sentence above
  >    looked at only one of them and stated a universal negative. Registration
  >    therefore probes `details` first and `sidebar.right.pane.tab` second, and
  >    degrades if neither exists (宁缺勿假).
- **Slot keys are checked against the upstream DSH slot catalog before any
  registration.** `src/ui/slot-catalog.ts` is the single source of truth: the
  92 keys parsed out of
  `deepseek-ai/deepseek-harness:packages/extensions/cordis-client-runner/src/client/slot-catalog.ts`
  (blob `7c8f7af1`, commit `2db0c83e`, 2026-10-02) plus the seats the four
  surfaces use. A seat missing from that catalog is **not registered** — the
  plugin logs a warning instead of inventing a key. (issue #97)
- `conversation.view` is declared `list/session` and `sidebar.right.pane.tab`
  `keyed/session`, matching the catalog. v2.1.2 declared both `single`, which
  is wrong even where the key existed: a keyed seat requires the `key` register
  option, and the old call passed `kind` — not a register option at all —
  while `name` carried the surface id instead of the slot key.
- Preferences moved to `settings.section` (list/root, "one settings page per
  list entry"), the settings landing the catalog actually offers.

### Changed
- `src/ui/surfaces.ts` and `src/client/slots.ts` no longer each define slot
  names: both derive from `REGISTERED_SLOTS`, and a compile-time assertion
  keeps the `declare module` literals in sync.
- Verification is no longer self-referential. `scripts/verify-slot-keys.mjs`
  fetches the upstream catalog and `test/slot-catalog.test.ts` parses those
  bytes into the allowed set before running `apply()`; the allowed set never
  comes from the plugin's own constants.

### Known limits
- No DSH host run yet (no `DEEPSEEK_API_KEY` here): component mount and the
  keyed `sidebar.right.pane.tab` dispatch are unverified at runtime.
- Preferences is read-only: the service has no config-write API, so no fake
  save button.

## [2.1.2] - 2026-10-03

> **Cut because 2.1.1 repeated the exact mistake 2.1.0 made.** The slot-key fix
> in 2.1.1 landed in a module `apply()` never reads, so the shipped bundle still
> injected invented slot names. Verified against a simulated DSH host this time,
> not against a grep.

### Fixed
- **`apply()` now registers into slots that actually exist.** 2.1.1 fixed the
  keys in `src/client/slots.ts` and left `src/index.ts` importing
  `src/ui/surfaces.ts`, whose `SURFACE_PLAN` is the table `apply()` reads. That
  table still said `ui-sidebar` / `ui-settings-plugins` — names I inferred from
  tutorial prose, neither in the shipped catalog. The bundle carried both sets
  and the runtime used the wrong one; `client/slots.ts` was dead code. (issue #95)

### Changed
- `SETTINGS_SURFACES` in `src/ui/surfaces.ts` is the single source for every
  placement — `sidebar.footer.action` (root list), `conversation.view` (session),
  `sidebar.right.pane.tab` (session). `client/slots.ts` derives from it rather
  than declaring its own copies; two tables for one fact is what let them drift.
- The invented names are gone from comments too, so a grep finds nothing rather
  than the paragraph where I explained they were wrong.

### Verified

Simulated a DSH host that only accepts keys in the real catalog, called
`apply()`, and looked at what landed:

```
sidebar.footer.action   -> pr-genius.dashboard     component=REAL
conversation.view       -> pr-genius.advisor-tab   component=REAL
sidebar.right.pane.tab  -> pr-genius.advisor-panel component=REAL
sidebar.footer.action   -> pr-genius.preferences   component=REAL
SKIPPED (not in DSH catalog): none
```

Stale keys in `dist`: **0**. `tsc` 0, `vitest` 34 passed, `validate --strict` 0.

### The pattern, recorded so it stops recurring

Three releases, one shape:

| | changed | verified | user hit |
|---|---|---|---|
| #89 | `parse_frontmatter` | called `parse_frontmatter` | `load_anti_patterns` → `_parse_simple_frontmatter` |
| #90 | `src/client/*` | `tsc` + `grep dist` | entry never imported it |
| #95 | `src/client/slots.ts` | `grep dist` found the keys | `apply()` read the other table |

"Exists in the artefact" is not "fixed on the path a user takes." The runtime
simulation above is the check that would have caught all three.


## [2.1.1] - 2026-10-03

> **This release exists to make two v2.1.0 claims true.** Both were wrong as
> published, were verified wrong against the published artifacts, and are
> retracted in the v2.1.0 entry below.

### Fixed
- **Block scalars no longer leak a literal `|` — for real this time.** v2.1.0
  claimed this and shipped without it, because the fix landed in
  `parser.py::parse_frontmatter` while the analyzer's load path
  (`evaluator.py::load_anti_patterns`) calls `_parse_simple_frontmatter`. Same
  file, different function. **12/251 patterns still leaked after 2.1.0.** Both
  parsers now share one `_fold_block_scalars` pre-pass and one `_finish_scalar`.
  Verified on the path production uses: `load_anti_patterns('.') -> 0/251`.
  (issue #51, #89)
- **The client layer is now in the bundle.** v2.1.0 claimed slots were declared
  by augmenting `SlotMap` and components were React. The modules existed in the
  source tree and were **not imported by `src/index.ts`**, so they never shipped;
  `dist/index.mjs` contained neither, and `apply()` still registered `null` as
  the component. The entry now imports the layer, and `register` gets a real
  component per surface. (issue #90, #86)
- **Slot keys match the platform's catalog.** `ui-sidebar` and
  `ui-settings-plugins` were names I inferred from tutorial prose; neither
  exists in the shipped catalog. Replaced with `sidebar.footer.action` (root
  list), `conversation.view` (session), `sidebar.right.pane.tab` (session) —
  read from the reference plugin's source. (issue #86)

### Changed
- Test runner is **vitest**, not `node --test`. Node's strip-only type removal
  does not handle JSX (`ERR_UNKNOWN_FILE_EXTENSION .tsx`) — the same class of
  limit as the constructor parameter properties in #2724. The platform's
  components are `.tsx`, so a JSX-aware runner is required. 34/34 pass.

### Not fixed (recorded so it is not forgotten)
- #57 `contributor_view` documentation, #58 `issue`/`issue-batch` docs
- #64 `test_crawler_friendly_count` still fails on live GitHub data
- #65 `validate.py` still exits 2 with a confusing message when PyYAML is missing
- #66 trigger coverage is now **measured** (`scripts/measure_pattern_coverage.py`)
  but the 96%-do-not-fire problem itself is not solved; measuring is the
  prerequisite, not the cure
- #59 #61 #62 #63 #70 #71 #72 were addressed earlier and have receipts on the
  issues; they are listed there rather than here.


> **⚠️ CORRECTION (2026-10-03)** — two claims below the 2.1.0 entry were wrong as
> published and are retracted inline:
> 1. "YAML block scalars no longer leak a literal `|`" — the fix did not reach
>    the analyzer's load path; **12/251 patterns still leak** (issue #89).
> 2. "Slots are declared by augmenting `SlotMap`, components are React" — those
>    modules are not imported by `src/index.ts` and are absent from the shipped
>    bundle; `apply()` still passes `null` as the component (issue #90, #86).
>
> Both were verified against the published `prgenius-core==2.1.0` / `pr-genius@2.1.0`
> artifacts. The 2.1.0 artifacts remain published; the corrections live here and
> in the linked issues.

## [2.1.0] - 2026-10-03

### Added
- `prgenius doctor` — install/data/MCP self-test, for the "why is my analysis
  empty" case. Answers: Python and package versions, knowledge-base
  readability, whether `gh` is usable, whether the MCP service connects.
  Also exposed as the `prgenius_doctor` MCP tool (the tool count is now 14).
- `scripts/measure_pattern_coverage.py` — measures how often pattern triggers
  actually fire on real PR text, so "generic" has a criterion instead of being
  an adjective.
- `scripts/print_data_scale.py` — reproducible corpus counts.

### Fixed
- **`status` no longer dies when `gh` is present but unexecutable** (WSL with a
  Windows-only `gh` in PATH). The curl + `GITHUB_TOKEN` fallback existed in
  `333ac8b` and had been lost; it is restored and widened — the historical gate
  caught only `FileNotFoundError`, while the reported traceback is
  `PermissionError`. `auto-ping` and `auto-rebase` write paths use the same
  helper. (issue #55)
- **YAML block scalars no longer leak a literal `|`** — *partially* (see correction).
  The fix landed in `parse_frontmatter`, but the analyzer's load path
  (`evaluator.py::load_anti_patterns`) calls `_parse_simple_frontmatter`, which
  does not understand block scalars. Measured against the 2.1.0 package:
  **12/251 patterns still leak `|`.** The CHANGELOG for 2.1.0 claimed this was
  fixed; that claim was wrong and is retracted here. (issue #51, #89)
- **URL list items no longer parse as dicts.** `- https://…` split on its colon
  into `{"https": "//…"}`, dropping the scheme into the key. (issue #60)
- `merge_probability` no longer presents a tier default as if measured — it now
  returns `basis: measured` with a real rate, or `merge_probability_degraded`
  with a reason. A URL string in `external_merge_rate_30` is no longer coerced
  into a number. (issue #68)
- `triage` no longer passes silently when no policy is loaded. (issue #63)
- MCP `list_open_prs` honours its `repo` argument. (issue #74)
- `coach` / `analyze` JSON carries `impact` and `review`. (issue #61)

### Changed
- Dependencies build against `@deepseek-ai/cordis` 4.0.4 and
  `@deepseek-ai/schemastery` 3.18.4 — the platform's own packages — not the
  public `cordis` / `schemastery`. Two different `Context` types; a plugin
  compiled against one is not assignable to the other's `Plugin<any>`.
- Slots and components — **the 2.1.0 claim here was wrong and is retracted**.
  `src/client/slots.ts` (SlotMap augmentation) and `src/client/AdvisorPanel.tsx`
  (React components) exist in the source tree but are **not imported by
  `src/index.ts`**, so they never reach the bundle. `dist/index.mjs` contains
  neither, and `apply()` still calls `register(..., null)`. The shipped bundle's
  slot behaviour is unchanged from 2.0.0. (issue #90, #86)
- README, `docs/BLOG.md` and `docs/dsh-integration.md` re-measured: 943 patterns
  (251 anti + 692 success) across 67 repos, 14 MCP tools. The unmeasurable
  "100% quality pass rate" claim is removed rather than replaced, and the
  comparison table that summed to 2116 against a real 943 is gone.
  (issues #52, #53, #54, #56, #73, #75)
- Success patterns documented as retrieval/reference only — they do not feed
  scoring. (issue #69)


## [2.0.0] - 2026-10-03

### Added
- **DSH (Cordis) plugin.** `name` / `inject` / `apply` / `provide` contract with a
  Schemastery `Config`: 12 tunables, every one settable from `cordis.yml` without
  touching code, and invalid values fail at load naming the field.
- **Four surfaces** on the researched slot map: PR Intelligence Dashboard (sidebar),
  Advisor session tab (`conversation.view`), the same as a right-hand panel, and
  `/prgenius`. Maintainer mode is the same surfaces on a different projection.
- `locale/` with EN and 简体中文.
- `docs/dsh-ui-slot-api.md` — the UI slot / sidebar / settings contract this was
  written against.
- `docs/compatibility.md` — DSH version matrix, every cell marked unrun.
- `docs/maturity-self-assessment.md` — form completeness 70%, engineering
  convergence 100%, equal-weighted 85%.
- `scripts/check_dsh_plugin_contract.py` — structural conformance without a
  runtime: 27/27 blocking checks.
- `tsdown.config.ts`, `.oxlintrc.json`, `tsconfig.json` (strict).

### Changed
- Version is now a single source: `prgenius/pyproject.toml` fans out through
  `scripts/sync_version.py` to `server.json`, `glama.json`, `package.json` and
  `Dockerfile`.
- `package.json` `exports` point at the built `dist/*.mjs`, not TypeScript source;
  `prepublishOnly` builds and tests before publish.

### Fixed
- TypeScript constructor parameter properties broke Node strip-only type
  stripping (`ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX`); fields are declared longhand.
- Probing for `ctx.command` threw before the probe could run — Cordis reads of
  absent properties raise, so detection now goes through `Reflect.has`, and
  `inject` stays empty so the plugin still loads without a web host.

  > **⚠️ CORRECTION (2026-10-04)** — the mechanism in the bullet above is wrong
  > in the DSH host, and the belief that "Detecting with `Reflect.has` is safe"
  > is what shipped issue #100. Verified against the shipped guard at
  > `node_modules/@deepseek-ai/dsh-cordis-client-runner/lib/client.js`
  > (`dynamicCordisContext`):
  >
  > - `ctx.<name>` **direct read** → `readService(prop, true)` → requires the
  >   name in `inject`, else `denyRead` **throws**.
  > - `Reflect.has(ctx, '<name>')` → the proxy's `has` trap → returns
  >   `declared.has(name)`. **It returns false; it does not throw.** The premise
  >   above ("detection runs") was therefore false all along.
  > - `ctx.get('<name>')` → `readService(name, false)` → the optional lookup,
  >   documented in cordis `ReflectService.get` as "without the inject
  >   requirement".
  >
  > Consequence: with `inject: []`, `Reflect.has` is always false in a real DSH
  > host, so the probe short-circuits and **no UI surface is ever registered** —
  > a silent no-op behind a reassuring log line, which is exactly what local
  > mocks hid (they attach `slots` as a plain property, bypassing the guard).
  >
  > Note also that listing `'slots'` in `inject` is **not** the fix: cordis
  > `Plugin.Base.inject` is a hard load gate ("it only loads while all are
  > available"), so that would turn "no web host" into "plugin does not load",
  > which the bullet above was trying to avoid. Optional seats are read through
  > `ctx.get()`.

---

> **⚠️ HISTORICAL SECTION BEGINS** — everything below this line is the pre-2.0
> changelog, spliced in during a docs merge. It is kept verbatim as history, but
> it is **not** maintained here: its own `## [Unreleased]` block is a stale
> staging area from the 1.x era and has no bearing on current work. Live entries
> for 2.x and onward are the sections above. Do not append below this line.

All notable changes to pr-genius are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this repo uses
GitHub tag/release compare links per Keep a Changelog guidance.

**版本口径说明**：本文档区分三种版本标识——
- **Package Version**：PyPI 发布版本号（`prgenius-core`）
- **Git Tag**：仓库标签
- **Milestone**：功能里程碑（可能跨多个 tag）

## [Unreleased]

### Added
- **coach 结构性检查 (issue #45)**: `prgenius/src/prgenius/structural.py` — 纯静态启发式，
  不执行 PR 代码，覆盖两条表层关键词抓不到的结构性反模式
  - `fabricated-evidence-in-claim`: 代码块里贴的输出与命令必然输出不一致
    （`print(表达式)` 却贴出 `SUCCESS:` 前缀 → critical，需人工复核，阻塞）；
    贴了输出但全篇无可核对命令 → high，需人工复核，列清单不阻塞
  - `state-derived-from-nonexistent-source`: 引用 `data/*.jsonl` 或 frontmatter
    字段驱动状态 → high，列清单并提示"先给命中数证据"
- **coach 退出码约定**: severity=critical 反模式命中 → exit 1 阻塞；
  severity=high → exit 0 但列进 checklist（P1）；非反模式 high 信号（merge_conflict 等）语义不变
- **pytest 回归**: `prgenius/tests/test_structural_checks.py` — 含 review-cases/
  302 条真实 PR 案例误报回归（防"泛词误报导致 coach 一律 high_risk"复发）

### Changed
- **anti-pattern 匹配**: `check_anti_patterns()` 命中项新增 `severity`/`match_mode`/
  `match_type` 字段；`match_mode: structural` 的反模式关键词弱命中降级为 high
  （列清单不阻塞），只有结构证据才按声明 severity 走

## [1.9.1] — Dockerfile Fix for Glama Build

### Fixed
- **Dockerfile**: `COPY pyproject.toml` failed because file is in `prgenius/`, not root
- **Dockerfile**: Invalid shell syntax (`COPY ... 2>/dev/null || true`) replaced with `COPY . .` + `.dockerignore`
- **Orphan files**: Added 7 missing anti-pattern references to resolve CI orphan warnings

## [1.9.0] — GitHub Marketplace Launch

### Added
- **GitHub Marketplace**: Root `action.yml` for one-click Marketplace install
  - Use `uses: zsxh1990/pr-genius@v1` instead of nested path
  - Branding: check-circle / green
  - Published as "PR Genius Advisor" on GitHub Marketplace

### Fixed
- **Version alignment**: pyproject.toml + glama.json + CHANGELOG aligned on 1.9.0
- **AUDIT_REPORT_20260905.md**: Added missing frontmatter (validate CI gate)
- **CI hardening**: Pin mcp<2.0 for API compat, Python 3.9 `__future__` annotations
- **Audit improvements**: Security, tests, CI, and docs (4 critical, 22 high addressed)
- **Orphan cleanup**: Archived orphan anti-patterns, fixed dead links

## [1.8.0] — comment_mode PR Comment Feature

### Added
- **PR Genius Check action**: `comment_mode` input (`never` / `high_risk` /
  `always`) — post the full analysis as a visible PR comment, mirroring
  pr-agent's `/review`. Existing comments are updated in place via a
  `<!-- pr-genius:report -->` marker (no comment spam on repeated syncs).
  Legacy `comment_on_high_risk: true` still works (acts as `high_risk`).
- **`post_comment.py`**: Structured comment renderer with tier icons,
  severity icons, positive/negative/neutral signals, checklist,
  anti-patterns, and repo context. Advisory-only (never fails workflow).

### Fixed
- **`post_comment.py`**: `anti_patterns_hit` contains string keys, not
  dicts. Use `anti_patterns_detail` (with severity/fix_action) for the
  Anti-Patterns section rendering. Fall back to key-only when detail unavailable.

## [1.7.2] — Docker Image & Bug Fixes

### Added
- **Docker Image**: Publish to GitHub Container Registry (GHCR)
- **GitHub Action**: Docker-based action with `docker://ghcr.io/zsxh1990/pr-genius:latest`
- **Auto-update**: Dependabot/Renovate support for Docker image version tracking
- **entrypoint.sh**: GitHub Action entry point supporting both CLI and Action modes

### Fixed
- **anti_patterns_hit**: Returns object array instead of string array (#28)
  - Now returns `[{key, description, severity, fix_action}]` as documented

### Changed
- **Version tags**: `v1` tag always points to latest `v1.x.x` release
- **publish-ghcr.yml**: Automated GHCR publishing on release

## [1.7.1] — suggested_fix Feature

### Added
- **suggested_fix**: Anti-patterns now include concrete code fix examples
- **YAML block scalar**: Support multiline `fix_example` with `|` syntax
- **CLI rendering**: Coach output displays suggested fixes as code blocks

### Fixed
- **ISSUE_LINK_RE**: Fixed false positive on "fixes formatting" without issue number

## [1.7.0] — Evidence Pipeline

### Added
- **enrich_cases.py**: Fetch real PR data from GitHub API and build evidence chains
- **extract_features.py**: Extract feature vectors from enriched cases
- **score_merge.py**: Weighted rule-based scoring model with 89.6% accuracy
- **generate_evidence.py**: Generate evidence chain reports with completeness verification
- **run_pipeline.py**: One-command pipeline orchestrator (enrich → features → score → evidence)
- **Pipeline tests**: 18 tests for evidence, features, and predictions validation

### Changed
- **Scoring accuracy**: 89.6% on closed cases (exceeds 80% target)
- **Evidence completeness**: 100% of cases have verified evidence chains
- **Feature coverage**: 10+ features per case (review engagement, author association, size, labels)

### Data
- **268 enriched cases**: Real PR data from GitHub API
- **268 feature vectors**: Structured features for scoring
- **268 predictions**: Merge probability predictions with evaluation metrics

## [1.6.3] — Issue Evaluator + CLI Entry Points

### Added
- **issue_evaluator.py**: Automated issue quality scoring with calibrated 5-dimension model (reproducibility, scope clarity, metadata completeness, actionability, secret risk)
- **CLI `issue` command**: Evaluate single issue by number (`prgenius issue <number>`)
- **CLI `issue-batch` command**: Batch evaluate issues from YAML/JSON config
- **Tier classification**: `high_risk` / `needs_work` / `ready` with secret risk override
- **Evidence collection**: Per-dimension evidence with per-item scores

### Fixed
- **Windows encoding**: `subprocess.run` with `encoding="utf-8", errors="replace"` prevents garbled terminal output
- **Issue-batch mapping**: Fixed `issues[batch["results"].index(r)]` KeyError — use `r['number']` and `r['title']` directly

### Changed
- **Output structure**: Aligned with PR Coach format (verdict dict with score/tier/summary/dimensions/evidence/next_steps)

## [1.6.2] — Composite Action Fix

### Fixed
- **action.yml duplicate inputs**: Remove duplicate `inputs:` section in composite action that caused `'inputs' is already defined` error for repos reusing PR Genius GitHub Action

## [1.6.1] — Diff Stat Integration + New Profiles

### Added
- **coach --diff-stat flag**: Pass git diff --stat for impact/review assessment
- **Action workflow diff_stat**: Workflow now extracts and passes diff_stat to coach
- **New profiles**: railtracks (144 stars), memex (17 stars)

### Fixed
- **Workflow diff_stat extraction**: Fall back to origin/main when HEAD~1 doesn't exist

### Changed
- **Test count**: 221 tests (unchanged)





## [1.6.0] — Phase 6: Contributor View

### Added
- **Contributor View** (`prgenius/src/prgenius/contributor_view.py`): 5-action decision for contributors
  - READY_TO_SUBMIT, FIX_BEFORE_SUBMIT, NEEDS_DISCUSSION, IMPROVE_CHANCE, ASK_MAINTAINER
  - Checklist generation (issue link, migration path, tests, security review)
  - Confidence level (low/medium/high)
  - Merge probability from shared evaluator
- **MCP contributor_view tool**: Exposed via MCP server
- **17 new tests**: Full coverage for contributor view

### Changed
- **Test count**: 176 tests (was 159, +17)

## [1.5.2] — Phase 5.2: Action Multi-Repo Support

### Added
- **Setup guide**: `docs/setup/README.md` — 5-minute guide to add PR Genius to any repo
- **Action parameterization**: Workflow uses `${{ vars.PR_GENIUS_URL }}` instead of hardcoded URL
- **Diff stat extraction**: Workflow extracts diff stat for impact assessment

### Fixed
- **No profile graceful degradation**: Already handled (returns medium_risk with no concerns)
- **Generic anti-patterns**: 559/562 anti-patterns are already generic (no repo field)





## [1.5.1] — Phase 5.1: Maintainer Decision Support Fields

### Added
- **`impact` field**: files_changed, lines_added/deleted, scope, breaking_change, security_sensitive, dependency_changes
- **`review` field**: complexity (low/medium/high), estimated_minutes, needs_domain_expert
- **`author_info` field**: association, first_time
- **`pr_metadata` module**: Impact/review assessment without GitHub API calls
- **18 new tests**: Full coverage for pr_metadata module

### Changed
- **maintainer_view**: Now returns impact/review/author_info fields
- **MCP maintainer_view tool**: Now accepts diff_stat parameter
- **Test count**: 159 tests (was 141, +18)


## [1.5.0] — Phase 5: Maintainer View

### Added
- **Maintainer View** (`prgenius/src/prgenius/maintainer_view.py`): 5-action routing for maintainer PR review
  - `review_ready` / `action` / `next_step` / `blocking_signals` / `review_queue_digest`
  - 20 unit tests (`tests/test_maintainer_view.py`)
- **CLI `maintainer-review` subcommand**: Quick maintainer review from CLI
- **MCP `maintainer_review` tool**: Exposed via MCP server
- **GitHub Actions auto-check workflow**: `.github/workflows/pr-genius-check.yml` with shell injection prevention
- **Positive confirmation summary**: `summary` field in coach output with 🟢/🟡/🔴 indicators

### Fixed
- **Anti-pattern false positives**: Stopwords filter + repo filter (14→0 false positives)
- **Validate version drift**: Synced Dockerfile/glama.json version
- **Missing frontmatter**: Added to `docs/maintainer/pr-review-queue.md`

### Changed
- **Test count**: 137 tests (was 110, +27 from Phase 5)


## [1.4.3] — Anti-pattern False Positive Fix

### Fixed
- **Anti-pattern false positives**: Added stopwords filter for generic PR words (file, test, this, etc.) and repo filter to only match anti-patterns from same repo or generic patterns. Reduced false positives from 14 to 0 for typical PR titles.
- **Regression test**: Added `scripts/regression_test.py` to verify summary field exists for all 63 profiles.



## [1.4.2] — Positive Confirmation + Auto-trigger

### Added
- **Positive confirmation summary**: Added `summary` field to coach output with emoji indicators (🟢/🟡/🔴). Borrowed from Cubic AI pattern.
- **GitHub Actions auto-check workflow**: `.github/workflows/pr-genius-check.yml` automatically comments on PRs with risk analysis.
- **Shell injection prevention**: Use `env:` vars instead of inline interpolation to avoid backticks/dollar-parens in PR body breaking shell.



## [1.4.1] — Bug Fixes

### Fixed
- **CLI `--repo-root` for harvest/profile subcommands**: `harvest`, `profile get`, `profile writeback` now accept `--repo-root` (previously resolved to wrong path in installed mode)
- **YAML inline comment stripping**: `_coerce()` now strips inline comments (`0.15  # comment` → `0.15`) before type coercion, fixing `TypeError` in evaluator when comparing `repo_merge_rate`
- **Anti-pattern YAML parse errors**: Fixed broken frontmatter in `contribai-auto-generated-trash.md` and `trusted-publisher-oidc-insufficient.md`
- **Missing frontmatter**: Added frontmatter to `docs/ROADMAP.md` and `docs/status-mvp-trial.md`
- **Profile evidence dict**: Added `agent_guidelines_evidence` to 4 profiles that had guidelines but no evidence dict

### Changed
- **Test count**: 110 tests (was 63 in v1.4.0 trial, +47 from Phase 3-4 additions)


## [1.4.0] — Package + Git Tag

### Milestone: Phase 1 稳定运营 ✅

### Added
- **Outbound PR Heartbeat** (`scripts/pr_status_heartbeat.sh`): 双账号心跳脚本
  - `--author` / `--all` 参数
  - 人类可读表格 + JSON 快照
  - exit code 0=无行动, 1=有可执行行动
- **Profile Data Boundary**: PUBLIC/PRIVATE 字段分类
  - `PROFILE_PUBLIC_FIELDS` / `PROFILE_PRIVATE_FIELDS` 常量
  - `profile writeback` 子命令（dry-run 模式）
- **Profile Writeback Suggestions**: 基于 PR 状态自动推断
  - `--writeback-mode suggest|auto`
  - confidence 门控（< 0.6 拒绝, ≥ 0.8 auto 模式自动写入）
  - evidence/source/confidence 字段完整
- **Transition Alert Enhancement**: 告警增强
  - `--alert-only` flag: 只输出有状态变化的 PR
  - severity 级别: critical（WAITING→NEEDS_REBASE）/ info（STALE→CLEAN）
  - 🚨/ℹ️ 图标区分
- **MCP Tools**: 2 个新工具（总计 10 个）
  - `status_prs`: outbound PR 健康检查
  - `profile_writeback_suggestions`: profile 更新建议
- **MisakaNet #773 合并**: PR Genius v1.3.1 advisory observation
  - 12 PR 观察, 100% 准确率
  - Workflow 硬化: 去 checkout, pin SHA, continue-on-error
  - Closes #756

### Changed
- 版本号: 1.3.0 → 1.4.0（pyproject.toml / __init__.py / server.json / glama.json / README）
- 描述更新: "Outbound PR CRM", 62 repos, 1455 patterns
- 测试覆盖: 33 → 39 全绿



## [1.3.1] — Git Tag only (Package: 1.3.0)

> ⚠️ 此 tag 仅修复 Action JSON 契约，未发布到 PyPI。Package version 仍为 1.3.0。

### Fixed
- **P0 Action JSON Contract**: `analyze --format json` 输出稳定
  - `tier` 不再是 `unknown`
  - JSON 无效时 `::error::` + `exit 1`
  - MisakaNet #773 验证通过（tier=high_risk）

### Milestone: Status Mode MVP ✅
- 9 状态分类 + 优先级规则
- GraphQL 批量查询（13 PR, 5s）
- Repo profile 接入 `stale_days_threshold`
- `--save-snapshot` + transition 侦测
- 33 单元测试全绿

### Compliance
- **OKF v0.1 合规审计** (克莱恩 2026-07-19 拍板): upstream
  [Sudhakaran88/okf-conformance](https://github.com/Sudhakaran88/okf-conformance)
  validator 实测 **PASS conformant · exit 0 · 0 errors · 0 warnings**.
  - 修复 4 MUST errors (M2 frontmatter + 3× M4 relative path)
  - 修复 120 SHOULD warnings (97 S4 orphan + 23 S2 sibling chain)
  - 命名规范化: docs/INDEX.md → docs/index.md (OKF M5 path identity)
  - 新增 docs/COMPLIANCE_AUDIT.md (审计历史 + 已知方言清单)
  - 新增 archive/scripts/pr-genius-landscape-search/ (5 search/fetch 脚本)
  - validate.py type 白名单加 Compliance Audit
- See docs/COMPLIANCE_AUDIT.md for full audit history.



## [1.3.0] - 2026-07-24

### Added
- **Daily content expansion** (552+ cases, 33 repos, 87% coach accuracy)
- **Electron repo profile** (122k stars, C++)
- **20 Electron PR cases** for training
- **Glama deployment** (MCP server + Dockerfile)
- **Tool call prediction table** with A/B testing

### Added (方舟 35 期评测反哺)
- **Check 7 policy_freshness** (`validate_checks/policy_freshness.py`)
  - Maintainer Policy + Repo Profile 超过 90 天 = warn
  - lesson-19 (in-sample 配 holdout) 的评分系统兏底
- **Check 8 release_audit** (`validate_checks/release_audit.py`)
  - pyproject / __init__ / glama.json / Dockerfile / CHANGELOG 版本对齐
  - 课程从 35 期 ether2 REVIEW_FINDINGS.md §1 抓的版本漂移
- **`scripts/anti_overfit.py`** (双指标 LORO + time-split)
  - 替换原 `anti_overfit_loro.py` (单 LORO)
  - 学自 husk2 scripts/anti_overfit.py (v1.5.2)
  - 跑出 4 仓真问题: mongodb LORO -84.5% / vercel/next.js time-split -50% /
    pydantic -44.7% / astral-sh/ruff -35.7%
- **MCP stdio roundtrip 测试** (`prgenius/tests/test_mcp_stdio.py`)
  - 10 个 test (8 tools 全覆盖 + B1/B2 regression)
  - 10 passed in 0.47s
- **data/anti_overfit_report.json** (600 行双指标产物)
  - 可作 lesson-17 "data snapshot README metric unification" 输入
- **lesson-19/20/21** (3 条 A 级, misakanet-50/)
  - lesson-19: Overfit Hard Gate (LORO + time-split required)
  - lesson-20: Honest Claim vs Runtime Evidence (诚实声明 + 实跑 4 形态分级)
  - lesson-21: MCP stdio Runtime Bug (static analysis misses field-path failures)

### Fixed (35 期评测抓到)
- **B1 soft_violations 路径错配** (`prgenius/src/prgenius/mcp.py`)
  - mcp.py:127 `len(result.get("soft_violations", []))` 改为
    `int(result.get("soft_violations", 0))` (triage.py 返回的是 int count)
- **B1' wrapper 漏传 labels** (`prgenius/src/prgenius/mcp.py`)
  - 底层 `triage.py:318` 不收 labels kwarg, wrapper 去掉 labels=
- **B2 _parse_frontmatter_dict 死导入** (`prgenius/src/prgenius/mcp.py`)
  - 改为现存的 `parse_frontmatter` (parser.py:96)
- **B3 .venv/site-packages 假阳** (`validate.py`)
  - SKIP_DIRS 加 .venv / venv / .tox / site-packages / dist / build
- **B5 eval_pr 死导入** (`prgenius/src/prgenius/mcp.py`)
  - 删 `from .evaluator import analyze_pr as _analyze_pr, eval_pr as _eval_pr`
    中的 eval_pr (mcp.py 内部不调用, cli.py:192 仍能用)

### Changed
- **CI gate 升级** (`.github/workflows/validate.yml`)
  - `--strict` 从 soft gate (`|| echo "::warning::"`) 改为 hard fail
  - Check 8 drift + Check 7 stale 在 errors.append 路径会硬卡 PR
- **Version 对齐**: pyproject.toml / __init__.py bump 1.2.0 → 1.3.0
  - 跟 glama.json / Dockerfile 同步
  - 35 期评测 ether2 §1 抓的 "glama/Dockerfile 1.3.0 vs init/pyproject 1.2.0" 漂移修复



## [1.2.0] - 2026-07-18

### Added
- **Daily content expansion**: `scripts/daily_content_expand.py`
  - 自动从 32 个大中仓采样 50 PR/天
  - 7 类质量配额（merged/closed/review/open）
  - 每日 20:37 cron 触发
- **Coach fit report**: `scripts/coach_cases.py`
  - 预测 vs 实际结果对比
  - 156 case, 24 repo, 85% 准确率
- **13 new repo profiles**: httpx, checkout, pydantic, markitdown, tailwindcss,
  huggingface, terraform, docker-compose, cli, openai-python, rust-lang,
  react, fastapi, chroma, qdrant, TypeScript, ruff, deno, golang, anthropics, prometheus
- **Maintainer Policy Memory**: `docs/policies/Ikalus1988-MisakaNet.md`
  - 基于 PR #491-#497 锚点的 9 条维护者政策
  - triage 指南 + hard/soft 分类
- **Shared utilities**: `prgenius/src/prgenius/utils.py`
  - run_gh, fetch_recent_prs, get_merge_rate, classify_pr, extract_signals

### Changed
- **evaluator**: 合并率 >0.8 的大仓取消"首次大仓提 PR"负面信号
  - 准确率从 79% 提升到 87%（121 case）/ 85%（156 case）
- **Signal extraction**: 新增 8 个 metadata-based 信号
  - is_small_pr, is_large_pr, is_backport, is_dependency_update,
    is_bot_pr, has_reviews, has_comments, change_ratio
- **validate.py**: 新增 "Test Report" 合法 type
- **Version**: 统一为 1.2.0（README + pyproject.toml + __init__.py）

### Fixed
- README version 1.1.1 → 1.2.0（与 pyproject.toml 一致）
- 根 index.md 同步 35 个仓库画像



## [1.1.1] - 2026-07-09

### Fixed
- **MCP surface rewrite**: `analyze_pr` / `coach_pr` 替代旧 `eval_pr` / `suggest_pr`
  - 别名导入防止函数遮蔽 (`from .evaluator import analyze_pr as _analyze_pr`)
  - 旧 `suggest_pr` 已从 MCP 移除（v1.0.0 后不再存在）

### Changed
- **DCO 仓库感知**: 从 profile 读取 `requires_dco` / `require_signed_off`
  - `true` → P1 必做项
  - `false` → 不提示
  - 未声明 → P2 提醒
- **Bot 检测升级**: 白名单 + `[bot]` 后缀通用规则
  - `my-custom[bot]` 等未知 bot 也能正确识别
  - Bot PR 跳过 issue link 检查
- **predict_success_rate** docstring 标注 deprecated，仅供 cross_validate 历史兼容



## [1.1.0] - 2026-07-09

### Added
- **coach** command (Agent PR Dojo): `python3 -m prgenius coach "title" --repo org/repo`
  - exit 0 = pass (低风险/中风险), exit 1 = fail (高风险)
  - `--format json` for bot/agent consumption
- **harvest** script: `python3 scripts/harvest.py org/repo 123`
  - 从被拒 PR 自动提取 anti-pattern/lesson draft
  - 支持 `--type lesson` (MisakaNet 风格) 和 `--type anti-pattern`
  - 自动检测 self-close (作者自己关闭) via events API
- Ikalus1988-MisakaNet repo profile
- validate.py accepts Success Pattern, Skill, Retrospective types
- index.md updated with tools section + all 21 repos

### Fixed
- skill/skill.md: added missing `type: Skill` field
- validate.py --strict now passes (0 errors)

### Changed
- Version unified to 1.1.0 across __init__.py, pyproject.toml, CHANGELOG



## [1.0.0] - 2026-07-09

### Changed (BREAKING)
- **从"合并概率预测器"转为"提交前改进顾问"**
- 新增 `analyze` 命令: 结构化信号 + 可操作建议 + 三档风险 (🟢低/🟡中/🔴高)
- `eval` 降级为三档，不再显示百分比
- 砍掉成功模式匹配从评分中移除（语义太粗，泛化差）
- 反模式检测 + 标签信号 + author 历史 → 直接输出 actionable 建议
- `predict_success_rate` 保留为内部兼容函数仅供 cross_validate 使用



## [0.8.0] - 2026-07-09

### Added — Evaluator v0.4.0 (P3/P4/P6)
- `author_association` dimension: OWNER +0.40, MEMBER +0.25, COLLABORATOR +0.20,
  CONTRIBUTOR +0.05, NONE +0.0 — fixes 8/8 FN where MEMBER/OWNER PRs were
  misclassified as rejected
- CLI `--author-association` parameter for `eval` / `suggest`
- `duplicate` label signal strengthened from -15 to -25
- Success pattern per-match bonus reduced from +0.05 to +0.03 (issue link downweight)

### Changed — Evaluator v0.4.0
- Cross-validation accuracy: 80.0% → **87.2%** (180 PR, 9 repos)
- Merged recall: 86.0% → **95.9%**
- FN (漏报): 14 → **4**
- LibreChat: 45% → **85%**, langchain: 80% → **95%**



## [0.7.9] - 2026-07-09

### Added — Evaluator v0.3.0 (P0/P1/P2)
- `scripts/cross_validate.py` — automated cross-validation script (`--repo`, `--all`, `--limit`, `--verbose`, `--json`)
- 3 new anti-patterns: `ai-generated-content`, `missing-issue-reference`, `duplicate-pr-same-author`
- 9 large repo profiles: langchain-ai/langchain, yt-dlp/yt-dlp, microsoft/markitdown,
  langchain-ai/langgraph, onyx-dot-app/onyx, danny-avila/LibreChat, goreleaser/nfpm,
  python-jsonschema/jsonschema, woodruffw/zizmor
- Label signal layer (`LABEL_SIGNALS` dict): ai-policy-violation -20, missing-issue-link -10,
  duplicate -15, new-contributor -3, bug +5, help-wanted +5, etc.
- Bot PR independent channel: dependabot[bot], pre-commit-ci[bot], renovate[bot], etc.
  with size-based baseline (small 70%, medium 50%, large 30%)
- Dynamic baseline: `repo_merge_rate * 0.7 + 0.45 * 0.3`
- CLI parameters: `--body`, `--labels`, `--author`, `--star-count`, `--repo-merge-rate`

### Fixed — Evaluator v0.3.0
- P0: `issue-linked-fix` matching now uses regex `(fixes|closes|resolves)\s+#\d+` instead
  of substring match — eliminates false positives from "this fix addresses..." patterns
- Anti-pattern check now includes PR body (was title+description only)
- Success pattern matching now includes body in full_text for non-issue factors

### Changed — Evaluator v0.3.0
- Base rate: 0.50 → **0.45** (conservative)
- Thresholds: high 0.70→0.60, medium 0.40→0.35
- Cross-validation accuracy: 67.6% → **80.0%** (180 PR, 9 repos)
- Rejected recall: 50.0% → **72.5%**



## [0.7.8] - 2026-07-07

### Changed
- `prgenius` distribution renamed `prgenius-kb` → **`prgenius-core`**
  (drop the awkward `kb` suffix; align with `misakanet-core` naming
  convention). CLI entry point `prgenius-kb` → `prgenius-core`; import
  path `prgenius.cli` unchanged. PyPI publish still pending.



## [0.7.5] - 2026-07-05

### Added
- `archive/scripts/inject-round-evidence.py` — re-runnable round-level evidence
  installer (11/11 case round 1 + 4/4 amend rounds have `verified_at` /
  `evidence_urls` / `confidence`)
- `archive/scripts/refresh-badges.py` — regenerates `docs/badges/*.json` for
  dynamic shields.io endpoints (validate / evidence / round-evidence /
  profiles / cases / lessons / releases / latest-release / prgenius version)
- `docs/INDEX.md` synced with current counts (was stale on agentic #1382/#1383
  double-counted as 12 PRs instead of 11 case studies)



## [0.7.4] - 2026-07-05

### Changed
- CI workflow now hard-fails on `validate.py --enforce-evidence` (no more
  `|| echo ::warning::` soft gate) — future PRs missing case-level evidence
  get red build
- README adds `Evidence 100%` and `Latest release` shields

### Added
- Round-level evidence fields populated for all 11 case studies' round 1
  (`open` action) and 4 amend rounds (e2b / future-agi / honcho / fastmcp)
- `prgenius` package version bumped from `0.1.0` → `0.7.3` in
  `src/prgenius/__init__.py` and `pyproject.toml`

Compare: [0.7.3...0.7.4](https://github.com/zsxh1990/pr-genius/compare/v0.7.3...0.7.4)



## [0.7.3] - 2026-07-05

### Added
- Case-level `verified_at` / `evidence_urls` / `confidence` for **all 11** PR
  Case Studies (honcho / qdrant / uv / mongodb / agentic / e2b / future-agi /
  harbor / fastmcp / sourcebot) — `validate.py --enforce-evidence` 22 → 0

### Fixed
- 4 case frontmatter status drift corrections (uv#19685 → closed-not-merged,
  agentic#1382/#1383 → closed-merged, e2b#1413 → closed-not-merged)
- Released v0.6.3 / v0.6.4 / v0.7.0 / v0.7.1 / v0.7.3 GitHub Releases (5 added
  on top of pre-existing v0.6.0 / v0.6.1 / v0.6.2)
- `archive/scripts/git-push-via-api.py` — Git DB API fallback for when
  `github.com:443` is unreachable but `api.github.com:443` works (WSL
  network-route workaround)
- `archive/scripts/create-v07[1|3]-release.py` and
  `archive/scripts/create-v063-v064-v070-release.py` — release-creation
  helpers using the GitHub API

Compare: [0.7.1...0.7.3](https://github.com/zsxh1990/pr-genius/compare/v0.7.1...0.7.3)



## [0.7.1] - 2026-07-05

### Changed
- Realigned `CHANGELOG.md` — entries previously parked under `[Unreleased]` are now
  under the release they landed in (doc-drift fix only; no code diff)

### Fixed
- `prgenius` distribution renamed `prgenius` → `prgenius-kb` (PyPI name collision
  with an unrelated 2024 GPT-3 PR-description tool — uploader/purpose/maintainer
  all differ). Import path `prgenius.cli` unchanged.
- `prgenius/README.md` missing frontmatter (validate.py --strict was red)

### Added
- 5 PR Case Studies now carry case-level `verified_at` / `evidence_urls` /
  `confidence`: honcho#801, qdrant#143, uv#19685, mongodb#1309, agentic#1382
- `archive/scripts/refresh-evidence.py` — reusable GH-API fetch (5 endpoints × N
  PRs) for evidence refresh passes
- MCP `--repo-root` flag now actually flows through `cli.py cmd_mcp_serve` →
  `mcp.serve(repo_root=...)` → `_load_tools(rr)` (was parsed but ignored — every
  tool was reading the hardcoded module-level constant)
- MCP install/config snippets for Cursor / Claude Code / Cline in
  `prgenius/README.md` (MCP wiring section)

### Known issues
- G. `astral-sh-uv/pr-19685-sarif-audit.md`: case frontmatter says
  `status: merged / merged_at: 2026-06-05`; GH API returns
  `state=closed, merged=False, closed_at=2026-06-05T14:43:54Z`.
- H. `agentic-community-mcp-gateway-registry/pr-1382-auth-md-mermaid-token.md`:
  case frontmatter says `status: open`; GH API returns
  `state=closed, merged=True, merged_at=2026-07-04T16:30:18Z, merged_by=aarora79`.

### Stats
- 12 profiles / 12 case studies / 11 lessons / 12 anti-patterns
- validate.py --strict: 0 errors
- validate.py --enforce-evidence: 12 warnings (down from 22 pre-N1; 6 cases
  not yet refreshed)

Compare: [0.7.0...0.7.1](https://github.com/zsxh1990/pr-genius/compare/v0.7.0...0.7.1)



## [0.7.0] - 2026-07-04

### Added (BREAKING for delta shape, but BC over v0.5.0)
- `prgenius/` Python package — stdlib-only CLI (`python3 -m prgenius …`) and
  stdio MCP shell (`python3 -m prgenius mcp serve`)
- `ROUNDS_SCHEMA.md` v0.7.0 — `verified_at` / `evidence_urls` / `confidence`
  added to delta + case-level (all optional, backward compatible)
- `mcp[server]>=1.0` optional runtime dependency (only loaded when
  `mcp serve` is invoked; everything else stays stdlib)

### Stats
- 12 profiles / 12 case studies / 11 lessons / 12 anti-patterns

Compare: [0.6.4...0.7.0](https://github.com/zsxh1990/pr-genius/compare/v0.6.4...v0.7.0)



## [0.6.4] - 2026-07-04

### Added
- `misakanet-50/lesson-11` — mcp typo pool (real-failure category)
- `scripts/heartbeat.py` snapshot tool + `validate.py --heartbeat` mode

Compare: [0.6.3...0.6.4](https://github.com/zsxh1990/pr-genius/compare/v0.6.3...v0.6.4)



## [0.6.3] - 2026-07-04

### Added
- `agentic-community-mcp-gateway-registry/` profile + 2 PR Case Studies
  (pr-1382, pr-1383)

Compare: [0.6.2...0.6.3](https://github.com/zsxh1990/pr-genius/compare/v0.6.2...v0.6.3)



## [0.6.2] - 2026-07-04

### Changed
- 6 legacy PR Case Studies migrated to `rounds v0.5.0` schema (action enum +
  delta object + close_decision case-level)

Compare: [0.6.1...0.6.2](https://github.com/zsxh1990/pr-genius/compare/v0.6.1...0.6.2)



## [0.6.1] - 2026-07-04

### Added
- `SECURITY.md` — coordinated disclosure policy (private advisory + email)
- `DISCUSSIONS.md` — placeholder for GitHub Discussions until enabled
- `.github/ISSUE_TEMPLATE/config.yml` — chooser config linking to
  Discussions/Security/MisakaNet
- `.github/CODEOWNERS` — singleton maintainer marker
- `.github/FUNDING.yml` — sponsors entry
- `.github/social-preview.svg` — repo social preview source (requires manual
  upload via Settings → Social preview)
- `docs/INDEX.md` — agent-readable file map (P3 stub)
- Topics (10) on GitHub repo settings + extended description + homepage link
- `README.zh.md` Chinese mirror

Compare: [0.6.0...0.6.1](https://github.com/zsxh1990/pr-genius/compare/v0.6.0...0.6.1)



## [0.6.0] - 2026-07-03

### Added
- Community surface: README badges/Quick Start, CONTRIBUTING, CODE_OF_CONDUCT, LICENSE (MIT), CHANGELOG, .github/ (5 issue templates + PR template + dependabot + CI validate workflow)
- `scripts/heartbeat.py` + `validate.py --heartbeat` for daily validator snapshots
- `scripts/fix_lesson_yaml{,_v2}.py` repair tools for `last-updated` field
- `NousResearch-hermes-agent/index.md` (16KB profile)

### Stats
- 11 profiles / 11 case studies / 10 lessons / 4 anti-patterns

Compare: [0.5.3...0.6.0](https://github.com/zsxh1990/pr-genius/compare/v0.5.3...v0.6.0)



## [0.5.3] - 2026-07-02

### Added
- `misakanet-50/SCORING.md` — source credibility scoring system (4-dimension)
- `misakanet-50/score_source.py` — scoring automation tool

### Fixed
- `chore: ignore __pycache__ in misakanet-50/` (commit 2aa4468)

Compare: [0.5.2...0.5.3](https://github.com/zsxh1990/pr-genius/compare/v0.5.2...v0.5.3)



## [0.5.2] - 2026-07-02

### Added
- 5 real-failure lessons in `misakanet-50/lesson-06` through `lesson-10`
- Archive flag on 5 news-style lessons (lessons not suitable for distillation)

Compare: [0.5.1...0.5.2](https://github.com/zsxh1990/pr-genius/compare/v0.5.1...v0.5.2)



## [0.5.1] - 2026-07-02

### Added
- 5 misakanet-style lessons (avg 91/100, all A-grade)
- `misakanet-50/lesson-01` through `lesson-05`

Compare: [0.5.0...0.5.1](https://github.com/zsxh1990/pr-genius/compare/v0.5.0...v0.5.1)



## [0.5.0] - 2026-07-02

### Changed (BREAKING)
- Rounds schema upgrade: `action` enum (9 values) + `delta` object + `close_decision` case-level field
- See [ROUNDS_SCHEMA.md](ROUNDS_SCHEMA.md) v0.2.0 for migration guide

### Added
- `mongodb-js-mongodb-mcp-server/pr-1309-azure-readme-version.md` (1 PR case study)
- Updated `README.md` and `KNOWN_ISSUES.md` for v0.5.0

Compare: [0.4.2...0.5.0](https://github.com/zsxh1990/pr-genius/compare/v0.4.2...v0.5.0)



## [0.4.2] - 2026-07-01

### Added
- Real PR loop #2 on `qdrant/mcp-server-qdrant#143` — stale + close-decision sample

Compare: [0.4.1...0.4.2](https://github.com/zsxh1990/pr-genius/compare/v0.4.1...v0.4.2)



## [0.4.1] - 2026-07-01

### Added
- Real PR decision loop on `plastic-labs/honcho#801` — validates rounds field

Compare: [0.4.0...0.4.1](https://github.com/zsxh1990/pr-genius/compare/v0.4.0...v0.4.1)



## [0.4.0] - 2026-07-01

### Changed
- Review: track 4 known data issues + verification plan

Compare: [0.3.0...0.4.0](https://github.com/zsxh1990/pr-genius/compare/v0.3.0...v0.4.0)



## [0.3.0] - 2026-07-01

### Added
- OKF v0.1 federation declaration (`federates_with` field)
- `misakanet_queries` + `misakanet_lessons` fields in 8 repo profiles

Compare: [0.2.0...0.3.0](https://github.com/zsxh1990/pr-genius/compare/v0.2.0...v0.3.0)



## [0.2.0] - 2026-07-01

### Added
- Agent-first upgrade: agent_guidelines field schema (17 keys)
- Blacklist schema + 6 initially-blacklisted repos

Compare: [0.1.0...0.2.0](https://github.com/zsxh1990/pr-genius/compare/v0.1.0...v0.2.0)



## [0.1.0] - 2026-07-01

### Added
- Initial release
- 8 repo profiles (uv / honcho / harbor / fastmcp / sourcebot / future-agi / qdrant / e2b)
- 4 anti-patterns (e2b / honcho / uv / vite)
- OKF v0.1 compliance

[0.1.0]: https://github.com/zsxh1990/pr-genius/releases/tag/v0.1.0


