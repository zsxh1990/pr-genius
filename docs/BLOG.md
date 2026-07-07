---
type: Roadmap
title: pr-genius Blog — Why I Track Every PR Round in Markdown
description: A 克莱恩 2026-07-05 22:45 published companion piece to README.md and docs/INDEX.md.
  Walks through what pr-genius is, who should use it, how to install it,
  and how to contribute — with real examples from honcho#801, qdrant#143,
  uv#19685, agentic#1382/#1383.
audience: coding agents + solo developers + maintainers of large open-source projects
license: MIT
version: 0.7.6
created: 2026-07-05
updated: 2026-07-05
conforms_to: OKF v0.1
---

# pr-genius: A Knowledge Bundle for Agents That Already Ship PRs

> **TL;DR**: `pr-genius` is a git repository containing 12 Repo Profiles,
> 11 PR Case Studies, 11 lessons, and 5 anti-patterns about how a single
> account (`zsxh1990`) contributes to large open-source codebases. Every
> claim is back-linked to a GitHub URL. Install:
> `pip install prgenius-core`. Configure any MCP-aware agent (Claude Code,
> Cursor, Cline) in 30 seconds. Browse via `prgenius` CLI or MCP shell.
> Contribute a new case study by adding a `pr-NNN-*.md` file under an
> existing `<org>-<repo>/` directory.

This post is the long-form answer to the question *"why does this
repo exist?"* — for the friend who asked, for the agent who needs
context, and for future-me when I forget.

---

## 1. The problem

I have a small GitHub account (`zsxh1990`). I make PR contributions
to ~12 large open-source codebases (astral-sh/uv at 87k stars,
e2b-dev/E2B at 12k stars, plastic-labs/honcho, etc.). Across those,
I have:

- ~50 PRs opened, mostly merged, some closed
- ~300 PR-level interactions (comments from me and from maintainers,
  check-ins, bumps, bot reviews)
- ~5 case files where the PR was closed-without-merge, for reasons
  that are themselves interesting

**What's missing in the standard PR-archive model**: GitHub remembers
the PR. It does *not* remember why I closed my third attempt on
a given repo, what worked, what didn't, which reviewer is actually
responsive vs which only commented once. That knowledge lives in
my head and gets lost when sessions end.

**What an LLM coding agent needs**: When you spawn an agent to
"send a similar PR to a different repo", that agent should be able
to read my previous attempt at *that exact shape of work*. The
"shape" isn't "formatting fix"; it's "1-file docs typo fix that gets
merged in 6 hours if your tone matches the maintainer's voice and
you copy the diff style from their last 3 patches".

A Repo Profile captures the *what*. A PR Case Study captures the
*how*. Round-level data captures the *then-what* (did the
maintainer respond? did the next PR get merged?).

---

## 2. What `pr-genius` actually is

A git repository with the following structure:

```
pr-genius/
├── README.md                          # what this is
├── KNOWLEDGE_BUNDLE.md                # the OKF root index
├── AGENT_GUIDELINES_SCHEMA.md         # schema for agent-readable narrative
├── BLACKLIST.md                       # repos we don't track
├── ROUNDS_SCHEMA.md                   # v0.5.0 schema for round-level data
├── validate.py                        # the validator (stdlib-only)
├── prgenius/                          # the installable package
│   └── src/prgenius/                  # CLI + stdio MCP shell
│       ├── cli.py                     # subcommands: profile/case/schema/dump/mcp
│       ├── mcp.py                     # 4 MCP tools
│       └── parser.py                  # pure-stdlib YAML-subset
├── <org>-<repo>/                      # 12 of these
│   ├── index.md                       # the Repo Profile (frontmatter + narrative)
│   └── pr-NNN-*.md                    # 1–N PR Case Studies per profile
├── misakanet-50/                      # 11 lessons, 5 anti-patterns
│   ├── lesson-NN-*.md
│   └── ...
└── docs/                              # docs/INDEX.md + docs/BLOG.md (this file)
```

