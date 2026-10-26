/**
 * 侧边栏 / 会话界面的 slot 声明 —— 编译期契约 + 注册形状。
 *
 * 权威依据（唯一）：DSH SDK 源码的 slot-catalog
 *   deepseek-ai/deepseek-harness
 *   packages/extensions/cordis-client-runner/src/client/slot-catalog.ts
 * 本机 2026-10-03 用 `gh api` 真实抓取（注意：deepseek-ai/deepseek-harness-sdk
 * 不存在，404；仓库名是 deepseek-harness）。快照固化在
 * docs/slot-catalog-evidence.json（92 个 key，机械抽取，非手写）。
 *
 */
import type { SlotEntryDef } from '@deepseek-ai/dsh-client-ui-slots'
import { REGISTERED_SLOTS, type SlotSeat } from '../ui/slot-catalog.ts'


/**
 * catalog 核对过的槽位契约。kind/scope 与 slot-catalog.ts 逐字一致；
 * entryShape 决定 register() 第一个参数的形状
 * （list → id，keyed → key，single → 只有 name，不带 cell）。
 */
export interface VerifiedSlotContract {
  kind: 'list' | 'keyed' | 'single' | 'chain'
  scope: 'root' | 'session' | 'session-maybe'
  /**
   * register() 的 cell 参数形状：list 槽用 id，keyed 槽用 key，
   * single 槽没有 cell 项（SDK 的 registerOptions 对 single 只声明 name）。
   */
  entryShape: 'id' | 'key' | 'none'
  /** slot-catalog.ts 里的 source 字段（出处行）。 */
  catalogSource: string
}

/**
 * **候选提示，不是权威白名单。**
 *
 * 决定改在这里（issue #97 反复翻车后的取舍）：pinned SDK 与 upstream master
 * 的 catalog 不一致（实测 0.0.1-rc.3 有 42 keys、0.2.1-rc.3 有 103 keys），
 * 数字用括号匹配数 CLIENT_SLOT_API 顶层元素得出，与 release-smoke gate 的
 * `catalog keys=` 报告一致；扫 `key:` 正则会把嵌套对象的 key 字段多算进去。
 * 两者都自称权威，对着任一个写死判据都会在对方更新时被推翻。所以权威是**运行时**
 * ——apply() 逐个试候选，宿主认哪个用哪个。这张表只回答「注册时该带哪些
 * options」，不回答「这个 key 合不合法」。
 */
export const VERIFIED_SLOT_CONTRACTS: Record<string, VerifiedSlotContract> = {
  'sidebar.footer.action': {
    kind: 'list',
    scope: 'root',
    entryShape: 'id',
    catalogSource: 'packages/extensions/cordis-client-runner/src/client/slot-catalog.ts',
  },
  'conversation.view': {
    kind: 'list',
    scope: 'session',
    entryShape: 'id',
    catalogSource: 'packages/extensions/cordis-client-runner/src/client/slot-catalog.ts',
  },
  /**
   * 右栏落点 **legacy 兜底**（SDK 0.2.1 已删除此 key）。
   *
   * 0.2.1 的 CLIENT_SLOT_API 只有 `sidebar.right.pane.tab`（keyed/session），
   * `details`（single/session）被删；但宿主版本不可控，老宿主仍只认 `details`。
   * 所以两个契约都登记、候选按「活的在前」排序 —— 只登记一个会让另一个的注册
   * 静默失败。默认值是 `ADVISOR_PANEL_SLOT`，走 keyed 那张。
   */
  'details': {
    kind: 'single',
    scope: 'session',
    // single 基数只接受 name —— 不是 id。gate 的 C4 报过这一点：多传 id/label
    // 会被 SDK 忽略或报错（CLIENT_SLOT_API 对 single 的 registerOptions
    // 只声明 name）。id 是 list 基数的 cell 选项，别照抄。
    entryShape: 'none',
    catalogSource: '@deepseek-ai/dsh-cordis-client-runner 0.0.1-rc.3 CLIENT_SLOT_API (legacy)',
  },
  'sidebar.right.pane.tab': {
    kind: 'keyed',
    scope: 'session',
    entryShape: 'key',
    catalogSource: 'packages/extensions/cordis-client-runner/src/client/slot-catalog.ts',
  },
  /**
   * 设置/偏好落点。SURFACE_PLAN 的 preferences seat 用的就是这个 key（唯一，不是候选）。
   * `settings.plugins.tab` 曾并列登记在这里，但它不在 preferences 的 candidates 里、
   * apply() 也不探测它 —— 两份 catalog 对它与 settings.section 的形状还完全一致
   * （都是 list/root），没有分歧需要探测兜底。留着只会让表看起来像有两个落点，
   * 所以删掉；需要它时应当先给 preferences 加 candidates，而不是让契约表撒谎。
   */
  'settings.section': {
    kind: 'list',
    scope: 'root',
    entryShape: 'id',
    catalogSource: 'pinned SDK CLIENT_SLOT_API (gate ledger: accepted)',
  },
}

/** register() 第一参数 —— 形状来自 slot-catalog 的 example（name=槽名 + id/key=cell）。 */
export interface SlotRegisterDef {
  name: string
  id?: string
  key?: string
  label?: string
  order?: number
}

