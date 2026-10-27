/**
 * DSH shipped slot catalog —— slot 名的唯一真相源（issue #97）。
 *
 * 权威来源（不是文档、不是参考插件用法、不是记忆）：
 *   repo:  deepseek-ai/deepseek-harness
 *          （任务里写的 deepseek-ai/deepseek-harness-sdk 不存在，404；
 *            代码搜索定位到的实际仓库是 deepseek-ai/deepseek-harness）
 *   path:  packages/extensions/cordis-client-runner/src/client/slot-catalog.ts
 *   blob:  7c8f7af10ff12104636f54a828556c4a1fd9d208
 *   commit 2db0c83e867c23918963ae8314630887d316e79d (2026-10-02T19:19:43Z)
 *   sha256[:16]: cba8c35b61fabd30
 *   fetched:   2026-10-03 via `gh api repos/deepseek-ai/deepseek-harness/contents/...`
 *
 * 下面的 CONFIRMED_SLOT_KEYS 是从上述文件的字节里**生成**的，不是手写的：
 *   `grep -E "^  key: '" slot-catalog.ts` 的 92 个 key，按字典序。
 * 重新拉取/校对用 `node scripts/verify-slot-keys.mjs`（会对比快照与上游 blob）。
 *
 * 纪律：注册之前先查这张表。表里没有的 key 一律不注册，只记 warn ——
 * 宁缺勿假（v2.0.0 / v2.1.0 / v2.1.1 / v2.1.2 连续四版都栽在臆造 slot 名上）。
 */

/** 上游契约文件的出处，供 verify 脚本与审计回查。 */
export const CATALOG_PROVENANCE = {
  repo: 'deepseek-ai/deepseek-harness',
  path: 'packages/extensions/cordis-client-runner/src/client/slot-catalog.ts',
  blobSha: '791274948f015f1e',
  commit: '2db0c83e867c23918963ae8314630887d316e79d',
  commitDate: '2026-10-02T19:19:43Z',
  fetchedAt: '2026-10-26',
  keyCount: 105,
} as const

/** 上游 catalog 里存在的全部 slot key（生成物，勿手改；重跑 verify 脚本刷新）。 */
export const CONFIRMED_SLOT_KEYS: readonly string[] = [
  'conversation.approval.detail',
  'conversation.chat.assistant-actions',
  'conversation.chat.commandview',
  'conversation.chat.flow',
  'conversation.chat.message.images',
  'conversation.chat.node',
  'conversation.chat.reasoning.body',
  'conversation.chat.text-interaction',
  'conversation.chat.turnTail',
  'conversation.chat.user.images',
  'conversation.composer',
  'conversation.composer.bar',
  'conversation.composer.dock',
  'conversation.header',
  'conversation.header.leading',
  'conversation.hero.agentPreset',
  'conversation.hero.brand.mark',
  'conversation.hero.options',
  'conversation.hero.workspace',
  'conversation.hero.workspace.directoryFlow',
  'conversation.input.activity',
  'conversation.input.attachments',
  'conversation.input.dock',
  'conversation.input.left',
  'conversation.input.model',
  'conversation.input.model.label',
  'conversation.input.overlay',
  'conversation.input.permission',
  'conversation.input.plan',
  'conversation.input.right',
  'conversation.plan-review.actions',
  'conversation.session',
  'conversation.session.header',
  'conversation.session.header.actions',
  'conversation.session.header.corner',
  'conversation.session.header.lineage',
  'conversation.session.header.utilities',
  'conversation.session.header.views.actions',
  'conversation.trajectory.images',
  'conversation.user.text.node',
  'conversation.view',
  'deliverables.file.actions',
  'deliverables.review.file.actions',
  'main',
  'main.conversation',
  'plugins.add.actions',
  'plugins.bundle.activation',
  'plugins.bundle.config',
  'plugins.detail.actions',
  'plugins.detail.badge',
  'plugins.detail.section',
  'plugins.item',
  'plugins.row.config',
  'plugins.tab',
  'rightbar',
  'rightbar.session',
  'root',
  'settings.action',
  'settings.close',
  'settings.general.item',
  'settings.header',
  'settings.launcher',
  'settings.models.footer',
  'settings.models.provider-card',
  'settings.models.sign-in',
  'settings.onboarding',
  'settings.plugins.tab',
  'settings.section',
  'settings.trigger',
  'shell.bottom',
  'shell.leading',
  'shell.overlay',
  'shell.quota-notice',
  'sidebar',
  'sidebar.brand.mark',
  'sidebar.brand.name',
  'sidebar.chat.conversation',
  'sidebar.footer.action',
  'sidebar.panellist',
  'sidebar.panellist.actions',
  'sidebar.right.pane.tab',
  'sidebar.right.pane.tab.title',
  'sidebar.right.tab.document',
  'sidebar.right.tab.document.action',
  'sidebar.right.tab.document.actions',
  'sidebar.right.tab.document.office.pdf',
  'sidebar.right.tab.document.unpreviewable',
  'sidebar.right.tab.files.actions',
  'sidebar.right.tab.guide',
  'sidebar.right.tab.guide.actions',
  'sidebar.right.tab.guide.entry',
  'sidebar.right.tab.menu.item',
  'sidebar.session.row.hover',
  'sidebar.session.row.leading',
  'sidebar.session.row.trailing',
  'sidebar.settings',
  'sidebar.toggle.badge',
  'sidebar.workspaces',
  'sidebar.workspaces.directoryFlow',
  'sidebar.workspaces.session.menu.item',
  'sidebar.workspaces.session.row.action',
  'tool.call.images',
  'tool.call.toolview',
  'tool.view.cordis',
  'workspace.toast',
]

