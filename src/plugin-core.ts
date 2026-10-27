/**
 * 插件核心 —— **浏览器安全**的那半（issue #159）。
 *
 * 为什么单独一层：`src/index.ts` 混了 node 专属依赖（`kb.ts` → `node:fs`、
 * `mcp-client.ts` → 子进程），没法直接当浏览器包发。而 DSH 的 web 端要的是
 * **一个独立的 client bundle** —— `package.json` 声明了 `dsh.client` 却没有
 * `exports["./client"]` 时，DSH 的 `client-modules` 会静默把插件从 client graph
 * 里丢掉（八次「空壳安装」的共同根因）。
 *
 * 所以这一层只放**两半共用**的东西，运行时差异经 `runtime` 参数注入：
 *   - 宿主半边（`src/index.ts`）注入 `kb`（读盘）与 `mcpInvoker`（子进程）
 *   - client 半边（`src/client/index.ts`）注入浏览器版，取不到就说取不到
 *
 * 判据：本文件不得 import `kb.ts` / `mcp-client.ts` / 任何 `node:` 内建。
 * 那两个类型只以 `import type` 引入 —— 类型在编译期擦除，不会进 bundle。
 */
import type { Context } from '@deepseek-ai/cordis'
import { planRegistrations, SURFACE_IDS, SURFACE_PLAN } from './ui/surfaces.ts'
// 导入 client 层是让它进 bundle 的唯一途径 —— 此前它只是躺在 src/client/ 里
// 未被引用，所以 tsc 通过、bundle 里却没有它（issue #90）。
import { surfaceComponents, type AdvisorFace } from './client/AdvisorPanel.tsx'
import { slotRegisterDef } from './client/slots.ts'
import {
  Config,
  parseConfig,
  type MaintainerAction,
  type RiskTier,
} from './config.ts'
import type { KbLayout } from './kb.ts'
import type { McpInvoker } from './mcp-client.ts'

/** 插件名 —— 两半共用的唯一来源；入口各自 re-export 给 DSH 读。 */
export const name = 'pr-genius'

/** 两半各自注入的运行时能力。核心不假设它们从哪来。 */
export interface PluginRuntime {
  readonly kb: KbLayout
  readonly version: string
  readonly invoker: McpInvoker
}

export interface PrGeniusRuntimeInfo {
  name: string
  version: string
  kbRoot: string
  mcp: {
    transport: string
    /** stdio 时为 `${command} ${args.join(' ')}`，http 时为 url。 */
    endpoint: string
    timeoutMs: number
    protocolVersion: string
  }
  sidebar: { defaultView: string }
  maintainer: {
    enabled: boolean
    actions: MaintainerAction[]
    confidenceMin: number
    staleDays: number
  }
  locale: string
  riskFilter: RiskTier
  /**
   * 四界面 + 命令面的注册结果（apply() 跑完后才有值）。
   *
   * 为什么要有这个字段：空壳安装（四个面一个都没注册上）连续发生过八次
   * （#86/#90/#95/#97/#98/#100/#101/#117），每次都靠单测说"已修"、没人真跑过。
   * 日志里的一条 warn 藏得住，describe() 里的结构化结果藏不住 —— 宿主可以直接打出来，
   * 测试可以直接断言。见 issue #131。
   */
  surfaces: SurfaceReport | null
}

/** 一个界面的注册结局。`registered` 为假时 `candidates` 是试过的落点。 */
export interface SurfaceReportEntry {
  id: string
  registered: boolean
  /** 实际被宿主接受的 slot key；命令面为 `ctx.command`。 */
  seat?: string
  /** 试过的候选落点（宿主一个都没认时）。 */
  candidates?: string[]
  /** 失败原因的人话版本。 */
  reason?: string
  /** 我们自己的 catalog 快照里没有这些 key —— 是我们的表，不是宿主。 */
  unknownToTable?: string[]
  /** key 我们认识，但宿主拒绝了。 */
  hostRefused?: string[]
}

export interface SurfaceReport {
  /** 计划注册的界面数（4 个 slot 面 + 1 个命令面）。 */
  expected: number
  registered: SurfaceReportEntry[]
  failed: SurfaceReportEntry[]
  /** 整个 slots 服务是否可用；false 说明本会话没有 web 运行时。 */
  slotsAvailable: boolean
}