/**
 * 生成注册参数。槽位不在核对表里返回 null（调用方必须跳过注册并 warn）。
 * list 槽：{ name, id, label, order }；keyed 槽：{ name, key }（catalog 的
 * registerOptions 对 keyed 只要求 key，不收 id/label/order，故不附带）。
 */
export function slotRegisterDef(slot: string, cellId: string, label?: string): SlotRegisterDef | null {
  const contract = VERIFIED_SLOT_CONTRACTS[slot]
  if (contract === undefined) return null
  if (contract.entryShape === 'key') return { name: slot, key: cellId }
  // single 基数：SDK 的 registerOptions 只声明 name。多传 id/label 会被忽略或报错
  // （gate 的 C4 就报过这一点），所以这里只给 name。
  if (contract.entryShape === 'none') return { name: slot }
  return label === undefined ? { name: slot, id: cellId } : { name: slot, id: cellId, label }
}

declare module '@deepseek-ai/dsh-client-ui-slots' {
  interface SlotMap {
    /** 侧边栏脚部（list / root）：Dashboard 与 Preferences 各占一项。 */
    'sidebar.footer.action': { kind: 'list'; scope: 'root' }
    /** 会话视图标签页（list / session）：顾问 Tab 与 Chat/Trajectory 并列。 */
    'conversation.view': { kind: 'list'; scope: 'session' }
    /**
     * 右栏落点有两个版本的 catalog 说不同的话（实测见 issue #150；本仓没有
     * docs/slot-key-drift.md 这份文件，旧注释引错过）：
     * 0.0.1-rc.x 里是 `details`（single），0.2.1-rc.3 里是 `sidebar.right.pane.tab`（keyed）。
     * 运行时探测决定用谁，所以这里把两个都声明成可注册，由 apply() 挑实际存在的。
     */
    'details': { kind: 'single'; scope: 'session' }
    'sidebar.right.pane.tab': { kind: 'keyed'; scope: 'session' }
  }

  interface LocaleNamespaceMap {
    'pr-genius':
      | 'surface.dashboard'
      | 'surface.advisorTab'
      | 'surface.advisorPanel'
      | 'surface.command'
      | 'surface.preferences'
      | 'mode.contributor'
      | 'mode.maintainer'
      | 'risk.low_risk'
      | 'risk.medium_risk'
      | 'risk.high_risk'
      | 'empty.noVerdict'
  }
}

/**
 * 四个界面的落点名 —— 必须与 SURFACE_PLAN 的 seat 一致（apply() 从那里注册）。
 * 面板走候选表，运行时探测（见 apply()）。
 */
export const DASHBOARD_SLOT = 'sidebar.footer.action'
export const ADVISOR_TAB_SLOT = 'conversation.view'
/**
 * 右栏面板默认落点。必须是**升级后 SDK 仍声明**的 key：
 * 0.2.1 的 CLIENT_SLOT_API 删掉了 `details`、新增 `sidebar.right.pane.tab` / `.title`
 * （实测 42 → 103 keys，见 issue #150）。`details` 只作为 legacy 兜底留在候选里，
 * 不再是默认值 —— 一个被 SDK 删掉的 key 当默认值，等于把每个新宿主的注册送到空座位。
 */
export const ADVISOR_PANEL_SLOT = 'sidebar.right.pane.tab'
/** 权威是 SURFACE_PLAN 的 preferences seat（REGISTERED_SLOTS.settingsSection）——不是 dashboard 的脚部席。 */
export const PREFERENCES_SLOT = 'settings.section'
/**
 * 探测顺序：**活的在前，legacy 兜底在后**（issue #142）。
 * 顺序不是洁癖 —— apply() 试到被接受就 break，死的排前面会让每次启动都白烧一次
 * 失败注入，而 release-smoke 的 C1 会把这次尝试记成「key 不在权威 catalog 内」。
 */
export const PANEL_SLOT_CANDIDATES = ['sidebar.right.pane.tab', 'details']

/** 契约表 → register() 的第一参数。 */
export function specOf(seat: SlotSeat): SlotEntryDef {
  return { kind: seat.kind, scope: seat.scope }
}

export const SLOT_DECLARATIONS = {
} as const satisfies Record<string, SlotEntryDef>

/** `declare module` 的字面 key 集合，与真相源对齐的编译期断言。 */
type DeclaredSlotKeys =
  | 'sidebar.footer.action'
  | 'conversation.view'
  | 'sidebar.right.pane.tab'
  | 'sidebar.right.pane.tab.title'
  | 'settings.section'

type SeatKeys =
  | (typeof REGISTERED_SLOTS)[keyof typeof REGISTERED_SLOTS]['key']
  | (typeof REGISTERED_SLOTS)['sidebarRightPaneTab']['titleKey']

type Equal<A, B> = (<T>() => T extends A ? 1 : 2) extends <T>() => T extends B ? 1 : 2
  ? true
  : false

/** 两边键集不一致 → 编译报错。 */
type DeclaredSeatKeysMatchCatalog = Equal<DeclaredSlotKeys, SeatKeys> extends true
  ? true
  : never
export const declaredSeatKeysMatchCatalog: DeclaredSeatKeysMatchCatalog = true
