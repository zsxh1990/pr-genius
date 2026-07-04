---
type: Community Resource
description: Pull request template
---
## What does this PR do?

<!-- Describe the change clearly. What does it add or fix? -->

## Type of Change

<!-- Check the one that applies. -->

- [ ] 🆕 New repo profile (`<org>-<repo>/index.md`)
- [ ] 📝 New PR case study (`pr-<num>-<slug>.md`)
- [ ] 🐛 New anti-pattern (`anti-patterns/<slug>.md`)
- [ ] 📚 New lesson (`misakanet-50/lesson-NN-*.md`)
- [ ] 🔧 Bug fix (broken link / validator error)
- [ ] 📝 Documentation update (README / CONTRIBUTING / CHANGELOG)
- [ ] ♻️ Refactor (reorganize without changing meaning)
- [ ] 🤖 Maintenance (gitignore / workflows / dependabot)

## Source

<!-- If this PR adds content from a real PR, link it here. -->

- Real PR: <!-- `https://github.com/<org>/<repo>/pull/<num>` -->
- Data harvest: <!-- `research/<project>/raw_data/` -->
- Issue: <!-- `Fixes #<num>` -->

## Files changed

<!-- List the files you touched. -->

- [ ] `<file path>`
- [ ] `<file path>`

## AI assistance disclosure

<!-- Be honest. AI-assisted PRs are welcomed, but please disclose. -->

- [ ] This PR is **AI-assisted** (mention tool name: e.g. Claude, GPT-4, etc.)
- [ ] This PR is **human-written**

## Validation

<!-- Run `python3 validate.py` before pushing. Paste output: -->

```bash
python3 validate.py
```

```
<paste output>
```

- [ ] `python3 validate.py` passes (warnings OK)
- [ ] `python3 validate.py --strict` passes (no warnings or errors)

## Checklist

<!-- Complete these before requesting review. -->

- [ ] I've read the [Contributing Guide](../../blob/main/CONTRIBUTING.md)
- [ ] My commit messages follow [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, etc.)
- [ ] I searched for [existing PRs](../../pulls) to make sure this isn't a duplicate
- [ ] My PR contains **only** changes related to this PR (no unrelated edits)
- [ ] I've added tests if applicable (e.g. validator changes need a sample input)
- [ ] I've updated [CHANGELOG.md](../../blob/main/CHANGELOG.md) under `[Unreleased]`

## Screenshots / Logs

<!-- If applicable. -->