#!/usr/bin/env node
/**
 * 注册层测量：拿**真实 DSH SDK** 声明的 slot catalog，跑 apply()，看四个面落在哪。
 *
 * ── 它测什么、不测什么 ────────────────────────────────────────────────
 * 测：**注册**。apply() 向宿主请求了哪些 slot、宿主接受了哪些、被拒了哪些。
 * 不测：**渲染**。组件是否真的挂上去、React hooks 是否正常、用户看不看得到 ——
 *       那些只有活着的 web 宿主能给（issue #102 正在征集这个）。
 *
 * 为什么需要它：历史上八次「空壳安装」(#86 #90 #95 #97 #98 #100 #101 #117)
 * 每次都靠单测说「已修」——而单测的宿主是**自己造的**。这个脚本的宿主
 * 不是造的：allowed 集合直接取自本机 DSH SDK 自己声明的 CLIENT_SLOT_API，
 * 行为照 DSH guard 的实际语义（未声明的 slot 一律拒绝）。
 *
 * 这不是 #102 的替代品，是它缺的那一半里**不需要真 web 宿主**的那一半。
 *
 * ── 用法 ────────────────────────────────────────────────────────────────
 *   node scripts/measure-surface-registration.mjs
 *   node scripts/measure-surface-registration.mjs --dist <dir>   # 测某个构建产物
 *   node scripts/measure-surface-registration.mjs --sdk <path>   # 指定 SDK 路径
 *
 *   exit 0  四个面都注册上了
 *   exit 2  有面没注册上（宿主拒绝了它声明过的 seat）
 *   exit 3  检查跑不起来（缺 SDK / 缺 dist / 缺 react）
 */
import { existsSync, readFileSync, readdirSync, statSync } from 'node:fs'
import { createRequire } from 'node:module'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const HERE = dirname(fileURLToPath(import.meta.url))
const ROOT = resolve(HERE, '..')

const argv = process.argv.slice(2)
const argOf = (flag) => {
  const i = argv.indexOf(flag)
  return i >= 0 ? argv[i + 1] : undefined
}
const DIST = argOf('--dist') ?? join(ROOT, 'dist')
const SDK = argOf('--sdk')

function fail(code, msg) {
  console.error(`measure-surface-registration: ${msg}`)
  process.exit(code)
}

/** 找本机的 DSH SDK：优先显式指定，其次从 dsh 的全局安装里找 client-runner。 */
function findSdkBundle() {
  if (SDK) return SDK
  const candidates = []
  // nvm 版本目录是动态的，直接扫
  const nvmBase = join(process.env.HOME ?? '', '.nvm/versions/node')
  if (existsSync(nvmBase)) {
    for (const v of readdirSafe(nvmBase)) {
      candidates.push(
        join(
          nvmBase,
          v,
          'lib/node_modules/@deepseek-ai/dsh/node_modules/@deepseek-ai/dsh-cordis-client-runner/lib/client.js',
        ),
      )
    }
  }
  for (const c of candidates) {
    if (existsSync(c) && statSync(c).isFile()) return c
  }
  return undefined
}

function readdirSafe(dir) {
  try {
    return readdirSync(dir)
  } catch {
    return []
  }
}

const sdkBundle = findSdkBundle()
if (!sdkBundle) {
  fail(3, '找不到本机 DSH SDK 的 client-runner bundle。用 --sdk <path> 指定。')
}

/**
 * 从 SDK bundle 里取出它声明的 slot key。
 *
 * client.js 是浏览器 bundle（顶层就 window.__ModuleLoader__），require() 会炸；
 * 所以直接取它的字符串字面量。bundle 里 slot key 形如 'sidebar.footer.action'，
 * 与上游 slot-catalog.ts 的 `key: '…'` 一致。
 */
function sdkSlotKeys(file) {
  const src = readFileSync(file, 'utf8')
  const keys = new Set()
  for (const m of src.matchAll(/'([a-z][A-Za-z0-9._-]{3,})'/g)) keys.add(m[1])
  return keys
}

const SDK_KEYS = sdkSlotKeys(sdkBundle)
if (SDK_KEYS.size === 0) fail(3, `SDK bundle 里没解析出 slot key：${sdkBundle}`)

console.log('=== 权威来源 ===')
console.log(`  SDK bundle : ${sdkBundle}`)
console.log(`  slot keys  : ${SDK_KEYS.size}`)

// 我们关心的四个面各自的候选（与 src/ui/surfaces.ts 的 SURFACE_PLAN 同源）
const SEATS = [
  { id: 'pr-genius.dashboard', candidates: ['sidebar.footer.action'] },
  { id: 'pr-genius.advisor-tab', candidates: ['conversation.view'] },
  {
    id: 'pr-genius.advisor-panel',
    candidates: ['sidebar.right.pane.tab', 'details'],
  },
  { id: 'pr-genius.preferences', candidates: ['settings.section'] },
]

