/**
 * slot 契约测试 —— 判据是「可探测的注册契约形状」，不是「key 在某份 catalog 里」。
 *
 * 权威是运行时探测（option C）。两份 catalog 不一致且都自称权威：
 *   - pinned SDK 0.0.1-rc.3（用户装到的那份）：42 keys，右栏落点是 `details`；
 *   - upstream deepseek-harness@master：92 keys，右栏落点是 `sidebar.right.pane.tab`。
 * 对着任一份写死 key 级判据，会在对方更新时被推翻 —— issue #97 就是这么翻的车。
 * docs/slot-catalog-evidence.json 是 upstream 那一份的实抓快照（2026-10-03），
 * 这里只拿它做**形状**对照，不做成员资格判定。
 *
 * 这些断言不证明宿主会渲染我们的组件（需 DSH 运行时），只证明：
 *   1. 契约表自身自洽（kind/scope/entryShape 互相咬合）；
 *   2. 每个非命令面都有可探测的 seat（有 key、候选非空）；
 *   3. register() 参数形状与 catalog example 一致（list→id，keyed→key）；
 *   4. 无契约的 key 会被保守拒绝（不猜测注册）。
 */
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { describe, it } from 'vitest'
import {
  ADVISOR_PANEL_SLOT,
  PANEL_SLOT_CANDIDATES,
  SLOT_DECLARATIONS,
  VERIFIED_SLOT_CONTRACTS,
  slotRegisterDef,
} from '../src/client/slots.ts'
import { SURFACE_IDS, planRegistrations } from '../src/ui/surfaces.ts'

interface CatalogEntry {
  key: string
  kind: string
  scope: string
  replaceRisk: string
  declaredBy: string
  summary: string
}

interface CatalogSnapshot {
  provenance: Record<string, string>
  entries: CatalogEntry[]
}

const snapshot = JSON.parse(
  readFileSync(
    fileURLToPath(new URL('../docs/slot-catalog-evidence.json', import.meta.url)),
    'utf8',
  ),
) as CatalogSnapshot

const byKey = new Map(snapshot.entries.map((e) => [e.key, e]))

describe('slot catalog evidence', () => {
  it('snapshot carries its provenance and a non-trivial key set', () => {
    assert.equal(snapshot.provenance.source, 'deepseek-ai/deepseek-harness')
    assert.ok(snapshot.entries.length >= 50, `catalog snapshot too small: ${snapshot.entries.length}`)
    // 下面只陈述**这份 upstream 快照**里有什么，不做「哪个 key 合法」的判断。
    // 权威是运行时（option C）；两份 catalog 不一致，任何 key 级主张都会被推翻。
    // 记下分歧，供漂移对照：
    const upstreamHas = (k: string) => byKey.has(k)
    console.log('  upstream snapshot: details=%s sidebar.right.pane.tab=%s (pinned SDK 与之相反)',
      upstreamHas('details'), upstreamHas('sidebar.right.pane.tab'))
    // 形状确实可核的：kind/scope 是契约的一部分，与 catalog 版本无关。
    assert.equal(byKey.get('conversation.view')?.kind, 'list')
    assert.equal(byKey.get('sidebar.footer.action')?.kind, 'list')
  })
})

