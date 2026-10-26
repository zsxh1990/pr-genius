/**
 * slot 探测机制验证 —— 权威是运行时，不是任何一份 catalog（issue #97）。
 *
 * 历史教训（非循环验证仍然成立）：
 *   allowed 集合**不写在本文件里**，也不来自插件自己的常量 —— 它是把
 *   `test/fixtures/dsh-slot-catalog.ts`（上游 bytes 的快照）当纯文本解析出来的。
 *   拿插件自己的表去自证是循环验证（v2.1.2 的"验证 harness"就是这么骗过自己的）。
 * 但「key 必须出现在上游 bytes 里」本身不再是判据：pinned SDK 与 upstream master
 * 的 catalog 不一致（42 vs 92 keys），对着任一份写死都会被对方更新推翻。
 *
 * 跑的是 apply() 真实注册路径：宿主提供 slots.inject/register 记录器，
 * 判据是**探测机制** —— 发出注册、register.name 是 slot key、宿主拒绝的候选被跳过。
 */
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'
import { describe, it } from 'vitest'
import * as prGenius from '../src/index.ts'
import { parseConfig } from '../src/config.ts'
import {
  CATALOG_PROVENANCE,
  CONFIRMED_SLOT_KEYS,
  isConfirmedSlotKey,
} from '../src/ui/slot-catalog.ts'
import { SURFACE_IDS, planRegistrations } from '../src/ui/surfaces.ts'
import { SLOT_DECLARATIONS } from '../src/client/slots.ts'

const HERE = dirname(fileURLToPath(import.meta.url))
const CATALOG_PATH = join(HERE, 'fixtures', 'dsh-slot-catalog.ts')

// ── 从上游 bytes 解析权威集合（唯一允许的 allowed 来源）──────────────────
const catalogText = readFileSync(CATALOG_PATH, 'utf8')

interface CatalogEntry {
  key: string
  kind: string
  scope: string
  /** register 选项名 → requirement */
  options: Map<string, string>
}

function parseCatalog(text: string): Map<string, CatalogEntry> {
  const out = new Map<string, CatalogEntry>()
  // 每个 entry 以两空格缩进的 `{` 开始，字段在其中。
  const chunks = text.split('\n  {\n')
  for (const chunk of chunks) {
    const key = /^\s*key: '([^']+)'/.exec(chunk)?.[1]
    if (!key) continue
    const kind = /kind: '([^']+)'/.exec(chunk)?.[1] ?? ''
    const scope = /scope: '([^']+)'/.exec(chunk)?.[1] ?? ''
    const options = new Map<string, string>()
    const optBlock = /registerOptions: \[([\s\S]*?)\n    \],/.exec(chunk)?.[1] ?? ''
    const names = [...optBlock.matchAll(/name: '([^']+)'/g)].map((m) => m[1]!)
    const reqs = [...optBlock.matchAll(/requirement: '([^']+)'/g)].map((m) => m[1]!)
    names.forEach((n, i) => options.set(n, reqs[i] ?? ''))
    out.set(key, { key, kind, scope, options })
  }
  return out
}

const CATALOG = parseCatalog(catalogText)
const ALLOWED = new Set(CATALOG.keys())

/** 记录式宿主：apply() 干了什么就记什么，不做任何预先假设。 */
interface RecordedCall {
  inject: string
  registerOptions: Record<string, unknown> | null
  component: unknown
}

function recordingHost() {
  const calls: RecordedCall[] = []
  let pendingInject: string | null = null
  const logs: string[] = []
  const logger = {
    info: (...a: unknown[]) => logs.push(a.map(String).join(' ')),
    warn: (...a: unknown[]) => logs.push(a.map(String).join(' ')),
    error: (...a: unknown[]) => logs.push(a.map(String).join(' ')),
    debug: () => {},
    trace: () => {},
  }
  const ctx = {
    logger: () => logger,
    provide: () => () => {},
    effect: () => {},
    slots: {
      inject: (key: string, factory: () => unknown) => {
        pendingInject = key
        calls.push({ inject: key, registerOptions: null, component: undefined })
        try {
          factory()
        } finally {
          pendingInject = null
        }
        return () => {}
      },
      register: (options: Record<string, unknown>, component: unknown) => {
        const hit = calls.find((c) => c.inject === pendingInject && c.registerOptions === null)
        if (hit) {
          hit.registerOptions = options
          hit.component = component
        }
        return () => {}
      },
    },
  }
  return { ctx, calls, logs }
}