/** 插件服务：配置投影 + 通往 Python 分析引擎的调用口。 */
export interface PrGeniusService {
  readonly config: ReturnType<typeof parseConfig>
  readonly kb: KbLayout
  /** 运行时形态描述（纯函数，无副作用）。 */
  describe(): PrGeniusRuntimeInfo
  /**
   * 调用 Python FastMCP 工具（analyze_pr / coach_pr / maintainer_view / ...）。
   * 工具名与参数原样透传 prgenius/src/prgenius/mcp.py，TS 不做任何再加工。
   */
  callTool(tool: string, args?: Record<string, unknown>): Promise<unknown>
  /** 释放传输层。由插件卸载自动调用；也可显式调用，幂等。 */
  close(): Promise<void>
}

export interface PrGeniusServiceDeps {
  config: ReturnType<typeof parseConfig>
  kb: KbLayout
  version: string
  invoker: McpInvoker
  /** apply() 在注册结束后回填；describe() 原样透出，供宿主/测试读。 */
  getSurfaceReport?: () => SurfaceReport | null
}

export function createPrGeniusService(deps: PrGeniusServiceDeps): PrGeniusService {
  const { config, kb, version, invoker, getSurfaceReport } = deps
  return {
    config,
    kb,
    describe(): PrGeniusRuntimeInfo {
      return {
        name,
        version,
        kbRoot: kb.root,
        mcp: {
          transport: config.mcp.transport,
          endpoint:
            config.mcp.transport === 'http'
              ? config.mcp.url
              : [config.mcp.command, ...config.mcp.args].join(' '),
          timeoutMs: config.mcp.timeoutMs,
          protocolVersion: config.mcp.protocolVersion,
        },
        sidebar: { defaultView: config.sidebar.defaultView },
        maintainer: {
          enabled: config.maintainer.enabled,
          actions: [...config.maintainer.actions],
          confidenceMin: config.maintainer.confidenceMin,
          staleDays: config.maintainer.staleDays,
        },
        locale: config.locale,
        riskFilter: config.riskFilter,
        surfaces: getSurfaceReport ? getSurfaceReport() : null,
      }
    },
    callTool(tool: string, args: Record<string, unknown> = {}) {
      return invoker.callTool(tool, args)
    },
    close() {
      return invoker.close()
    },
  }
}

/**
 * 可选服务探测 —— 经 `ctx.get(name)`，不走属性直读。
 *
 * 权威依据：DSH guard 的 dynamicCordisContext（node_modules/@deepseek-ai/
 * dsh-cordis-client-runner/lib/client.js，动态插件的 apply() 收到的白名单 facade）：
 *   - `ctx.slots` 直读 → readService(prop, true) → 名字不在 declared
 *     （`new Set(Object.keys(ctx.fiber.inject))`）就 denyRead **抛错**；
 *   - `Reflect.has(ctx, 'slots')` → has trap → 只答 `declared.has(prop)`。
 *     inject 为空时恒 false：不抛，但探测永远失败，四个界面静默不注册（issue #100）；
 *   - `ctx.get('slots')` → readService(name, false) → **可选查找，不需要 inject 声明**
 *     （cordis `ReflectService.get` 的 docstring：“Read a service from the store
 *     without the inject requirement.”）。
 *
 * 所以可选服务只能经 ctx.get 取。宿主是普通对象（测试 mock，没有 ctx.get）时
 * 退化为直读 —— 否则 mock 里的字面量属性读不到。真 guard 下直读会抛，那是要
 * 避免的路径；mock 退化只为测试可跑，不是给真宿主的第二条路。
 */
export function optionalService<T>(ctx: object, name: string): T | undefined {
  const get = (ctx as { get?: (n: string) => unknown }).get
  if (typeof get === 'function') return get.call(ctx, name) as T | undefined
  return (ctx as Record<string, unknown>)[name] as T | undefined
}

/** apply() 只用到的三个日志口 —— 兜底实现要满足的最小面。 */
type Logger = {
  info: (...args: unknown[]) => void
  warn: (...args: unknown[]) => void
  error: (...args: unknown[]) => void
}