describe('registered slots follow the runtime probe contract', () => {
  // 前提同 option C：不判「key 在不在某份 catalog」——pinned 42 keys 与 upstream
  // 92 keys 不一致，任一判定都会被对方更新推翻（#97）。判的是**注册契约形状**。
  it('every contract is self-consistent (kind/scope/entryShape agree)', () => {
    // 不查 catalog —— 权威是运行时。查的是契约自身是否自洽。
    for (const [slot, contract] of Object.entries(VERIFIED_SLOT_CONTRACTS)) {
      assert.ok(contract.kind, `${slot}: kind required`)
      assert.ok(contract.scope, `${slot}: scope required`)
      assert.equal(
        contract.entryShape,
        contract.kind === 'keyed' ? 'key' : contract.kind === 'single' ? 'none' : 'id',
        `${slot}: entry shape must follow kind (keyed→key, single→none, list/chain→id)`,
      )
    }
  })

  it('every non-command surface names a probeable seat', () => {
    // 「已验证 / 在某份 catalog 里」不再是判据（权威是运行时）。判的是**可探测**：
    // 有 key 可试；声明了候选的，候选非空且 seat.key 自己就是候选之一。
    // 对照面是 advisorPanel：它的 key 是 `details`，upstream 快照里没有、pinned SDK
    // 里有 —— 成员资格断言会在这里翻车，可探测断言不会。
    for (const surface of planRegistrations()) {
      if (surface.kind === 'command') {
        // ctx.command 是 cordis 命令面，不是 slot key —— seat 为 null 是设计，不是缺口。
        assert.equal(surface.seat, null, 'command surface must not invent a slot seat')
        continue
      }
      const seat = surface.seat as { key?: string; candidates?: string[] } | null
      assert.ok(seat, `surface ${surface.id} must have a seat to probe`)
      assert.ok(seat!.key, `surface ${surface.id} must name a slot key to probe`)
      if (seat!.candidates !== undefined) {
        assert.ok(
          Array.isArray(seat!.candidates) && seat!.candidates.length > 0,
          `surface ${surface.id}: declared candidates must be non-empty`,
        )
        assert.ok(
          seat!.candidates.includes(seat!.key),
          `surface ${surface.id}: seat.key must itself be one of the probe candidates`,
        )
      }
    }
  })

  it('SLOT_DECLARATIONS kind/scope agree with the frozen snapshot where both know the key', () => {
    // 形状证据仍成立，成员资格判据被新前提否定（见文件头 option C）：
    // - 删掉的是「key 必须在 catalog 里」——pinned 有 details / 无 sidebar.right.pane.tab，
    //   upstream 相反，任何单侧成员资格断言都会被另一侧推翻。
    // - 保留的是「若 key 恰好在**这份**快照里，则 kind/scope 必须一致」：它抓的是
    //   v2.1.2 那类 single-vs-keyed 转写错误，与「谁是权威」无关 —— 两边都认识的
    //   key，形状不该有分歧。单侧认识的 key 跳过，交给运行时探测。
    for (const [slot, def] of Object.entries(SLOT_DECLARATIONS) as [string, { kind: string; scope: string }][]) {
      const entry = byKey.get(slot)
      if (!entry) continue
      assert.equal(def.kind, entry.kind, `declaration kind mismatch for ${slot}`)
      assert.equal(def.scope, entry.scope, `declaration scope mismatch for ${slot}`)
    }
  })

  it('register() defs follow the catalog example shape (list→id, keyed→key)', () => {
    const footer = slotRegisterDef('sidebar.footer.action', SURFACE_IDS.dashboard, 'PR Genius')
    assert.deepEqual(footer, {
      name: 'sidebar.footer.action',
      id: SURFACE_IDS.dashboard,
      label: 'PR Genius',
    })
    const tab = slotRegisterDef('conversation.view', SURFACE_IDS.advisorTab, 'Advisor')
    assert.deepEqual(tab, { name: 'conversation.view', id: SURFACE_IDS.advisorTab, label: 'Advisor' })
    const panel = slotRegisterDef('details', SURFACE_IDS.advisorPanel)
    // single 基数只收 name —— 多传 id 会被 SDK 忽略或报错（gate 的 C4）。
    assert.deepEqual(panel, { name: 'details' })
    // preferences 实际落座的是 settings.section（SURFACE_PLAN 的 seat），
    // 不是 settings.plugins.tab —— 后者已从契约表删掉（不是候选、apply() 不探测）。
    const prefs = slotRegisterDef('settings.section', SURFACE_IDS.preferences, 'pr-genius')
    assert.deepEqual(prefs, {
      name: 'settings.section',
      id: SURFACE_IDS.preferences,
      label: 'pr-genius',
    })
    assert.equal(slotRegisterDef('settings.plugins.tab', SURFACE_IDS.preferences, 'pr-genius'), null,
      'settings.plugins.tab is not a probe candidate — must be refused, not guessed')
  })

  it('conservative degrade: an unverified slot key is refused (no guessed registration)', () => {
    // 两个候选都合法（探测接受任一）；真正不存在的 key 才返回 null。
    assert.notEqual(slotRegisterDef('details', 'pr-genius.x'), null, 'details is a probe candidate')
    assert.notEqual(slotRegisterDef('sidebar.right.pane.tab', 'pr-genius.x'), null, 'pane is a probe candidate')
    assert.equal(slotRegisterDef('nonexistent.slot.from.no.catalog', 'pr-genius.x'), null,
      'a key with no contract must be refused, not guessed')
  })
})