console.log()
console.log('=== 四个面在 SDK 声明里的存在性 ===')
for (const s of SEATS) {
  for (const c of s.candidates) {
    const known = SDK_KEYS.has(c)
    console.log(`  ${known ? '✅' : '❌'} ${c.padEnd(26)} (${s.id})`)
  }
}

const entry = join(DIST, 'index.mjs')
if (!existsSync(entry)) {
  fail(3, `没有构建产物：${entry}（先跑 npm run build）`)
}

// react 必须能解析 —— 否则 import 阶段就 ERR_MODULE_NOT_FOUND（#117 的根因），
// 测出来的是环境问题，不是注册结果。
//
// 解析基准是**被测 dist 所在位置**，不是脚本自己所在的位置：被测的可能是装在
// 别的 profile 里的 pr-genius，它的 react 在那个 profile 的 node_modules 下。
try {
  createRequire(join(DIST, 'index.mjs')).resolve('react')
} catch {
  fail(3, 'react 解析不了 —— 这是环境问题，不是注册结果。先在宿主目录 npm install。')
}

const mod = await import(`file://${entry}`)

// 宿主语义照 DSH guard：只接受 SDK 真正声明的 slot，未声明的一律拒绝并抛错。
const injected = []
const rejected = []
const slots = {
  inject(key, factory) {
    if (!SDK_KEYS.has(key)) {
      rejected.push(key)
      throw new Error(`slot "${key}" is not declared by the host`)
    }
    injected.push(key)
    factory()
    return () => {}
  },
  register() {
    return () => {}
  },
}

const commands = []
const command = (name) => ({
  action(fn) {
    commands.push(name)
    return fn
  },
  option: undefined,
})

const logs = []
const logger = {
  info: (...a) => logs.push(['info', a.join(' ')]),
  warn: (...a) => logs.push(['warn', a.join(' ')]),
  error: (...a) => logs.push(['error', a.join(' ')]),
}

let service = null
const ctx = {
  get(name) {
    if (name === 'slots') return slots
    if (name === 'command') return command
    return undefined
  },
  provide(_name, svc) {
    service = svc
    return () => {}
  },
  effect(fns) {
    if (Array.isArray(fns)) fns.forEach((f) => typeof f === 'function' && f())
    else if (typeof fns === 'function') fns()
  },
  logger: () => logger,
}

mod.apply(ctx, mod.parseConfig({}))

const info = service?.describe?.()
const surfaces = info?.surfaces ?? null

console.log()
console.log('=== apply() 的注册结果 ===')
console.log(`  injected      : ${injected.join(', ') || '(none)'}`)
console.log(`  host rejected : ${rejected.join(', ') || '(none)'}`)
console.log(`  slash command : ${commands.join(', ') || '(none)'}`)
console.log()
if (surfaces) {
  console.log(`  surfaces.expected       : ${surfaces.expected}`)
  console.log(`  surfaces.slotsAvailable : ${surfaces.slotsAvailable}`)
  for (const r of surfaces.registered ?? []) {
    console.log(`    REGISTERED ${r.id} -> ${r.seat}`)
  }
  for (const f of surfaces.failed ?? []) {
    console.log(
      `    FAILED     ${f.id} | ${f.reason ?? ''}` +
        ` | candidates: ${(f.candidates ?? []).join(',') || '-'}` +
        ` | unknownToTable: ${(f.unknownToTable ?? []).join(',') || '-'}` +
        ` | hostRefused: ${(f.hostRefused ?? []).join(',') || '-'}`,
    )
  }
}

const errors = logs.filter((l) => l[0] === 'error')
const warns = logs.filter((l) => l[0] === 'warn')
console.log()
console.log('=== 日志 ===')
console.log(`  errors: ${errors.length}`)
for (const e of errors) console.log(`    ERROR> ${e[1]}`)
console.log(`  warns : ${warns.length}`)
for (const w of warns) console.log(`    warn > ${w[1]}`)

const uiRegistered = (surfaces?.registered ?? []).filter((r) => r.id !== 'pr-genius')
const ok = uiRegistered.length === SEATS.length && errors.length === 0

console.log()
console.log('=== 结论 ===')
console.log(
  ok
    ? `注册层通过：${uiRegistered.length}/${SEATS.length} 个 UI 面在真实 SDK catalog 下注册成功。`
    : `注册层不通过：${uiRegistered.length}/${SEATS.length} 个 UI 面注册成功。`,
)
console.log(
  '这**不是**渲染证据。组件是否挂上、React hooks 是否正常、用户看不看得到，' +
    '仍需活的 web 宿主（issue #102）。',
)
process.exit(ok ? 0 : 2)
