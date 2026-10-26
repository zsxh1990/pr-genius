/**
 * 发版 smoke gate 自身的测试（issue #96）。
 *
 * 为什么 gate 也要有测试：gate 是发版前最后一道关，它自己悄悄坏掉比没有 gate
 * 更糟——会把坏的发版放行成绿的。这里锁四件事：
 *   1. catalog 解析器在「marker 里带类型标注」时不被 `[]` 骗走（真的踩过）
 *   2. 反循环自检真能抓到「把 slot 名种进代码」，也不会被注释误报
 *   3. 本仓库 gate 源码里此刻没有任何硬编码 slot 名 —— 防止后来的人又写死一张表
 *   4. 取上游失败可分诊、且交叉校验缺席会写进 VERDICT（issue #149）
 *
 * 刻意不在此处断言任何具体 slot 名的「应该存在」：那正是循环验证。
 * slot 名的事实只来自 DSH SDK，测试只验「取表的管道是通的、来源是外部的」。
 */
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { describe, it } from 'vitest'
import {
  assertNoHardcodedSlotKeys,
  describeGhFailure,
  extractArrayLiteral,
  loadSlotCatalog,
  UPSTREAM,
} from '../scripts/release-smoke/slot-catalog.mjs'

const HERE = dirname(fileURLToPath(import.meta.url))
const REPO_ROOT = join(HERE, '..')

describe('extractArrayLiteral', () => {
  it('slices and evaluates a plain array literal', () => {
    const src = 'const X = [1, 2, 3]\nconst Y = 4'
    assert.deepEqual(extractArrayLiteral(src, 'const X = ['), [1, 2, 3])
  })

  it('is not fooled by `[]` inside the marker type annotation', () => {
    // 真实踩坑：`ClientSlotEntry[]` 里的那对方括号是空数组，
    // 拿 marker 后的第一个 '[' 起算会切出空表，让 gate 误以为 catalog 是空的。
    const src = "export const API: readonly Entry[] = [\n  { key: 'a' },\n  { key: 'b' },\n]\n"
    const out = extractArrayLiteral(src, 'export const API: readonly Entry[] = [')
    assert.equal(out.length, 2)
    assert.deepEqual(out.map((e) => (e as { key: string }).key), ['a', 'b'])
  })

  it('throws on an absent marker', () => {
    assert.throws(() => extractArrayLiteral('const A = []', 'const MISSING = ['), /marker not found/)
  })

  it('throws on unbalanced brackets', () => {
    assert.throws(() => extractArrayLiteral('const A = [1, 2', 'const A = ['), /unbalanced/)
  })
})

describe('loadSlotCatalog — 管道是通的，来源是外部的', () => {
  it('loads the pinned SDK catalog from the installed package', async () => {
    const r = await loadSlotCatalog({ source: 'npm', cwd: REPO_ROOT })
    assert.equal(r.ok, true, `npm catalog should load, got: ${r.error ?? ''}`)
    assert.ok(r.primary, 'primary must be set')
    // 出处必须是「从 SDK 包里取」，不是本仓库写的表 —— 反循环的前提。
    assert.equal(r.primary.provenance.kind, 'installed-sdk-bundle')
    assert.equal(r.primary.provenance.package, UPSTREAM.npmPackage)
    assert.ok(
      typeof r.primary.provenance.packageVersion === 'string' &&
        r.primary.provenance.packageVersion.length > 0,
      'provenance must pin the SDK version — otherwise「验的是哪一版」无从对账',
    )
    // 表必须是张真表，不是解析坏了剩两三条。这个下界不是 slot 名，只是「解析没塌」。
    assert.ok(r.primary.entries.length >= 30, `catalog too small: ${r.primary.entries.length}`)
    for (const e of r.primary.entries) {
      assert.equal(typeof e.key, 'string')
      assert.ok(e.key.length > 0)
      assert.ok(['single', 'list', 'keyed', 'chain'].includes(e.kind), `bad kind on ${e.key}: ${e.kind}`)
      assert.ok(['root', 'session', 'session-maybe'].includes(e.scope), `bad scope on ${e.key}: ${e.scope}`)
      assert.ok(Array.isArray(e.registerOptions))
    }
    // 唯一性：重复 key 意味着解析切错了，会让「在不在表里」的判定失真。
    const keys = r.primary.entries.map((e) => e.key)
    assert.equal(new Set(keys).size, keys.length, 'catalog keys must be unique')
  })

  it('names the upstream source module so a reader can chase it', async () => {
    const r = await loadSlotCatalog({ source: 'npm', cwd: REPO_ROOT })
    assert.ok(r.primary)
    assert.ok(
      (r.primary.provenance.upstreamModule ?? '').includes(UPSTREAM.repo),
      `provenance must point at ${UPSTREAM.repo}, got ${r.primary.provenance.upstreamModule}`,
    )
    assert.ok(
      (r.primary.provenance.upstreamModule ?? '').includes(UPSTREAM.path),
      `provenance must name ${UPSTREAM.path}`,
    )
  })
})