/**
 * 取命名 logger —— 比 slots 更靠前的一个坑，不能裸读 `ctx.logger`。
 *
 * 为什么不能直接 `ctx.logger('pr-genius')`：`logger` **不在** guard 的
 * `CTX_VERBS` 白名单里（client.js / upstream guard.ts 两处都是 effect/on/once/
 * provide/timer 系，均无 logger；upstream guard.ts 全文 0 次提到 logger），而
 * facade 的 proxy target 是空对象。于是 `ctx.logger` 落到 `readService(prop, true)`
 * → 不在 declared → `denyRead` **抛错**。那是 apply() 的第一行，抛在这儿连
 * `ctx.get` 的探测都跑不到 —— issue #100 的修法会被它抵消。
 *
 * 也不能改走 `ctx.get('logger')` 或 `inject: ['logger']`：`LoggerService` 不
 * `extends Service`、不调 `provide()`（cordis `lib/index.js` 的 Context 构造器里
 * `this.logger = new LoggerService(self)` 只是属性赋值），所以它**不在 service
 * store** 里。`ctx.get` 恒 undefined；写进 inject 更糟 —— `_checkImpl` 查不到
 * impl 就 `delete this._store[name]`，`_refresh` 判 INACTIVE，fiber **永久挂起**，
 * 插件永不加载。
 *
 * 分流靠 `Reflect.has(ctx, 'logger')`，它在两种宿主下都是安全的：
 *   - 普通 cordis Context：`logger` 是自有属性 → has 为 true → 可直读；
 *   - guard facade：has 陷阱答 `declared.has(prop)` → false，**且不抛**。
 * 所以 true 才读，false 就降级到 console 兜底 —— 日志缺失绝不让 apply() 崩掉。
 */
export function resolveLogger(ctx: object, name: string): Logger {
  // 普通 cordis Context：logger 是 Context 的自有属性，可安全直读。
  if (Reflect.has(ctx, 'logger')) {
    const maybe = (ctx as { logger?: (n: string) => Logger }).logger
    if (typeof maybe === 'function') return maybe.call(ctx, name)
  }
  // 宿主若把 logger 注册成服务（可选，当前上游没有），ctx.get 能拿到。
  const viaGet = optionalService<unknown>(ctx, 'logger')
  if (typeof viaGet === 'function') return (viaGet as (n: string) => Logger).call(ctx, name)
  // DSH guard facade 上 logger 取不到 —— 用 console 兜底，不空转、更不抛。
  const tag = `[${name}]`
  return {
    info: (...args: unknown[]) => console.info(tag, ...args),
    warn: (...args: unknown[]) => console.warn(tag, ...args),
    error: (...args: unknown[]) => console.error(tag, ...args),
  }
}

/**
 * 插件入口：注册服务 + 挂好清理。返回 void，卸载时由 fiber 自动还原。
 *
 * 配置非法 → 抛 PrGeniusConfigError（字段路径见 message），加载即失败，不带病运行。
 * kbRoot 布局缺失 → 同样抛错，响亮失败。
 */

  // 注册结果由下面的循环回填；describe() 通过这个闭包读到它。
