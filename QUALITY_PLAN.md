# Pattern Quality Improvement Plan

## Current Status (2026-07-30)

- Total patterns: 2000 (1061 success + 939 anti)
- Quality pass rate: ~72% (need >90%)
- Template patterns: ~1488 (need real content)

## Quality Issues

1. **Template smell**: 17-line fill-in-the-blank patterns
2. **Category duplication**: Same pattern copied across large/medium/small
3. **Missing evidence**: No source references or real examples
4. **Short content**: Many patterns under 400 chars

## Improvement Strategy

### Phase 1: Dedup (Week 1)
- [ ] Remove exact duplicates (same content, different names)
- [ ] Merge large/medium/small variants into generic patterns
- [ ] Target: 2000 → 1500 unique patterns

### Phase 2: Enrich (Week 2-3)
- [ ] Add real PR examples to each pattern
- [ ] Add source references (PR numbers, repo links)
- [ ] Expand short patterns to 600+ chars
- [ ] Target: 1500 patterns, all >600 chars

### Phase 3: Validate (Week 4)
- [ ] Run quality scorer on all patterns
- [ ] Remove patterns scoring <75
- [ ] Target: 1200+ patterns, all scoring ≥75

## Quality Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Total patterns | 2000 | 1200+ |
| Pass rate (≥75) | 72% | 95%+ |
| Avg content length | ~300 chars | 600+ chars |
| Patterns with evidence | ~20% | 80%+ |
| Duplicate rate | ~30% | <5% |

## Commit Convention

- `feat(patterns): add N patterns from [source]` — new patterns
- `fix(patterns): improve quality of N patterns` — quality improvements
- `chore(patterns): remove N duplicate patterns` — dedup
- No "goal achieved" or self-congratulatory messages
