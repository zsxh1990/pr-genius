/**
 * pr-genius — DSH (Cordis) 插件，**宿主（node）半边**（issue #159）。
 *
 * 契约（dsh plugin add pr-genius 后由 ctx.use 实例化为带生命周期的 fiber）：
 *   - name / Config(schema) / inject / apply
 *   - 加载即生效、卸载即还原：apply() 里注册的都是 effect，框架卸载时自动清理。
 *
 * 架构：TS 只是壳与投影 —— 直读知识库静态数据文件，分析一律调用现有 Python
 * FastMCP 服务 (prgenius/src/prgenius/mcp.py)。绝不重写分析逻辑。
 *
 * 两半拆分（issue #159）：注册与投影的共用逻辑在 `plugin-core.ts`，本文件只负责
 * **node 侧的运行时能力** —— 从磁盘解析知识库布局、拉起 MCP 子进程。浏览器侧
 * 同样的 `apply` 由 `src/client/index.ts` 提供，两边注入不同的 `PluginRuntime`。
 *
 * 诚实边界：插件曾在真 DSH 宿主跑过（issue #100/#101/#103 即真机暴露）；本机没有
 * DEEPSEEK_API_KEY，2.1.5 起的修复未经真机复验。本文件只保证 TypeScript
 * 编译、单元测试与静态契约自洽；渲染与运行时行为需 DSH 运行时验证，本机未执行。
 */
import type { Context } from '@deepseek-ai/cordis'
import {
  Config,
  PrGeniusConfigError,
  parseConfig,
  type ContributorAction,
  type MaintainerAction,
  type RiskTier,
} from './config.ts'
import { defaultKbRoot, readPackageMeta, resolveKbRoot } from './kb.ts'
import { createMcpInvoker } from './mcp-client.ts'
import { applyWith, name, resolveLogger } from './plugin-core.ts'

export { name } from './plugin-core.ts'

export { Config, PrGeniusConfigError, parseConfig }
export type { Config as ConfigType, ContributorAction, MaintainerAction, RiskTier }

/**
 * `inject` 必须保持为空 —— 不是省事，是硬约束。
 *
 * 权威依据：cordis `Plugin.Base.inject`
 * （node_modules/@deepseek-ai/cordis/lib/types/registry.d.ts）：
 *   "Services the plugin requires; **it only loads while all are available**."
 * 即写进 inject 的名字是**加载门**：缺一个，插件整个不加载。把 `slots` / `command`
 * 写进去，等于把「界面缺失」升级成「插件不可用」—— 正是现有注释警告过的回归。
 *
 * 可选的 UI 席位改经 `ctx.get(name)` 读取（见 plugin-core.ts 里的 optionalService）：
 * 那条路径**不需要 inject 声明**（cordis ReflectService.get 的 docstring：
 * "Read a service from the store without the inject requirement."）。
 * 本插件也不依赖任何宿主服务：分析走自带的 MCP 客户端、知识库是静态文件。
 */
export const inject: string[] = []

/** 本插件向宿主提供的服务名，其他插件/UI 可通过 inject: ['prGenius'] 使用。 */
export const provide = 'prGenius'

// 共用核心的对外形状 —— 测试与下游经本模块（宿主半边）读它们。
export {
  createPrGeniusService,
  type PrGeniusRuntimeInfo,
  type PrGeniusService,
  type PrGeniusServiceDeps,
  type SurfaceReport,
  type SurfaceReportEntry,
} from './plugin-core.ts'

/**
 * 宿主半边的 `apply`：把 node 侧能力备齐，再交给共用核心。
 *
 * 配置非法 → 抛 PrGeniusConfigError（字段路径见 message），加载即失败，不带病运行。
 * kbRoot 布局缺失 → 同样抛错，响亮失败。
 */
export function apply(ctx: Context, config: Config): void {
  // 防御性再校验：框架已按 schema 校验过，这里保证直接调用 apply() 时同样响亮。
  const resolved = parseConfig(config)
  // 不裸读 ctx.logger —— guard facade 上 logger 不在 CTX_VERBS，直读会 denyRead 抛错。
  // 见 resolveLogger 的注释（含为什么 inject/logger 和 ctx.get/logger 都不通）。
  const logger = resolveLogger(ctx, 'pr-genius')
  const kb = resolveKbRoot(resolved.kbRoot)
  const meta = readPackageMeta(defaultKbRoot())
  const invoker = createMcpInvoker(
    {
      transport: resolved.mcp.transport,
      command: resolved.mcp.command,
      args: resolved.mcp.args,
      url: resolved.mcp.url,
      timeoutMs: resolved.mcp.timeoutMs,
      protocolVersion: resolved.mcp.protocolVersion,
      clientName: name,
      clientVersion: meta.version,
    },
    (line) => logger.warn('[mcp:stderr] %s', line),
  )
  applyWith(ctx, config, { kb, version: meta.version, invoker })
}