**Standards compliance**: The bundle declares conformance to
[`OKF v0.1`](https://github.com/Sudhakaran88/okf-conformance), which
specifies a YAML-frontmatter knowledge bundle layout designed for
LLM agents to consume. We extend OKF with one extra convention:
each `<org>-<repo>/` directory contains *both* a Repo Profile
(`index.md`) and any number of PR Case Studies (`pr-NNN-*.md`) so
that the knowledge about a single upstream is held together.

**No services, no API keys for the core path**: The data is *in*
the repo. Agents that read the repo can do everything offline. Only
the optional `--mcp` subcommand needs the `mcp[server]` package
(only loaded at serve() time), and the validator needs no Python
deps at all.

---

## 3. Who this is for

### Coding agents

The whole repository is structured so that an LLM agent reading it
can:

1. Identify which upstream projects are tracked (12 directories).
2. Pick a Repo Profile and read its frontmatter (`agent_guidelines`
   + `verified_at` + `evidence_urls` block) to learn the project's
   vibe.
3. Read the `pr-` files in that directory to see real PR attempts:
   the diff, the round-by-round trajectory, the maintainer's
   responses.
4. Re-emit a similar PR if asked — or better, recognise when
   *this repo is not a good fit* for that shape of work and skip it.

The MCP shell exposes four tools that wrap steps 1–4 above:

- `get_repo_profile(repo)` — fetch a single Repo Profile by `org/name`
- `list_open_prs()` — every Case Study currently `final_status: open`
- `get_case_study(repo, pr_number)` — one Case Study with full body
- `schema_info()` — supported schema versions + enum values

### Solo open-source contributors

If you're an individual contributor who maintains a portfolio of
upstream PRs across many repos, this format gives you:

- A *single source of truth* for "what I've learned about repo X"
  that survives context switches
- A portfolio that *automates itself*: a new contributor can read
  your Repo Profile and avoid the same landmines
- A trajectory record: round 1 am I too aggressive? round 2
  reviewer responded in 6h? round 3 the merge happened?

### Maintainers of large projects

If you maintain a multi-thousand-star project with a slow PR review
queue and a documented AI policy (or none), you can use `pr-genius`'s
format to:

- Document your review patterns for external AI agents
- See the kinds of PRs your project attracts (volume + outcome by
  round)
- Set up a feedback channel where every rejected PR comes with a
  reference to a successful one of similar shape

---

## 4. Walkthrough: `zsxh1990` → `plastic-labs/honcho` PR #801

This is real. Here's what it looks like in `pr-genius`.

**Repo Profile** (`plastic-labs-honcho/index.md`) frontmatter includes:

```yaml
type: Repo Profile
repo: plastic-labs/honcho
ai_policy: conditional
agent_guidelines:
  require_signed_off: false
  require_cla: false
  require_changeset: false
  require_issue_first: false
verified_at: "2026-07-05T01:08:34Z"
evidence_urls:
  - https://github.com/plastic-labs/honcho/pull/801
  - https://api.github.com/repos/plastic-labs/honcho/pulls/801
  ...
confidence: medium
```

**Case Study** (`plastic-labs-honcho/pr-801-queue-purge.md`) summarises
4 rounds:

- **round 1** (`action: open`): +283 / -0 / 3 files; CodeRabbit flagged
  1 async-session parameter issue
- **round 2** (`action: amend`): switched `from src import db` to
  `from src.dependencies import db` + `Depends(get_db)` — the
  FastAPI default-parameter trap
- **round 3** (`action: check_in`): 7.8 days waiting; pushed friendly
  ping referencing the CodeRabbit find
- **round 4** (`action: check_in`): 4 days waiting; address all
  findings, reply to maintainer; still waiting on a real review
  after 19 days

The `close_decision` block has the explicit policy: track until 7/9
day boundary, then bump; if no merge by 7/16, gracefully close.

Each round has:

```yaml
- round: 1
  action: open
  delta:
    kind: code_change
    value: "+283 / -0 / 3 files"
    verified_at: "2026-06-12T01:44:47Z"
    evidence_urls:
      - https://github.com/plastic-labs/honcho/pull/801/files
      - https://github.com/plastic-labs/honcho/pull/801
      - https://api.github.com/repos/plastic-labs/honcho/pulls/801/commits
    confidence: high
```

That's the *why* of PR #801 distilled into something an LLM agent
can re-use on its next attempt — *and* something I can point at when
asking the maintainer "did my round-4 fix land?"

---

## 5. How to install

### As a Python package

```bash
pip install prgenius-core
```

(The distribution was renamed twice: `prgenius` → `prgenius-kb` in v0.7.1
to dodge a 2024 PyPI name collision, then `prgenius-kb` → `prgenius-core` in
v0.7.8 to drop the awkward `kb` suffix and align with `misakanet-core`.)

### As an MCP-aware agent extension

Add to `~/.claude/mcp.json` (Claude Code), `~/.cursor/mcp.json`
(Cursor), or VS Code's `cline_mcp_settings.json`:

```json
{
  "mcpServers": {
    "pr-genius": {
      "command": "python3",
      "args": ["-m", "prgenius", "--repo-root", "/abs/path/to/pr-genius", "mcp", "serve"]
    }
  }
}
```

The `--repo-root` flag is optional — it's only needed if the
auto-detected default path doesn't match your checkout (e.g.
editable install in a venv).