export function applyWith(ctx: Context, config: Config, runtime: PluginRuntime): void {
  const { kb, version, invoker } = runtime
  // 防御性再校验：框架已按 schema 校验过，这里保证直接调用 apply() 时同样响亮。
  const resolved = parseConfig(config)
  // 不裸读 ctx.logger —— guard facade 上 logger 不在 CTX_VERBS，直读会 denyRead 抛错。
  // 见 resolveLogger 的注释（含为什么 inject/logger 和 ctx.get/logger 都不通）。
  const logger = resolveLogger(ctx, 'pr-genius')
  const surfaceReport: SurfaceReport = {
    expected: SURFACE_PLAN.length,
    registered: [],
    failed: [],
    slotsAvailable: false,
  }
  const service = createPrGeniusService({
    config: resolved,
    kb,
    version,
    getSurfaceReport: () => surfaceReport,
    invoker,
  })

  // provide 返回的 disposable 会随 fiber 卸载自动撤销服务注册。
  const disposeService = ctx.provide('prGenius', service)

  // ── 四个界面 ──────────────────────────────────────────────────────────
  const face: AdvisorFace = {
    service, locale: resolved.locale,
    workMode: resolved.maintainer.enabled ? 'maintainer' : 'contributor',
    riskFilter: resolved.riskFilter,
  }
  const COMPONENTS = surfaceComponents(face)

  const surfaceDisposers: Array<() => void> = []

  // 可选服务经 ctx.get 探测（见 optionalService 的权威依据）。command 不在 guard
  // 的 CTX_VERBS 白名单里，真宿主上 ctx.get('command') 也返回 undefined —— 与此前
  // Reflect.has 恒 false 同效：跳过、warn、不抛。缺服务就是降级，不升级成加载失败。
  const commandService = optionalService<
    (name: string) => {
      action?: (fn: () => unknown) => unknown
      option?: unknown
    }
  >(ctx, 'command')
  if (typeof commandService === 'function') {
    const cmd = commandService(SURFACE_IDS.command)
    cmd.action?.(() => {
      // 快查弹窗：不离开聊天就得到「能不能提 PR」的结论 + 阻塞项。
      // 分析逻辑在 Python 侧（coach_pr），TS 只透传 —— 见架构约束注释。
      void service
        .callTool('coach_pr', { title: '', body: '', repo: '' })
        .then(
          (verdict: unknown) =>
            logger.info('[%s] %s', SURFACE_IDS.command, JSON.stringify(verdict).slice(0, 400)),
          (err: unknown) => logger.error('[%s] failed: %s', SURFACE_IDS.command, String(err)),
        )
    })
    surfaceDisposers.push(() => logger.info('command %s unregistered', SURFACE_IDS.command))
    surfaceReport.registered.push({
      id: SURFACE_IDS.command,
      registered: true,
      seat: 'ctx.command',
    })
    logger.info('surface ready: %s (slash command)', SURFACE_IDS.command)
  } else {
    surfaceReport.failed.push({
      id: SURFACE_IDS.command,
      registered: false,
      reason: 'ctx.command unavailable',
    })
    logger.warn('ctx.command unavailable — slash surface not registered')
  }

  // ctx.get('slots') 拿到的可能是 guardedSlots 代理（真宿主），.inject/.register
  // 仍可调用（guard 只做转发 + 记账，见 client.js 的 guardedSlots）。
  const slotsService = optionalService<{
    inject?: (slot: string, factory: () => unknown) => () => void
    register?: (def: unknown, component: unknown) => () => void
  }>(ctx, 'slots')
  surfaceReport.slotsAvailable = Boolean(slotsService?.inject && slotsService?.register)
  if (slotsService?.inject && slotsService?.register) {
    // 运行时探测：候选落点里挑宿主真的提供的那个。
    // 不静态硬编码争议 key —— 不同 SDK 版本的 catalog 不一致
    // （实测 42 vs 103 keys，右栏落点分别是 details / sidebar.right.pane.tab，见 issue #150），
    // 谁存在用谁；都不存在就不注册。宁缺勿假。
    for (const surface of planRegistrations()) {
      if (surface.kind === 'command') continue
      const candidates: string[] = Array.isArray((surface.seat as { candidates?: string[] } | null)?.candidates)
        ? ((surface.seat as { candidates?: string[] }).candidates as string[])
        : [surface.seat].filter(Boolean).map((x) => (x as { key?: string }).key ?? '')
      // 真探测：逐个候选试注册，宿主不认就换下一个。不靠"key 非空"这种假探测。
      //
      // 两种失败必须说不同的话（issue #139）：
      //   unknown_to_table — 我们的 catalog 快照里没有这个 key。快照落后时这会假装
      //                      成"宿主不给座位"，而其实座位是有的、是我们没登记。
      //   host_refused     — key 我们认识，宿主不要。
      // 「宁缺勿假」仍然成立：表里没有的一律不注册。但报错必须让人分得清是谁拒绝的，
      // 否则 #102 那种真机报告会把快照落后读成宿主故障。
      let registered = false
      const unknownToTable: string[] = []
      const hostRefused: string[] = []
      for (const key of candidates) {
        if (!key) continue
        try {
          const def = slotRegisterDef(key, surface.id, surface.id)
          if (!def) {
            unknownToTable.push(key)
            logger.warn(
              'surface %s: slot %s is not in pr-genius\'s own catalog snapshot, so it is not registered — ' +
                'this is our table, not your host. If the host does offer it, our snapshot is stale (#139).',
              surface.id, key,
            )
            continue
          }
          const dispose = slotsService.inject(key, () =>
            slotsService.register!(def, COMPONENTS[surface.id] ?? null))
          surfaceDisposers.push(dispose)
          logger.info('surface registered: %s -> %s', surface.id, key)
          surfaceReport.registered.push({ id: surface.id, registered: true, seat: key })
          registered = true
          break
        } catch (err) {
          hostRefused.push(key)
          logger.warn('surface %s: slot %s rejected by the host (%s); trying next candidate', surface.id, key, String(err))
        }
      }
      if (!registered) {
        // 宁缺勿假：一个都不注册。但要把原因写清楚。
        const allUnknown = hostRefused.length === 0 && unknownToTable.length > 0
        const reason = allUnknown
          ? 'every candidate is absent from pr-genius\'s catalog snapshot — this is our table, not the host'
          : hostRefused.length > 0
            ? 'the host refused every candidate slot we know'
            : 'no candidate slot to try'
        logger.warn(
          'surface %s: not registered (%s). candidates=%j known_to_table=%j unknown_to_table=%j',
          surface.id, reason, candidates, hostRefused, unknownToTable,
        )
        surfaceReport.failed.push({
          id: surface.id,
          registered: false,
          candidates: candidates.filter(Boolean),
          reason,
          unknownToTable,
          hostRefused,
        })
      }
    }
  } else {
    logger.warn(
      'ctx.slots unavailable — dashboard / tab / panel / settings surfaces not registered ' +
        '(need a DSH web host; this session has no runtime)',
    )
  }

  // 空壳安装的告警（issue #131）：slots 在、四个面一个都没注册上 —— 这才是
  // "装了但什么都没有"的形状，也是 #86/#90/#95/#97/#98/#100/#101/#117 连续八次
  // 被单测说"已修"却没人看见的原因。warn 藏得住，error 不该藏。
  //
  // 刻意**不**在 slots 不可用时升成 error：那说明本会话没有 web 运行时（CLI 用法），
  // 不是注册失败。两种情况在 describe().surfaces 里都是结构化可读的。
  // 只数 UI（slot）面：命令面走 ctx.command，它注册成功不能掩盖"四个 UI 面全灭"。
  const isUi = (e: SurfaceReportEntry) => e.id !== SURFACE_IDS.command
  const uiRegistered = surfaceReport.registered.filter(isUi)
  const slotFailures = surfaceReport.failed.filter(isUi)
  if (surfaceReport.slotsAvailable && uiRegistered.length === 0) {
    logger.error(
      'pr-genius: NO SURFACES REGISTERED — the plugin loaded but the host accepted none of the %d ' +
        'UI surfaces. This install will look empty. Tried: %s. ' +
        'Report the host/SDK version and these candidate slots to ' +
        'https://github.com/zsxh1990/pr-genius/issues/102',
      surfaceReport.expected - 1,
      slotFailures.map((f) => `${f.id}[${(f.candidates ?? []).join('|') || 'none'}]`).join(' ') ||
        '(none attempted)',
    )
  } else if (slotFailures.length > 0) {
    logger.warn(
      'pr-genius: %d of %d UI surfaces did not register: %s',
      slotFailures.length,
      surfaceReport.expected - 1,
      slotFailures.map((f) => f.id).join(', '),
    )
  }

  ctx.effect(() => [
    disposeService,
    ...surfaceDisposers,
    () => {
      void service.close()
    },
    () => {
      logger.info('pr-genius unloaded')
    },
  ])

  logger.info(
    'pr-genius loaded: kb=%s mcp=%s/%s locale=%s maintainer=%s',
    kb.root,
    resolved.mcp.transport,
    service.describe().mcp.endpoint,
    resolved.locale,
    String(resolved.maintainer.enabled),
  )
}
