#!/usr/bin/env node
/**
 * 渲染层测量：把四个面的组件**真的渲染成 HTML**，看有没有内容。
 *
 * ── 为什么要有这个脚本 ────────────────────────────────────────────────
 * issue #98 的教训：那次四个面里只有 Preferences 渲染，另三个因为
 * 「两个 React 实例」抛 `Invalid hook call` 而空白，而**单测是绿的**——
 * 因为单测只查 `slots.register` 的参数，没有真的 mount 组件。
 *
 * `renderToStaticMarkup` 是这里能做到的最接近真渲染的一步：它真的跑
 * hooks、真的执行组件体、真的产出 HTML。少了它，四个面「注册成功」
 * 只能说明宿主接受了这四个 key，说明不了任何关于用户看到什么的事。
 *
 * 它**仍然不是**真 web 宿主：没有 layout、没有 CSS、没有事件、没有
 * 宿主自己的 React。issue #102 征集的仍是那件事。
 *
 * ── 用法 ────────────────────────────────────────────────────────────────
 *   node scripts/measure-surface-rendering.mjs
 *   node scripts/measure-surface-rendering.mjs --dist <dir>
 *
 *   exit 0  四个面都渲染出了非空 HTML
 *   exit 2  有面渲染为空（真正的空壳）
 *   exit 3  检查跑不起来（缺依赖）
 */
import { existsSync, readFileSync, readdirSync, statSync } from 'node:fs'
import { createRequire } from 'node:module'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const HERE = dirname(fileURLToPath(import.meta.url))
const ROOT = resolve(HERE, '..')
const argv = process.argv.slice(2)
const argOf = (f) => {
  const i = argv.indexOf(f)
  return i >= 0 ? argv[i + 1] : undefined
}
const DIST = argOf('--dist') ?? join(ROOT, 'dist')

function fail(code, msg) {
  console.error(`measure-surface-rendering: ${msg}`)
  process.exit(code)
}

const entry = join(DIST, 'index.mjs')
if (!existsSync(entry)) fail(3, `没有构建产物：${entry}（先 npm run build）`)

// react / react-dom 必须从**被测 dist 所在位置**解析：被测的可能是装在别的
// profile 里的 pr-genius，它的 react 在那个 profile 的 node_modules 下。
const req = createRequire(join(DIST, 'index.mjs'))
let React, renderToStaticMarkup
try {
  React = req('react')
  ;({ renderToStaticMarkup } = req('react-dom/server'))
} catch (e) {
  fail(3, `react / react-dom 解析不了 —— 环境问题，不是渲染结果：${e.message.split('\n')[0]}`)
}

const mod = await import(`file://${entry}`)

// ── 一个够用的假 service：组件只需要 callTool 与 describe ──────────────
const calls = []
const service = {
  config: {},
  kb: { root: '/tmp/kb' },
  describe: () => ({
    name: 'pr-genius',
    version: 'test',
    kbRoot: '/tmp/kb',
    mcp: { transport: 'stdio', endpoint: 'python3 -m prgenius mcp serve', timeoutMs: 30000, protocolVersion: 'x' },
    sidebar: { defaultView: 'dashboard' },
    maintainer: { enabled: false, actions: [], confidenceMin: 0, staleDays: 30 },
    locale: 'en',
    riskFilter: 'low_risk',
    surfaces: null,
  }),
  callTool: async (tool, args) => {
    calls.push({ tool, args })
    if (tool === 'prgenius_doctor') {
      return {
        ok: true,
        knowledge_base: {
          repo_root: '/tmp/kb',
          readable: true,
          anti_patterns: 61,
          success_patterns: 692,
          profiles: 68,
          case_studies: 302,
          policies: 5,
        },
        warnings: [],
      }
    }
    if (tool === 'list_cases' || tool === 'get_case_study') return []
    if (tool === 'search_patterns') return []
    if (tool === 'list_open_prs') return []
    if (tool === 'status_prs') return []
    return {}
  },
  close: async () => {},
}