describe('slot probing: authority is the runtime, not any one catalog', () => {
  // 前提（option C）：pinned SDK 与 upstream master 的 catalog 不一致（42 vs 92
  // keys），两者都自称权威。对着任一份写死判据，会在对方更新时被推翻——issue #97
  // 就是这么翻的车。所以这里的判据是**探测机制**：发出注册、name 是 slot key、
  // 宿主拒绝的候选会被跳过。不判「key 在不在某份 catalog 里」。
  it('the fixture really is the upstream catalog (shape + provenance)', () => {
    assert.ok(catalogText.includes('CLIENT_SLOT_API'), 'fixture must be the upstream catalog module')
    assert.ok(
      catalogText.includes('@module @deepseek-ai/dsh-cordis-client-runner/client/slot-catalog'),
      'fixture must carry the upstream module marker',
    )
    assert.equal(CATALOG.size, ALLOWED.size)
    assert.equal(CATALOG_PROVENANCE.keyCount, CATALOG.size, 'provenance keyCount must match parsed entries')
    // 上游 catalog 自称 sorted by key
    const keys = [...ALLOWED]
    assert.deepEqual(keys, [...keys].sort(), 'upstream catalog is sorted by key')
  })

  it('candidate lists are non-empty wherever a surface can probe', () => {
    // 不判 key 合法性；判「有得可试」。候选为空等于没得探测。
    for (const surface of planRegistrations()) {
      if (!surface.seat) continue
      const cands = (surface.seat as { candidates?: string[] }).candidates
      if (cands !== undefined) {
        assert.ok(cands.length > 0, `${surface.id}: candidates must be non-empty`)
      }
      assert.ok(surface.seat.key, `${surface.id}: seat must name a key to probe`)
    }
  })

  it('apply() probes: it attempts registrations and uses the slot key as register.name', () => {
    const host = recordingHost()
    prGenius.apply(host.ctx as never, parseConfig({}))
    const attempts = host.calls
    assert.ok(attempts.length > 0, 'apply() must attempt slot registrations')
    for (const call of attempts) {
      assert.ok(call.inject, 'probe must attempt some slot key')
      assert.equal(call.registerOptions?.name, call.inject,
        `register options.name must be the slot key (${call.inject})`)
      for (const field of ['kind', 'scope']) {
        assert.ok(!(call.registerOptions && field in call.registerOptions),
          `${field} is not a register option (it belongs to the children declaration)`)
      }
      assert.ok(call.component !== null, `component for ${call.inject} must not be null`)
    }
  })

  it('every surface either names a probeable seat or is the command surface', () => {
    const withoutSeat: string[] = []
    for (const surface of planRegistrations()) {
      if (!surface.seat) { withoutSeat.push(surface.id); continue }
      assert.ok(surface.seat.key, `${surface.id} must name a slot key to probe`)
    }
    // 命令面走 ctx.command，不是 slot —— 这是设计，不是缺口。
    assert.deepEqual(withoutSeat, [SURFACE_IDS.command])
  })

  it('probe skips a key the host refuses and keeps going (宁缺勿假)', () => {
    const host = recordingHost()
    const registered: string[] = []
    ;(host.ctx as { slots: { inject: unknown } }).slots.inject = (key: string, factory: () => unknown) => {
      if (key === 'nonexistent.slot.from.no.catalog') throw new Error('slot not declared')
      try { factory() } catch { /* host refused the register */ }
      registered.push(key); return () => {}
    }
    prGenius.apply(host.ctx as never, parseConfig({}))
    assert.ok(!registered.includes('nonexistent.slot.from.no.catalog'),
      'a key the host refuses must not be reported as registered')
    assert.ok(registered.length > 0, 'probe must still register what the host accepts')
  })

  it('kind/scope declarations match the catalog (the v2.1.2 single-vs-keyed bug class)', () => {
    // 形状证据保留、成员资格判据去掉（同 option C）：只在 key 恰好出现在**这份**
    // fixture catalog 里时才比 kind/scope —— 那是双方都认识的 key，形状不该有分歧。
    // 单侧认识的 key（如 pinned-only 的右栏落点）跳过，交给运行时探测。
    for (const [key, spec] of Object.entries(SLOT_DECLARATIONS) as [string, { kind: string; scope: string }][]) {
      const entry = CATALOG.get(key)
      if (!entry) continue
      assert.equal(spec.kind, entry.kind, `${key}: declared kind must match catalog`)
      assert.equal(spec.scope, entry.scope, `${key}: declared scope must match catalog`)
      console.log(`  ✓ declaration ${key} = ${spec.kind}/${spec.scope}`)
    }
  })

  it('generated CONFIRMED_SLOT_KEYS is exactly the parsed authority (no hand-typed drift)', () => {
    assert.equal(CONFIRMED_SLOT_KEYS.length, ALLOWED.size)
    for (const key of CONFIRMED_SLOT_KEYS) {
      assert.ok(ALLOWED.has(key), `generated list has key ${key} missing from the authority`)
    }
  })
})