const CONFIRMED: ReadonlySet<string> = new Set(CONFIRMED_SLOT_KEYS)

/** key 是否在上游 catalog 里。查不到 → 不注册，只 warn。 */
export function isConfirmedSlotKey(key: string): boolean {
  return CONFIRMED.has(key)
}

/** 基数（cardinality），与上游 catalog 的 `kind` 字段一致。 */
export type SlotKind = 'single' | 'list' | 'keyed' | 'chain'
/** 数据作用域，与上游 catalog 的 `scope` 字段一致。 */
export type SlotScope = 'root' | 'session-maybe' | 'session'
/** register 调用在 `name` 之外必须带的那个选项名。 */
export type CellOptionName = 'id' | 'key'

/**
 * pr-genius 要注册进去的座位。字段值全部取自上游 catalog 的对应 entry
 * （key / kind / scope / registerOptions），不是从用法反推的。
 */
export interface SlotSeat {
  /** 上游 SlotMap key，一字不差。 */
  readonly key: string
  readonly kind: SlotKind
  readonly scope: SlotScope
  /** 该基数要求的 register 选项：list→id，keyed→key，single→无。 */
  readonly cellOption: CellOptionName
  /** 配对的标题席（keyed 正文/标题成对，见上游 occupants 的 Body+Title 组合）。 */
  readonly titleKey?: string
}

/**
 * 四个界面的落点表 —— 单一真相源。src/client/slots.ts 的类型声明与
 * SLOT_DECLARATIONS 都从这里派生，不再各写各的（issue #95 的根因）。
 *
 * 落点选择依据上游 catalog 的 summary/doc：
 *   sidebar.footer.action    list/root   "Optional actions beside Settings at the sidebar foot."
 *   conversation.view        list/session "Registered Conversation target Views, rendered one at a time."
 *   sidebar.right.pane.tab   keyed/session "One tab's body, dispatched with the `id` of the type in force"
 *   settings.section         list/root   "One settings page per list entry."（多设置项 → 整页；
 *                                         单设置项的加法座位是 settings.general.item）
 *
 * 注意：`details` 这个 key **不在** 上游 catalog 里（92 个 key 中无此名；
 * 回溯到 2026-09-18 的历史快照 74 个 key 时也没有）。issue #97 断言右栏
 * 真实 key 是 `details` —— 与权威 catalog 不符，不予采用。
 */
export const REGISTERED_SLOTS = {
  /** 侧边栏脚部。 */
  sidebarFooterAction: {
    key: 'sidebar.footer.action',
    kind: 'list',
    scope: 'root',
    cellOption: 'id',
  },
  /** 会话标签（与 Chat/Trajectory 并列的一栏）。 */
  conversationView: {
    key: 'conversation.view',
    kind: 'list',
    scope: 'session',
    cellOption: 'id',
  },
  /**
   * 右栏面板。上游是 keyed（不是 single）：register 必须带 `key` 选项，
   * keyDomain 为 "open: any string the owner dispatches"。
   * 标题席与正文席成对注册，沿用上游 occupants 的 Body+Title 形态。
   */
  sidebarRightPaneTab: {
    key: 'sidebar.right.pane.tab',
    kind: 'keyed',
    scope: 'session',
    cellOption: 'key',
    titleKey: 'sidebar.right.pane.tab.title',
  },
  /** 设置页（偏好项多 → 整页；settings.section 是"一列表项一页"）。 */
  settingsSection: {
    key: 'settings.section',
    kind: 'list',
    scope: 'root',
    cellOption: 'id',
  },
} as const satisfies Record<string, SlotSeat>

/** 全部落点的 key（含配对标题席），用于自检。 */
export function registeredSlotKeys(): string[] {
  const out: string[] = []
  const seats: readonly SlotSeat[] = Object.values(REGISTERED_SLOTS)
  for (const seat of seats) {
    out.push(seat.key)
    if (seat.titleKey) out.push(seat.titleKey)
  }
  return out
}

/**
 * register 调用的 options：`name` = slot key（上游示例如此），
 * 外加该基数要求的 cell 选项（list→id，keyed→key）。
 * `kind`/`scope` 不是 register 选项 —— 它们是 children 声明表的字段。
 */
export function registerOptionsFor(
  seat: SlotSeat,
  cellId: string,
): Record<string, string> {
  return { name: seat.key, [seat.cellOption]: cellId }
}
