/**
 * pr-genius — DSH (Cordis) 插件，**浏览器（client）半边**（issue #159）。
 *
 * 这个文件存在的唯一理由：`package.json` 声明了 `dsh.client`（`platform: "web"`）
 * 却没有 `exports["./client"]`，于是 DSH 的 `client-modules` **静默**把插件从
 * client graph 里丢掉 —— 67 条 boot manifest 里没有我们，四个面从未被挂载过。
 * 那是八次「空壳安装」（#86 #90 #95 #97 #98 #100 #101 #117）的共同根因，
 * 而且它比崩更糟：崩至少有日志，缺席是安静的。
 *
 * ## 导出形状是 DSH 的契约，不是我们随口定的
 *
 * `@deepseek-ai/dsh-cordis-client-runner` 的 `guardedSurface()`：
 *   - 模块是函数 → `apply: (ctx) => plugin(guarded(ctx))`
 *   - 模块是对象 → `{ ...plugin, apply: (ctx, config) => plugin.apply(guarded(ctx), config) }`
 *     并且「The plugin's OWN `inject` survives」—— `inject` 是服务声明，也是加载门。
 * 参考 DSH 自己的 `dsh-client-ui-cordis/lib/client.js`：`exports.apply` + `exports.inject`。
 *
 * 打包形态见 `tsdown.config.ts`：**CJS 包进 `window.__ModuleLoader__.load({id, factory})`**，
 * 不是标准 IIFE 也不是裸 ESM。
 *
 * ## 这一半现在能做什么、不能做什么
 *
 * 能：**让插件出现在 web 宿主里**，并把四个面注册上去（issue #159 验收判据 1-2 的前置）。
 * 不能：跑分析。分析引擎在 Python 侧，宿主半边经 node 子进程调它；浏览器侧要改走
 * DSH 的 `@deepseek-ai/dsh-client-connection`（它已经在 `dsh.client.inject` 里）。
 * 那是后续工作。**现在 `callTool` 会返回一个明确的失败，而不是崩、也不是静默。**
 */
import type { Context } from '@deepseek-ai/cordis'
import { Config, PrGeniusConfigError, parseConfig } from '../config.ts'
import { applyWith, name, type PluginRuntime } from '../plugin-core.ts'
import type { KbLayout } from '../kb.ts'
import type { McpInvoker } from '../mcp-client.ts'

/** 构建期由 tsdown `define` 注入；取不到时诚实说 unknown，不猜一个版本号。 */
declare const __PRGENIUS_VERSION__: string | undefined

export { name, Config, PrGeniusConfigError, parseConfig }
export type { Config as ConfigType }

/**
 * 与宿主半边同一个 `inject` 空数组，理由相同：写进去的名字是加载门，
 * 缺一个整个插件不加载，会把「界面缺失」升级成「插件不可用」。
 */
export const inject: string[] = []

/** 向宿主提供的服务名。 */
export const provide = 'prGenius'

export {
  createPrGeniusService,
  type PrGeniusRuntimeInfo,
  type PrGeniusService,
  type PrGeniusServiceDeps,
  type SurfaceReport,
  type SurfaceReportEntry,
} from '../plugin-core.ts'

/**
 * 浏览器侧的知识库布局。
 *
 * 知识库是**磁盘上的静态文件**，浏览器读不到。这里不假装有 —— `root` 写明
 * 「在宿主半边」，`describe()` 会原样透出，UI 与诊断都能看见它是不可用的，
 * 而不是看到一个不存在的路径。
 */
const browserKb: KbLayout = {
  root: '(browser half — the knowledge bundle lives on the host half)',
  antiPatterns: '(unavailable in the browser)',
  successPatterns: '(unavailable in the browser)',
  profiles: '(unavailable in the browser)',
  policies: '(unavailable in the browser)',
}

/**
 * 浏览器侧的 MCP 通道。
 *
 * 分析引擎是 Python FastMCP 服务，宿主半边经 node 子进程调它。浏览器侧的正解是
 * 走 `@deepseek-ai/dsh-client-connection`（已在 `dsh.client.inject` 里），那是后续
 * 工作（issue #159 验收判据 3-4）。
 *
 * 在那之前：**返回明确的失败**。不抛（那会让 apply() 半途崩、四个面一个都注册不上），
 * 也不返回假数据（那正是「空壳安装」的另一种形态）。
 */
const browserInvoker: McpInvoker = {
  callTool: async (tool: string) => {
    throw new Error(
      `pr-genius (browser half): tool "${tool}" needs the analysis engine, which runs on ` +
        'the host half via a node child process. The browser transport ' +
        '(@deepseek-ai/dsh-client-connection) is not wired up yet — see issue #159.',
    )
  },
  close: async () => {},
}

function browserVersion(): string {
  try {
    return typeof __PRGENIUS_VERSION__ === 'string' ? __PRGENIUS_VERSION__ : 'unknown'
  } catch {
    return 'unknown'
  }
}

/**
 * client 半边的 `apply` —— 形状与宿主半边一致，只是注入的运行时不同。
 *
 * 注册失败仍然按「宁缺勿假」处理，且 `describe().surfaces` 结构化透出结果，
 * 所以「装上了但四个面一个没落座」和「装上了且落座了」在 web 宿主里分得开。
 */
export function apply(ctx: Context, config: Config): void {
  // 配置校验两半一致：非法配置响亮失败，不带病运行。
  parseConfig(config)
  const runtime: PluginRuntime = {
    kb: browserKb,
    version: browserVersion(),
    invoker: browserInvoker,
  }
  applyWith(ctx, config, runtime)
}