const face = {
  service,
  locale: 'en',
  workMode: 'contributor',
  riskFilter: 'low_risk',
}

// 组件不在公开 API 里，但 dist 里有 surfaceComponents 的产物。
// 用 src 里的导出面拿不到 —— 所以从 bundle 里找。
const bundle = readFileSync(entry, 'utf8')
if (!bundle.includes('surfaceComponents') && !bundle.includes('advisor-panel')) {
  fail(3, 'bundle 里找不到 surfaceComponents —— 这个脚本认不出组件表。')
}

console.log('=== 权威来源 ===')
console.log(`  dist : ${entry}`)
console.log(`  react: ${React.version}`)

console.log()
console.log('=== 渲染四个面 ===')

// 用一个能列出所有已注册组件的方式：通过 apply() 捕获 slots.register 的组件。
const components = new Map()
const injected = []
const slots = {
  inject(key, factory) {
    injected.push(key)
    factory()
    return () => {}
  },
  register(def, component) {
    components.set(def?.id ?? def?.name ?? `unknown-${components.size}`, component)
    return () => {}
  },
}
const command = (name) => ({ action: (fn) => fn, option: undefined })
const logs = []
const logger = {
  info: () => {},
  warn: (...a) => logs.push(['warn', a.join(' ')]),
  error: (...a) => logs.push(['error', a.join(' ')]),
}
let svc = null
const ctx = {
  get: (n) => (n === 'slots' ? slots : n === 'command' ? command : undefined),
  provide: (_n, s) => {
    svc = s
    return () => {}
  },
  effect: (fns) => {
    if (Array.isArray(fns)) fns.forEach((f) => typeof f === 'function' && f())
    else if (typeof fns === 'function') fns()
  },
  logger: () => logger,
}

mod.apply(ctx, mod.parseConfig({}))

const results = []
for (const [id, component] of components) {
  if (typeof component !== 'function') {
    results.push({ id, ok: false, why: `组件不是函数（${typeof component}）` })
    continue
  }
  try {
    const html = renderToStaticMarkup(React.createElement(component, face))
    const text = html.replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim()
    results.push({
      id,
      ok: html.length > 0 && text.length > 0,
      htmlLen: html.length,
      textLen: text.length,
      sample: text.slice(0, 160),
      error: null,
    })
  } catch (e) {
    results.push({ id, ok: false, why: String(e?.message ?? e).split('\n')[0] })
  }
}

for (const r of results) {
  const mark = r.ok ? '✅' : '❌'
  console.log(`  ${mark} ${r.id}`)
  if (r.ok) {
    console.log(`       html ${r.htmlLen} chars / text ${r.textLen} chars`)
    console.log(`       「${r.sample}」`)
  } else {
    console.log(`       ${r.why}`)
  }
}

const errors = logs.filter((l) => l[0] === 'error')
const warns = logs.filter((l) => l[0] === 'warn')
console.log()
console.log('=== apply() 期间的日志 ===')
console.log(`  errors: ${errors.length}`)
for (const e of errors) console.log(`    ERROR> ${e[1]}`)
console.log(`  warns : ${warns.length}`)
for (const w of warns) console.log(`    warn > ${w[1]}`)

const rendered = results.filter((r) => r.ok).length
console.log()
console.log('=== 结论 ===')
console.log(`  ${rendered}/${results.length} 个面渲染出了非空 HTML。`)
if (rendered < results.length) {
  console.log('  上面标 ❌ 的面在真宿主里就是空白的 —— 这就是「空壳安装」。')
}
console.log(
  '  这仍不是真 web 宿主：没有 layout / CSS / 事件，也没有宿主自己的 React。' +
    'issue #102 征集的是那件事。',
)
process.exit(rendered === results.length && results.length > 0 ? 0 : 2)