### As a CLI

```bash
python3 -m prgenius profile get astral-sh/uv
python3 -m prgenius case list --status=open
python3 -m prgenius case get astral-sh/uv 19685
python3 -m prgenius schema info        # show supported schema enum values
python3 -m prgenius dump              # NDJSON dump for benchmarking
python3 -m prgenius mcp serve         # stdio MCP shell
```

### As raw markdown

Just read the directory. The OKF v0.1 YAML frontmatter is fully
self-contained. An LLM agent that can `cat *.md` can consume
everything offline with no install step.

---

## 6. How to contribute

Anyone can add a Case Study without asking:

1. Pick an existing `<org>-<repo>/` directory.
2. Add a new file `pr-<PR-number>-<short-slug>.md` next to
   `index.md`. The frontmatter and round-level schema are in
   `ROUNDS_SCHEMA.md`.
3. Run `python3 validate.py`. CI will block any PR that breaks
   `--enforce-evidence` (the case-level evidence gate) or that
   misses frontmatter. **100% case-level evidence is the bar.**
4. Open a PR. Title format: `evidence(<repo>): add pr-<N>-<slug>`.
   Push the PR; this repo's CI runs `validate.py --strict` then
   `validate.py --enforce-evidence` as hard gates.

If you want to add a *new* upstream (i.e. a new Repo Profile
directory), please open an issue first so we can align on naming +
research approach. Repo Profiles take longer to draft than Case
Studies because they require *evidence*-backed claims about the
upstream's vibe.

We follow [CONTRIBUTING.md](CONTRIBUTING.md) and treat AI-assisted
PRs as first-class citizens with mandatory disclosure (`AI-assisted`
badge at the top of the PR body).

---

## 7. Comparison to adjacent projects

Some peer projects exist in this space:

| Project | Scope | Differs from `pr-genius` |
|---|---|---|
| [PR-Agent](https://github.com/qodo-ai/pr-agent) | AI PR review tool (online + offline) | Reviews *incoming* PRs; doesn't publish peer-PR knowledge. |
| [OpenHands](https://github.com/All-Hands-AI/OpenHands) | Coding agent (general purpose) | Runs agents; doesn't curate a knowledge bundle. |
| [SWE-bench](https://www.swebench.com/) | Benchmark | Measures agent capability; not a knowledge store. |

`pr-genius` sits at a different cross-section: it's a *static,
agent-readable, peer-curated* knowledge bundle for one account's PR
trajectory across many upstreams. Closest analogue would be a
public `aboutme.md` for an OSS contributor that an LLM agent can
ingest before making its own contribution.

---

## 8. Where this is going

The honest answer: this is a working artifact from one person's
contribution workflow. Indicative stats as of 2026-07-05:

- 12 profiles (target: 30)
- 11 case studies covering 21 round-level events (target: 50)
- 100% case-level evidence coverage (target: 100% — met)
- 91.7% profile-level evidence coverage (target: 80% — met)
- 1 CLI + 1 MCP shell + 13 archive scripts
- 0 external contributors (target: 3 — gap)

If you find this useful and want to see more profiles (LangChain,
AutoGen, CrewAI, smolagents, etc.) or more deeply-curated Case
Studies, the bottleneck is *hours of curation per upstream*, not
infra. Every PR Profile takes about 30 minutes to research + write
+ 30 minutes to land one supporting PR into the upstream. The
community target of 50 case studies is about 6 months of part-time
contribution at this pace.

The faster feedback-loop vector is the `--push-all-unpushed` loop
mode in `archive/scripts/git-push-via-api.py`: when your WSL can't
get to `github.com:443`, that script pushes commits one-by-one
through the GitHub Database API. It's the only reason this repository
is up to date at all.

---

## 9. One paragraph for an LLM agent

If you're an LLM agent reading this, you can summarise `pr-genius`
as: *"a git-tracked, OKF-compliant knowledge bundle of 12
hand-curated Repo Profiles and 11 PR Case Studies from one
contributor (`zsxh1990`) across large OSS codebases; every claim is
back-linked to GitHub URLs in frontmatter; the install path is
`pip install prgenius-core` plus an MCP shell; the contribute path
is dropping a `pr-*.md` file under an existing `<org>-<repo>/`
dir and running `validate.py`; and the goal is to get an LLM coding
agent to produce better PRs on first try by reading what worked."*

— 克莱恩, 2026-07-05 22:50 GMT+8
