/**
 * 四个界面 + 维护者模式的注册层。
 *
 *
 * 诚实边界：插件曾在真 DSH 宿主跑过（issue #100/#101/#103 即真机暴露）；本机没有
 * DEEPSEEK_API_KEY，2.1.5 起的修复未经真机复验。这里只保证注册形状与契约一致、
 * TypeScript 编译通过；渲染与运行时行为需 DSH 运行时验证，本机未执行。
 */
import {
  isConfirmedSlotKey,
  REGISTERED_SLOTS,
  registerOptionsFor,
  type SlotSeat,
} from './slot-catalog.ts'
import { PANEL_SLOT_CANDIDATES } from '../client/slots.ts'


/** 四个界面 + 命令面的稳定标识 —— 配置与测试都引用这些常量，不写字面量。 */
export const SURFACE_IDS = {
  dashboard: 'pr-genius.dashboard',
  advisorTab: 'pr-genius.advisor-tab',
  advisorPanel: 'pr-genius.advisor-panel',
  command: 'pr-genius',
  preferences: 'pr-genius.preferences',
} as const

/** 维护者模式：切换只换投影，不换数据层 —— 两侧共用 kb 与 mcp 桥。 */
export type WorkMode = 'contributor' | 'maintainer'

export type SurfaceKind = 'dashboard' | 'tab' | 'panel' | 'command' | 'settings'

export interface SurfaceRegistration {
  id: string
  /**
   * 上游 catalog 里的座位。命令面走 `ctx.command`（Cordis 的命令 API，
   * 不是 slot），所以它的 seat 是 null —— 不硬造一个 slot 名。
   */
  seat: SlotSeat | null
  kind: SurfaceKind
  mode: WorkMode | 'both'
}

/**
 * 要注册的界面清单。维护者模式不是第二套界面，而是同一组界面的另一投影，
 * 所以它标记为 `mode: 'both'` 并由一个开关决定渲染哪一侧的数据。
 *
 * 落点（全部经上游 slot-catalog 核对存在，见 REGISTERED_SLOTS 的注释）：
 *   侧边栏脚部  dashboard    → sidebar.footer.action   list/root
 *   会话标签    advisorTab   → conversation.view       list/session
 *   右栏面板    advisorPanel → sidebar.right.pane.tab  keyed/session
 *   设置/偏好   preferences  → settings.section        list/root
 *   命令面      command      → ctx.command（非 slot，无 slot 落点）
 */
export const SURFACE_PLAN: SurfaceRegistration[] = [
  {
    id: SURFACE_IDS.dashboard,
    seat: REGISTERED_SLOTS.sidebarFooterAction,
    kind: 'dashboard',
    mode: 'both',
  },
  {
    id: SURFACE_IDS.advisorTab,
    seat: REGISTERED_SLOTS.conversationView,
    kind: 'tab',
    mode: 'both',
  },
  {
    id: SURFACE_IDS.advisorPanel,
    // 右栏落点在 SDK 0.2.1 里换了：`details`（single/session）被删，
    // `sidebar.right.pane.tab`（keyed/session，带 `.title` 伴席）成为唯一落点
    // （实测 CLIENT_SLOT_API 42 → 103 keys，见 issue #150）。默认走 keyed 那张
    // 真类型席位（REGISTERED_SLOTS.sidebarRightPaneTab，带 titleKey），
    // `details` 降为 legacy 兜底 —— 仍留在候选里给老宿主，但不再当默认。
    // 不二选一 —— 交给 apply() 逐个试，宿主认哪个用哪个，都不认就不注册（宁缺勿假）。
    seat: {
      ...REGISTERED_SLOTS.sidebarRightPaneTab,
      candidates: PANEL_SLOT_CANDIDATES,
    } as unknown as SlotSeat,
    kind: 'panel',
    mode: 'both',
  },
  {
    id: SURFACE_IDS.command,
    seat: null,
    kind: 'command',
    mode: 'both',
  },
  {
    id: SURFACE_IDS.preferences,
    seat: REGISTERED_SLOTS.settingsSection,
    kind: 'settings',
    mode: 'both',
  },
]

/**
 * 注册一个界面。返回 disposer —— Cordis 的「注册是可逆的副作用」，框架卸载时
 * 会调用它，贡献的组件 / slot 条目 / store 一并撤销。
 *
 * 这里刻意不写死组件实现：组件由调用方注入，本层只负责把「落点」这件事收敛到
 * 一处可核对的表里。好处是四个界面的 slot 归属能被测试断言，而不用渲染任何东西。
 */
export function planRegistrations(): SurfaceRegistration[] {
  return SURFACE_PLAN.map((r) => ({ ...r }))
}

/**
 * 一处界面的全部 register 调用：正文席 + 配对标题席（若上游成对，如
 * sidebar.right.pane.tab / .title）。每个元素是 `{ slotKey, options }`，
 * options 形状由上游基数决定，绝不臆造。
 *
 * 座位不在上游 catalog 里 → 返回空数组（保守降级：不注册、由调用方记 warn）。
 */
export function registrationCalls(
  surface: SurfaceRegistration,
): Array<{ slotKey: string; options: Record<string, string> }> {
  const { seat, id } = surface
  if (!seat) return []
  if (!isConfirmedSlotKey(seat.key)) return []
  const calls: Array<{ slotKey: string; options: Record<string, string> }> = [
    { slotKey: seat.key, options: registerOptionsFor(seat, id) },
  ]
  if (seat.titleKey && isConfirmedSlotKey(seat.titleKey)) {
    calls.push({
      slotKey: seat.titleKey,
      options: { name: seat.titleKey, [seat.cellOption]: id },
    })
  }
  return calls
}

/**
 * 断言某个界面挂在正确的 slot 上 —— 无需运行时即可验证「侧边栏安装配置架构」。
 * 契约或抄写出错时这里会红，而不是等到用户打开面板才发现空白。
 */
export function assertSlotPlacement(id: string, expectedSlot: string): void {
  const hit = SURFACE_PLAN.find((r) => r.id === id)
  if (!hit) throw new Error(`unknown surface id: ${id}`)
  const actual = hit.seat?.key ?? '(no slot: ctx.command)'
  if (actual !== expectedSlot) {
    throw new Error(`surface ${id} is planned for slot ${actual}, expected ${expectedSlot}`)
  }
}