describe('diffCatalogs — 漂移必须两侧都算得出来', () => {
  const mk = (source: string, keys: Array<[string, string, string]>) =>
    ({
      ok: true,
      source: 'npm' as const,
      provenance: { kind: 'installed-sdk-bundle' as const, note: source },
      entries: keys.map(([key, kind, scope]) => ({
        key,
        kind,
        scope,
        registerOptions: [],
        replaceRisk: null,
        declaredBy: null,
        occupants: [],
        source: null,
        summary: null,
      })),
    })

  it('reports keys present on each side and kind/scope changes', async () => {
    const { diffCatalogs } = await import('../scripts/release-smoke/slot-catalog.mjs')
    const a = mk('a', [['shared', 'list', 'root'], ['only-a', 'single', 'session'], ['moved', 'single', 'root']])
    const b = mk('b', [['shared', 'list', 'root'], ['only-b', 'keyed', 'session'], ['only-b2', 'list', 'root'], ['moved', 'single', 'session']])
    const d = diffCatalogs(a, b)
    assert.equal(d.aCount, 3)
    assert.equal(d.bCount, 4)
    // 回归锁：曾经把 onlyInB 写成「在 B 里却不在 B 里」，恒为空——上游多出来的 50+ 个 key
    // 被静默吞掉，漂移报告看起来「没多少变化」。两侧必须都真的算。
    assert.deepEqual(d.onlyInA, ['only-a'])
    assert.deepEqual(d.onlyInB, ['only-b', 'only-b2'])
    assert.deepEqual(d.kindOrScopeChanged, [{ key: 'moved', a: 'single/root', b: 'single/session' }])
  })
})

describe('assertNoHardcodedSlotKeys — 反循环自检', () => {
  const keys = ['sidebar.footer.action', 'conversation.view', 'details']

  it('flags a slot key planted in code', () => {
    const src = "const ALLOW = new Set(['sidebar.footer.action'])\n"
    const r = assertNoHardcodedSlotKeys([{ file: 'x.mjs', source: src }], keys)
    assert.equal(r.ok, false)
    assert.equal(r.offenders.length, 1)
    assert.equal(r.offenders[0].key, 'sidebar.footer.action')
    assert.equal(r.offenders[0].line, 1)
  })

  it('does not flag a slot key that only appears in a comment', () => {
    const src = "/** 例如 'sidebar.footer.action'。 */\nconst X = 1\n"
    const r = assertNoHardcodedSlotKeys([{ file: 'x.mjs', source: src }], keys)
    assert.equal(r.ok, true, JSON.stringify(r.offenders))
  })

  it('does not flag ordinary non-slot strings', () => {
    const src = "const A = 'npm'\nconst B = 'auto'\nconst C = 'lib/client.js'\n"
    const r = assertNoHardcodedSlotKeys([{ file: 'x.mjs', source: src }], keys)
    assert.equal(r.ok, true)
  })
})

