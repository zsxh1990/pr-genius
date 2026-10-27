import { defineConfig } from 'tsdown'

/**
 * 宿主提供的包**必须** external，不能打进 bundle（issue #101）。
 *
 * DSH web 宿主自带 React / Cordis / slots API。若把 React 内联进
 * dist/index.mjs，宿主里的组件会同时存在两份 React —— `useState` 那套
 * hooks 依赖「同一个 React 的 dispatcher」，两份实例会让 3/4 个侧边栏界面
 * 在带自己 React 的宿主上直接抛 "Invalid hook call"。
 *
 * 判据：只要那个包在插件加载时由宿主解析，就 external。
 *   - react / react-dom —— 宿主渲染层
 *   - cordis —— 宿主容器
 *
 * 注意 **不能** 一刀切 external 掉 `@deepseek-ai/*`：源码里唯一运行时的
 * `@deepseek-ai` import 是 `@deepseek-ai/schemastery`，而它只是 devDependency
 * （`dependencies` 里放的是公开的 `schemastery`）。把它设成 external 会让
 * 解包产物 `Cannot find package '@deepseek-ai/schemastery'`，apply() 直接崩
 * —— smoke gate 曾因此 4 个 FAIL。它必须打进 bundle。
 * 另外两个 `@deepseek-ai/*`（cordis、dsh-client-ui-slots）是 type-only，
 * 不进运行时，不需要列。
 *
 * node: 内建模块由 target 处理，不列在这里。
 */

import { createRequire } from 'node:module'
import type { UserConfig } from 'tsdown'

const CLIENT_ID = 'pr-genius'

/** DSH client bundle 的外壳 —— 与 dsh-client-ui-cordis/lib/client.js 同形。 */
const CLIENT_BANNER = `window.__ModuleLoader__.load({
\tid: "${CLIENT_ID}",
\tfactory: (require) => {
\t\tvar module = { exports: {} };
\t\tvar exports = module.exports;
`

const CLIENT_FOOTER = `
\t\treturn module.exports;
\t}
});`

function pkgVersion(): string {
  const require = createRequire(import.meta.url)
  return String(require('./package.json').version)
}

const hostConfig: UserConfig = {
  entry: ['src/index.ts', 'src/config.ts', 'src/kb.ts', 'src/mcp-client.ts', 'src/ui/surfaces.ts'],
  format: ['esm'],
  target: 'node22',
  dts: true,
  clean: true,
  external: [
    'react',
    'react-dom',
    'react/jsx-runtime',
    'react-dom/server',
    'cordis',
    'schemastery',
  ],
}

/**
 * client 半边（issue #159）—— 与宿主半边**分开构建**，因为形态完全不同。
 *
 * 输出**不是**标准 IIFE、也**不是**裸 ESM：DSH 的 client bundle 是
 * `window.__ModuleLoader__.load({ id, factory })`，factory 内部是 CJS ——
 * `var module = { exports: {} }` / 外部依赖走 `require()` / `return module.exports`。
 * 权威依据是 DSH 自己的 `@deepseek-ai/dsh-client-ui-cordis/lib/client.js`。
 *
 * 外部依赖同样必须 external（同 issue #101 的理由）：react / cordis 由宿主提供，
 * 打进 bundle 会产生两份 React、`Invalid hook call`。
 *
 * `clean: false` —— 两个 config 共用 `dist/`，第二个清盘会把第一个的产物擦掉。
 */
const clientConfig: UserConfig = {
  entry: { client: 'src/client/index.ts' },
  format: ['cjs'],
  target: 'es2022',
  platform: 'browser',
  dts: false,
  clean: false,
  define: {
    __PRGENIUS_VERSION__: JSON.stringify(pkgVersion()),
  },
  external: [
    'react',
    'react-dom',
    'react/jsx-runtime',
    'react-dom/server',
    'cordis',
    'schemastery',
    '@deepseek-ai/cordis',
    '@deepseek-ai/dsh-client-ui-slots',
    '@deepseek-ai/dsh-client-connection',
    '@deepseek-ai/dsh-client-locale',
    '@deepseek-ai/dsh-client-ui-conversation',
    '@deepseek-ai/dsh-client-ui-settings',
    '@deepseek-ai/dsh-client-ui-sidebar-right',
  ],
  outputOptions: {
    // 外部依赖在 factory 里走 require()，与 DSH 的 client bundle 一致。
    externalLiveBindings: false,
  },
  banner: () => CLIENT_BANNER,
  footer: () => CLIENT_FOOTER,
}

export default defineConfig([hostConfig, clientConfig])