/**
 * 候选顺序守卫（issue #142 / PR #145 的规则，这里写成通用规则而不是绑死面板）。
 *
 * 规则：**凡是带两个以上候选的 surface，只要候选里有任何一个在 catalog 里，
 * 第一个就必须也在 catalog 里。** 违反它的代价是每次启动都白烧一次失败注入
 * （apply() 试到被接受才 break），并让 release-smoke 的 C1 记成
 * `slot-key-not-in-catalog`。
 *
 * 写成通用规则而不是断言面板的 key 叫什么，是因为上游改名时这个失败会自己
 * 点名 surface 和两个 key，而不是指望有人重读一条注释（#142 就是这么翻的车）。
 */
describe('candidate order is self-guarding', () => {
  /** 返回违规说明；合规返回 null。抽出来是为了正反两个方向共用同一段判据。 */
  function orderViolation(id: string, candidates: string[]): string | null {
    if (candidates.length < 2) return null
    const resolving = candidates.filter((k) => isConfirmedSlotKey(k))
    // 一个都不在 catalog 里是合法状态（宁缺勿假：都不认就不注册），
    // 所以只在「至少有一个能落座」时才要求第一个也能落座。
    if (resolving.length === 0) return null
    if (isConfirmedSlotKey(candidates[0])) return null
    return (
      `surface ${id}: first candidate ${JSON.stringify(candidates[0])} is not in ` +
      `the catalog, but ${JSON.stringify(resolving)} are. Probe a known key first — ` +
      `a dead key wastes the first inject on every launch (#142).`
    )
  }

  it('if any candidate resolves, the first candidate resolves too', () => {
    for (const surface of planRegistrations()) {
      const raw = surface.seat as { candidates?: unknown; key?: string } | null
      const candidates: string[] = Array.isArray(raw?.candidates)
        ? (raw!.candidates as string[]).filter((k) => typeof k === 'string' && k.length > 0)
        : [raw?.key ?? ''].filter(Boolean)
      const violation = orderViolation(surface.id, candidates)
      assert.equal(violation, null, violation ?? '')
    }
  })

  it('the guard is not vacuous: a dead key listed first is rejected', () => {
    // 反向对照 —— 只验「规则写对了」不够，还得证明它在坏输入下真的会红，
    // 否则上游改名时这条测试会安静地放过。
    const deadFirst = ['details.gone.forever', 'sidebar.right.pane.tab']
    const violation = orderViolation('pr-genius.fixture', deadFirst)
    assert.ok(violation, 'a dead key first must produce a violation')
    assert.match(violation, /first candidate "details\.gone\.forever" is not in/)
    assert.match(violation, /"sidebar\.right\.pane\.tab"/)
  })

  it('a dead key first is fine when nothing resolves at all (宁缺勿假)', () => {
    // 规则的边界：候选里一个都不在 catalog 时不判违规 —— 那是「都不认就不注册」
    // 的合法状态，不是顺序问题。否则守卫会把保守降级误报成顺序 bug。
    const allDead = ['nope.one', 'nope.two']
    assert.equal(orderViolation('pr-genius.fixture', allDead), null,
      'no candidate resolving is a valid conservative-degrade state, not an order bug')
  })
})