describe('本仓库 gate 源码当前不得含硬编码 slot 名', () => {
  it('scan of the shipped gate sources is clean against the live SDK catalog', async () => {
    const r = await loadSlotCatalog({ source: 'npm', cwd: REPO_ROOT })
    assert.ok(r.ok && r.primary, 'need a live catalog to run the anti-circular scan')
    const files = ['scripts/release-smoke/slot-catalog.mjs', 'scripts/release-smoke/runtime-smoke-gate.mjs']
    const scan = assertNoHardcodedSlotKeys(
      files.map((f) => ({ file: f, source: readFileSync(join(REPO_ROOT, f), 'utf8') })),
      r.primary.entries.map((e) => e.key),
    )
    assert.deepEqual(
      scan.offenders,
      [],
      `gate 源码里出现了权威 catalog 的 slot 名字面量 —— 那就是循环验证：` +
        `自己出题自己批卷，只能确认错误，无法证伪。命中：${JSON.stringify(scan.offenders)}`,
    )
    assert.equal(scan.ok, true)
  })

  it('the gate never treats a non-SDK provenance as authoritative', () => {
    const src = readFileSync(join(REPO_ROOT, 'scripts/release-smoke/runtime-smoke-gate.mjs'), 'utf8')
    assert.ok(
      src.includes('ALLOWED_PROVENANCE'),
      'gate 必须校验 catalog 出处是 SDK 侧，否则本地写一张表也能冒充权威',
    )
    assert.ok(
      src.includes('installed-sdk-bundle'),
      'gate 必须接受「已安装 SDK 包」这种出处',
    )
    assert.ok(
      !/ALLOWED_PROVENANCE\s*=\s*new Set\(\[\s*['"]inline['"]/.test(src),
      "gate 不得把 'inline' 当作合法 catalog 出处",
    )
  })
})

/**
 * 取上游失败时的 reason 形状（issue #149）。
 *
 * 为什么这也是判据：CI 里 `gh api` 交叉校验**从未成功过**，而 reason 只有一句
 * `Command failed: gh api …`（就是 execFileSync 的 err.message）。既看不出是
 * 限流还是仓库名打错，也看不出是没认证——于是「交叉校验缺席」被折叠成一次普通
 * 失败，SDK 漂移在 CI 里完全不可见。
 *
 * 判据是**可分诊**：退出码、信号、stderr 首行（gh 的 HTTP 码在那）都要在场，
 * 且 spawn 不起来（gh 不在 PATH）要和「gh 跑了但报错」分得开。
 */
describe('describeGhFailure — 失败必须可分诊', () => {
  const ctx = { repo: 'deepseek-ai/deepseek-harness', ref: 'master', path: 'x/y.ts' }

  it('carries the exit status, the stderr line, and the HTTP code gh prints', () => {
    // 真实形状：execFileSync 失败时 err.message 只有 "Command failed: …"，
    // HTTP 码在 stderr 里（gh: Not Found (HTTP 404)）。
    const err = Object.assign(new Error('Command failed: gh api repos/… --jq .content'), {
      status: 1,
      stdout: '',
      stderr: 'gh: Not Found (HTTP 404)\n',
    })
    const reason = describeGhFailure(err, ctx)
    assert.match(reason, /exit=1/, '退出码必须在 reason 里')
    assert.match(reason, /404/, 'gh 在 stderr 打的 HTTP 码必须被带出来')
    assert.match(reason, /Not Found/, 'stderr 首行要进 reason')
  })

  it('does not stop at err.message — Command failed alone is not a diagnosis', () => {
    const err = Object.assign(new Error('Command failed: gh api …'), {
      status: 1,
      stderr: 'gh: API rate limit exceeded for 1.2.3.4. (HTTP 403)\n',
    })
    const reason = describeGhFailure(err, ctx)
    // 关键回归锁：曾经整条 reason 只有 err.message，于是限流和 404 长得一模一样。
    assert.match(reason, /403/, '限流的 403 必须能和 404 区分开')
    assert.ok(reason.length > 'Command failed: gh api …'.length, '不能只回声 err.message')
  })

  it('distinguishes "gh is not installed" from "gh ran and failed"', () => {
    // spawn 都没起来（ENOENT）与 gh 跑完退出码非 0 是两回事：
    // 前者是环境问题（exit 3 那一类），后者是取不到。
    const err = Object.assign(new Error("spawnSync gh ENOENT"), {
      code: 'ENOENT',
      errno: -2,
      syscall: 'spawnSync gh',
      path: 'gh',
    })
    const reason = describeGhFailure(err, ctx)
    assert.match(reason, /ENOENT|not found|不存在/i, 'gh 不在 PATH 要和「gh 报错」分得开')
    assert.ok(!/HTTP \d+/.test(reason), '没跑起来就没有 HTTP 码，不要编一个')
  })

  it('reports a real execFileSync timeout as a timeout, not as "gh 不可执行"', async () => {
    // **用真实超时，不用手搓错误对象。** 上一版这里 mock 了
    // `{killed: true, signal: 'SIGTERM', status: null}` —— 而 Node 的
    // execFileSync 超时错误**没有 `killed` 属性**（实测：`killed: undefined`，
    // `'killed' in err` 为 false），形状是
    // `{code:'ETIMEDOUT', syscall:'spawnSync …', status:null, signal:'SIGTERM'}`。
    // mock 形状从未被真代码路径产生过，所以绿灯锁的是 mock、不是行为 ——
    // 真实超时当时会被误报成「gh 不可执行（ETIMEDOUT）」。
    // 真跑一次超时，形状就不会再漂。
    const { execFileSync } = await import('node:child_process')
    let realErr: unknown
    try {
      execFileSync('sleep', ['5'], {
        encoding: 'utf8',
        stdio: ['ignore', 'pipe', 'pipe'],
        timeout: 250,
      })
      assert.fail('expected the sleep to time out')
    } catch (err) {
      realErr = err
    }
    // 先钉住形状本身：这条断言让「超时错误长什么样」成为显式判据，
    // 而不是靠下一个读测试的人猜。
    const e = realErr as { code?: unknown; killed?: unknown; status?: unknown; signal?: unknown }
    assert.equal(e.code, 'ETIMEDOUT', 'real execFileSync timeouts carry code=ETIMEDOUT')
    assert.equal(e.status, null, '… and no exit status')
    assert.equal(e.killed, undefined, '… and NO `killed` property — do not rely on it')

    const reason = describeGhFailure(realErr, ctx)
    assert.match(reason, /超时|ETIMEDOUT|SIGTERM|timeout/i, '超时要能和「取不到」分开')
    assert.doesNotMatch(reason, /gh 不可执行/, '真实超时不得被误报成「gh 没起来」')
    assert.doesNotMatch(reason, /HTTP \d+/, '超时没有 HTTP 码，不要编一个')
  })

  it('names the target so the reason is actionable without the logs', () => {
    const err = Object.assign(new Error('Command failed'), { status: 1, stderr: 'gh: Bad credentials (HTTP 401)\n' })
    const reason = describeGhFailure(err, ctx)
    assert.match(reason, /deepseek-ai\/deepseek-harness/, '要指名是哪个仓')
    assert.match(reason, /x\/y\.ts/, '要指名是哪个文件')
    assert.match(reason, /401/, '未认证（401）要显式可见 —— 这正是 CI 里一直发生的情况')
  })
})

/**
 * 交叉校验缺席必须在 VERDICT 里说出来（issue #149 第三条建议）。
 *
 * 这条用**真跑 gate + 解析 JSON 报告**，不看源码字符串。原因就是本次翻的车：
 * 手搓的错误对象形状和 Node 真实形状不一致，绿灯锁的是 mock 不是行为。
 * gate 跑一次约 2s（`--catalog npm` 会跳过上游取数，不需要网络）。
 */
describe('gate 把「交叉校验缺席」写进 VERDICT', () => {
  it('reports PASS_WITH_WARNINGS and names the absent cross-check, not a silent PASS', async () => {
    const { execFileSync } = await import('node:child_process')
    const { mkdtempSync, readFileSync, rmSync } = await import('node:fs')
    const { tmpdir } = await import('node:os')
    const dir = mkdtempSync(join(tmpdir(), 'pg-xcheck-'))
    const out = join(dir, 'report.json')
    try {
      // --catalog npm：强制只用主源，交叉校验必然缺席。这不是伪造失败，
      // 是把「只有一条来源」这个真实状态摆出来。
      execFileSync('node', [
        join(REPO_ROOT, 'scripts/release-smoke/runtime-smoke-gate.mjs'),
        '--catalog', 'npm',
        '--json', out,
      ], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'], timeout: 120_000, cwd: REPO_ROOT })

      const report = JSON.parse(readFileSync(out, 'utf8'))
      assert.equal(report.verdict, 'PASS_WITH_WARNINGS',
        '主源成功但交叉校验缺席，不能是安静的 PASS —— 那正是 #149 让漂移不可见的原因')

      const finding = (report.findings ?? []).find((f: { id?: string }) => f.id === 'C0.catalog-crosscheck-absent')
      assert.ok(finding, '必须有 C0.catalog-crosscheck-absent 这条 finding')
      assert.equal(finding.severity, 'WARN',
        '缺席是 WARN 不是 FAIL —— 钉住版本来就是用户装到的那份，以它为准不为错')

      assert.equal(report.catalogCrossCheck?.attempted, false,
        '要分清「没尝试」和「试了没取到」—— --catalog npm 是我们自己关的')
    } finally {
      rmSync(dir, { recursive: true, force: true })
    }
  }, 130_000)
})