/**
 * SDK 0.2.1 的右栏落点契约（issue #150 / #145）。
 *
 * 实测（独立探针解 `lib/client.js` 的 CLIENT_SLOT_API，括号匹配数顶层元素，
 * 非 pr-genius 自己的脚本；对 `key:` 扫正则会把嵌套对象的 key 字段也算进去、每个版本多算 3 个）：
 *   pinned  0.0.1-rc.3   42 keys  — 有 `details`，无 `sidebar.right.pane.tab`
 *   next    0.2.1-rc.3  103 keys  — 无 `details`，有 `sidebar.right.pane.tab` / `.title`
 * 42 与 release-smoke gate 及 README/CHANGELOG 既有数字一致；103 与 gate 的
 * `catalog keys=103` 一致。4 个 key 被删：`conversation`, `conversation.details.tool`,
 * `details`, `settings.plugin.item`；65 个新增。
 *
 * 判据是**默认落点必须是升级后 SDK 仍声明的 key**，并且探测顺序先试活的、
 * 再试 legacy 兜底 —— 不是「删掉 details」。宿主版本不可控，兜底探测是设计意图
 * （见 VERIFIED_SLOT_CONTRACTS 的注释：候选提示，不是权威白名单）。
 */
describe('panel seat under the 0.2.1 SDK surface', () => {
  it('the default panel key is the one the 0.2.1 SDK still declares', () => {
    assert.equal(ADVISOR_PANEL_SLOT, 'sidebar.right.pane.tab',
      'the default must be a key the pinned-after-bump SDK declares — `details` was removed in 0.2.1')
  })

  it('probe order tries the live key before the legacy fallback', () => {
    assert.deepEqual(PANEL_SLOT_CANDIDATES, ['sidebar.right.pane.tab', 'details'],
      'dead key first burns a failed inject on every launch (issue #142)')
  })

  it('the panel seat registers with the keyed shape, not the removed single shape', () => {
    const panel = planRegistrations().find((s) => s.id === SURFACE_IDS.advisorPanel)
    assert.ok(panel?.seat, 'panel must have a seat')
    assert.equal(panel.seat.key, 'sidebar.right.pane.tab')
    assert.equal(panel.seat.kind, 'keyed',
      'sidebar.right.pane.tab is keyed/session upstream; `details` was the single-shaped legacy')
    const def = slotRegisterDef(panel.seat.key, SURFACE_IDS.advisorPanel)
    assert.deepEqual(def, {
      name: 'sidebar.right.pane.tab',
      key: SURFACE_IDS.advisorPanel,
    }, 'keyed seats must register with `key`, not `id`')
  })

  it('the legacy fallback keeps a contract so the probe can still land on old hosts', () => {
    assert.notEqual(slotRegisterDef('details', 'pr-genius.x'), null,
      'details stays as a fallback candidate for hosts still on the 0.0.1 surface')
    assert.equal(VERIFIED_SLOT_CONTRACTS['details']?.kind, 'single',
      'its registration shape is still single — that is what the 0.0.1 host expects')
  })

  it('keys the 0.2.1 SDK removed are not presented as live defaults', () => {
    for (const removed of ['details', 'conversation', 'conversation.details.tool', 'settings.plugin.item']) {
      assert.notEqual(ADVISOR_PANEL_SLOT, removed,
        `${removed} was deleted from CLIENT_SLOT_API in 0.2.1 and must not be a default`)
    }
  })
})
