#!/usr/bin/env node
/**
 * 发版运行时 smoke gate（issue #96）。
 *
 * ── 它要挡什么 ──────────────────────────────────────────────────────────
 * v2.0.0 / v2.1.0 / v2.1.1 三次发版，CHANGELOG 都写了「四个界面挂在真实 slot 上」，
 * 三次都是假的：slot 名是照教程散文臆造的、组件是 null、客户端组件压根没进 bundle。
 * 三次的共同根因是**发版前从不跑运行时**——只跑 tsc + 单测 + grep dist。
 * tsc 是语法检查，grep 只能证明「文件里有」，证明不了「apply() 会这么调」。
 *
 * ── 它怎么验（走用户实际执行的路径，不是「文件里有」）──────────────────
 *   1. `npm pack` → 解压真实 tarball（把 `files` 白名单也一并验了）
 *   2. `import()` **解压出来的** `dist/index.mjs`（不是 src，不是工作树里的 dist）
 *   3. 真的调 `apply(ctx, config)`，录下它每一次 `slots.inject` / `slots.register`
 *   4. 拿录到的 slot key 去比**权威 slot catalog**（DSH SDK 自己声明的那张表）
 *   5. 组件不得为 null / undefined / 非函数
 *   6. register 选项必须满足该 slot 基数（cardinality）的 required 项
 *   7. 再跑一遍「没有 slots 服务的宿主」，确认 apply() 保守降级（不注册、记 warn），
 *      而不是崩掉或者假装注册成功
 *   8. 再跑一遍 denyRead 语义的宿主（真 guard 的复刻：直读未声明名抛、Reflect.has
 *      恒 false、ctx.get 可选查找），确认 apply() 仍能注册四个界面 —— 这一条专治
 *      「gate 看绿、真宿主空白」：旧 mock 把 slots 当字面量属性，绕开了 guard。
 *
 * ── 反循环纪律：slot 列表从哪来？───────────────────────────────────────
 * **不是代码里写死的。** 来自 `scripts/release-smoke/slot-catalog.mjs`，它去取
 * DSH SDK 自己的 `CLIENT_SLOT_API`（= 源码
 * `packages/extensions/cordis-client-runner/src/client/slot-catalog.ts` 的编译产物，
 * 优先取 package.json 钉住的已安装 SDK 包，其次 `gh api` 取上游源码交叉校验）。
 * 两个来源都取不到 ⇒ 本 gate 报「权威 catalog 不可得，无法验证」并以非 0 退出，
 * **绝不退回内置列表**。内置列表 = 自己出题自己批卷：只能确认错误，无法证伪。
 *
 * ── 诚实边界 ────────────────────────────────────────────────────────────
 * 本 gate 验的是「apply() 发出的调用落在 SDK 声明的座位上、组件不是 null」，
 * **不是**「渲染出来了」。真 DSH web 宿主要 DEEPSEEK_API_KEY，本机没有，
 * 插件曾在真宿主里加载过（issue #100/#101/#103 即真机暴露），但**本 gate 验的是
 * 这份 tarball 的调用形状**，不是真宿主渲染。渲染正确性不在本 gate 的证明范围内。
 * 同理，这里调的 `apply()` 来自 tarball 里的产物，宿主是记录器不是真 Cordis
 * web 宿主——它按 apply() 实际触碰的 Context 面（logger/provide/effect/command/slots）
 * 构造，多出来的行为不会被观察到。
 *
 * 退出码：0 = 声明站得住；1 = 站不住（有 FAIL）；2 = 无法验证（权威 catalog 不可得）。
 */
import { execFileSync, execSync } from 'node:child_process'
import { createRequire } from 'node:module'
import { mkdirSync, mkdtempSync, readFileSync, writeFileSync, existsSync, rmSync, readdirSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve as resolvePath } from 'node:path'
import { pathToFileURL } from 'node:url'
import { loadSlotCatalog, diffCatalogs, assertNoHardcodedSlotKeys, UPSTREAM } from './slot-catalog.mjs'

// ── CLI ───────────────────────────────────────────────────────────────────
const argv = process.argv.slice(2)
function flag(name) {
  return argv.includes(name)
}
function opt(name, dflt = null) {
  const i = argv.indexOf(name)
  return i >= 0 && argv[i + 1] ? argv[i + 1] : dflt
}
const REPO_ROOT = resolvePath(opt('--repo', process.cwd()))
const CATALOG_SOURCE = opt('--catalog', 'auto')
const CATALOG_FILE = opt('--catalog-file', null)
const JSON_OUT = resolvePath(opt('--json', join(REPO_ROOT, 'reports', 'release-smoke.json')))
const KEEP_WORK = flag('--keep-work')
const FORCE_BUILD = flag('--build')
const SKIP_PACK = flag('--skip-pack')

// ── 记录器宿主 ────────────────────────────────────────────────────────────
/**
 * 按 apply() 实际触碰的 Context 面构造的记录器。
 * 不假设 slot 名、不假设 opts 形状——原样录下，判定交给 catalog。
 */
function makeRecordingHost({ withSlots }) {
  const log = []
  const calls = { inject: [], register: [], provide: [], effect: [], command: [], warn: [], info: [], error: [] }
  const logger = {
    info: (...a) => calls.info.push(a.map(String).join(' ')),
    warn: (...a) => calls.warn.push(a.map(String).join(' ')),
    error: (...a) => calls.error.push(a.map(String).join(' ')),
    debug: () => {},
    trace: () => {},
  }
  const ctx = {
    logger: () => logger,
    provide: (name, service) => {
      calls.provide.push({ name, serviceType: typeof service })
      return () => calls.provide.push({ disposed: name })
    },
    effect: (fn) => {
      const out = typeof fn === 'function' ? fn() : undefined
      calls.effect.push({ returnedDisposers: Array.isArray(out) ? out.length : 0 })
    },
  }
  if (withSlots) {
    ctx.slots = {
      inject: (slot, factory) => {
        const rec = { slot, factoryCalled: false, registers: [] }
        calls.inject.push(rec)
        // 真实 slots 服务会立即调 factory 让 registrant 完成 register——照做。
        try {
          const out = typeof factory === 'function' ? factory() : undefined
          rec.factoryCalled = true
          rec.factoryReturn = out === undefined ? 'undefined' : typeof out
        } catch (err) {
          rec.factoryThrew = String(err && err.message ? err.message : err)
        }
        return () => {
          rec.disposed = true
        }
      },
      register: (opts, component) => {
        const rec = {
          opts: opts === null ? null : typeof opts === 'object' ? JSON.parse(JSON.stringify(opts, (k, v) => (typeof v === 'function' ? '[function]' : v))) : String(opts),
          componentType: component === null ? 'null' : component === undefined ? 'undefined' : typeof component,
          componentIsNull: component === null || component === undefined,
        }
        // 归到最近一次 inject 的 rec 上，便于按 surface 对账。
        const last = calls.inject[calls.inject.length - 1]
        if (last) last.registers.push(rec)
        calls.register.push(rec)
        return () => {
          rec.disposed = true
        }
      },
    }
  }
  return { ctx, calls, log }
}

/**
 * denyRead 语义的宿主 —— 专治「gate 看绿、真宿主是坏的」。
 *
 * 旧 mock 把 `slots` 当字面量属性挂在 ctx 上，`Reflect.has` 恒真、直读恒通，
 * 绕开真宿主的 guard。真宿主里 apply() 收到 dynamicCordisContext 的白名单 facade
 * （node_modules/@deepseek-ai/dsh-cordis-client-runner/lib/client.js）：
 * 直读未声明名 → denyRead **抛**；`Reflect.has` 恒 false；`ctx.get` 是可选查找。
 * 这里逐条复刻那三条，让「重新引入 Reflect.has + 直读探测」在发版门禁里立刻红。
 * 与 test/fixtures/guarded-context.ts 是同一语义的两份实现（那边 TypeScript 给
 * vitest 用，这边 JS 给 gate 用 —— gate 只测 tarball 产物，不能 import src/）。
 *
 * 诚实边界：真 guard 的 CTX_VERBS 不含 logger（client.js 205-216 行，upstream
 * guard.ts 22-24 同），LoggerService 也不在 service store —— 所以这里**不**放行
 * logger，与真 guard 一致。插件自己用 resolveLogger() 分流（Reflect.has 为真才
 * 直读，否则 console 兜底），因此 apply() 跑得完。日志经 console 兜底，gate
 * 在受控 console 上截获它们，而不是假装 facade 有 logger。
 */
function makeGuardedHost({ services = {} } = {}) {
  const declared = new Set([]) // 本插件 inject: []
  const getLog = []
  const serviceTable = services // 活引用：构造后仍可填（slots 服务要记账到 calls）
  const calls = { inject: [], register: [], provide: [], effect: [], warn: [], info: [], error: [] }
  const logger = {
    info: (...a) => calls.info.push(a.map(String).join(' ')),
    warn: (...a) => calls.warn.push(a.map(String).join(' ')),
    error: (...a) => calls.error.push(a.map(String).join(' ')),
    debug: () => {},
    trace: () => {},
  }
  const denyRead = (prop, present) => {
    if (present) {
      throw new Error(
        `service "${prop}" is not declared by your plugin. Declare it on the plugin you return: ` +
          `{ inject: ['${prop}', …], apply(ctx) { … } } — a plain \`function\` has no ` +
          'declaration site, so use the object form. The runtime then parks the package ' +
          'if the provider unloads.',
      )
    }
    throw new Error(
      `dynamic ctx does not expose "${prop}". Available: ctx.on / ctx.provide / timer ` +
        'helpers after injecting timer, and any service your returned plugin declared in ' +
        'inject (slots and theme are the usual UI seats). Framework internals are withheld ' +
        'by design.',
    )
  }
  const readService = (name, requireDeclaration) => {
    if (requireDeclaration && !declared.has(name)) denyRead(name, name in serviceTable)
    return serviceTable[name]
  }
  const target = {
    // 不放 logger：真 guard 的 CTX_VERBS 里没有它。apply() 会经 resolveLogger
    // 降级到 console 兜底，gate 用 withCapturedConsole 收日志。
    provide: (name, service) => {
      calls.provide.push({ name, serviceType: typeof service })
      return () => calls.provide.push({ disposed: name })
    },
    effect: (fn) => {
      const out = typeof fn === 'function' ? fn() : undefined
      calls.effect.push({ returnedDisposers: Array.isArray(out) ? out.length : 0 })
    },
  }
  const ctx = new Proxy(target, {
    get(t, prop, receiver) {
      if (prop === 'get') {
        return (name) => {
          getLog.push(name)
          return readService(name, false)
        }
      }
      if (typeof prop !== 'string') return Reflect.get(t, prop, receiver)
      if (prop in t) return Reflect.get(t, prop, receiver)
      return readService(prop, true) // 未声明名 → denyRead 抛
    },
    has(_t, prop) {
      return prop === 'get' || (typeof prop === 'string' && (prop in target || declared.has(prop)))
    },
    set() {
      throw new Error('dynamic ctx is read-only')
    },
  })
  return { ctx, calls, getLog, services: serviceTable }
}

/** 跑一次 apply()，返回录到的调用。 */
async function runApply(artifactUrl, host) {
  const mod = await import(artifactUrl)
  if (typeof mod.apply !== 'function') {
    throw new Error(`产物没有导出 apply() —— 导出面: ${Object.keys(mod).join(', ')}`)
  }
  const exportsBefore = Object.keys(mod).sort()
  // 用默认配置；配置非法会抛，那本身就是 gate 要报的失败。
  const { parseConfig } = mod
  const config = typeof parseConfig === 'function' ? parseConfig({}) : {}
  mod.apply(host.ctx, config)
  return { mod, exportsBefore }
}

// ── 判定 ──────────────────────────────────────────────────────────────────
function makeFinding(id, severity, title, detail, evidence) {
  return { id, severity, title, detail, evidence: evidence ?? null }
}

function validate({ calls, catalog, injectDeclared, runLabel }) {
  const findings = []
  const entryOf = (k) => catalog.entries.find((e) => e.key === k) ?? null

  // C1 —— slot key 必须在权威 catalog 里
  for (const rec of calls.inject) {
    const entry = entryOf(rec.slot)
    if (!entry) {
      findings.push(makeFinding(
        'C1.slot-key-not-in-catalog',
        'FAIL',
        `slot key 不在权威 catalog 内：${rec.slot}`,
        `apply() 向 ctx.slots.inject('${rec.slot}', ...) 注册，但 DSH SDK 的 CLIENT_SLOT_API（${catalog.entries.length} 个 key）里没有它。` +
          `这不是「可能拼错」——宿主没有这个座位，注册等于什么都没发生。`,
        { run: runLabel, slot: rec.slot, catalogSource: catalog.provenance, catalogSize: catalog.entries.length },
      ))
    }
  }

  // C2 —— 组件不得为 null / undefined / 非函数
  for (const rec of calls.register) {
    if (rec.componentIsNull || (rec.componentType !== 'function' && rec.componentType !== 'object')) {
      findings.push(makeFinding(
        'C2.null-component',
        'FAIL',
        `register() 的组件不是可用组件：${rec.componentType}`,
        `占了座位却不渲染——正是 v2.0.0/v2.1.0 那个「侧边栏空白」的形状。组件必须是函数或 React 元素工厂。`,
        { run: runLabel, opts: rec.opts, componentType: rec.componentType },
      ))
    }
  }

  // C3 —— inject 声明与可达性
  if (injectDeclared.length > 0 && !injectDeclared.includes('slots')) {
    findings.push(makeFinding(
      'C3.inject-mismatch',
      'FAIL',
      `插件 inject 声明了 ${JSON.stringify(injectDeclared)}，但没有 'slots'`,
      `声明了要注入却不要 slots，却仍然去调 ctx.slots.* —— 契约自相矛盾。`,
      { run: runLabel, inject: injectDeclared },
    ))
  }

  // C4 —— register 选项必须满足该 slot 基数的 required 项
  for (const rec of calls.inject) {
    const entry = entryOf(rec.slot)
    if (!entry) continue
    const required = entry.registerOptions.filter((o) => o.requirement === 'required').map((o) => o.name)
    for (const reg of rec.registers) {
      const opts = reg.opts && typeof reg.opts === 'object' ? reg.opts : {}
      const missing = required.filter((r) => !(r in opts) || opts[r] === undefined || opts[r] === null)
      if (missing.length > 0) {
        findings.push(makeFinding(
          'C4.missing-required-register-option',
          'FAIL',
          `slot '${rec.slot}'（${entry.kind}）注册时缺 required 选项：${missing.join(', ')}`,
          `SDK 为该基数规定 register 必传 ${required.join(', ') || '（无）'}；实际传的是 ${JSON.stringify(opts)}。` +
            `缺 required 项的注册调用在真宿主里不会落到预期的座位上。`,
          {
            run: runLabel,
            slot: rec.slot,
            kind: entry.kind,
            scope: entry.scope,
            required,
            passed: opts,
            missing,
          },
        ))
      }
      // 基数不匹配：single 不收 id/key，list 收 id，keyed 收 key —— 传了不该传的也报
      const allowed = new Set(entry.registerOptions.map((o) => o.name))
      allowed.add('name')
      const extra = Object.keys(opts).filter((k) => !allowed.has(k))
      if (extra.length > 0) {
        findings.push(makeFinding(
          'C4.unknown-register-option',
          'WARN',
          `slot '${rec.slot}'（${entry.kind}）注册时传了 SDK 不认识的选项：${extra.join(', ')}`,
          `该基数接受的选项是 ${[...allowed].join(', ')}；多出来的会被忽略或报错。`,
          { run: runLabel, slot: rec.slot, kind: entry.kind, allowed: [...allowed], extra, passed: opts },
        ))
      }
    }
    // 一个 slot 一次 inject 却一次 register 都没发生 ⇒ 空占位
    if (rec.factoryCalled && rec.registers.length === 0 && !rec.factoryThrew) {
      findings.push(makeFinding(
        'C4.inject-without-register',
        'FAIL',
        `inject('${rec.slot}') 的 factory 跑完了却一次 register 都没调`,
        '占了 inject 名额但没贡献组件——加载后这里会是空白。',
        { run: runLabel, slot: rec.slot },
      ))
    }
    if (rec.factoryThrew) {
      findings.push(makeFinding(
        'C4.factory-threw',
        'FAIL',
        `inject('${rec.slot}') 的 factory 抛了：${rec.factoryThrew}`,
        '注册过程本身就失败了，界面不会出现。',
        { run: runLabel, slot: rec.slot, error: rec.factoryThrew },
      ))
    }
  }

  // C5 —— 保守降级：没有 slots 服务时不得崩、不得假装注册
  return findings
}

function validateDegradation({ calls, runLabel }) {
  const findings = []
  if (calls.register.length > 0 || calls.inject.length > 0) {
    findings.push(makeFinding(
      'C5.degraded-but-registered',
      'FAIL',
      '宿主没有 slots 服务，apply() 却仍然发出了 inject/register 调用',
      '无法确认座位存在时必须保守降级（不注册、记 warn），不能盲发注册。',
      { run: runLabel, injects: calls.inject.length, registers: calls.register.length },
    ))
  }
  const warned = calls.warn.some((w) => /slot/i.test(w))
  if (!warned) {
    findings.push(makeFinding(
      'C5.degraded-silently',
      'WARN',
      '宿主没有 slots 服务，apply() 没有留下任何提到 slot 的 warn',
      '降级应当可见（记 warn），否则用户只看到界面缺失、查不到原因。',
      { run: runLabel, warns: calls.warn },
    ))
  }
  return findings
}

/**
 * C6 —— denyRead 语义下也必须能注册（否则「gate 绿、真宿主空白」）。
 * 只有经 ctx.get 探测才能通过；Reflect.has + 直读会在这里红。
 */
function validateGuarded({ calls, getLog, runLabel }) {
  const findings = []
  if (!getLog.includes('slots')) {
    findings.push(makeFinding(
      'C6.probe-not-via-ctx-get',
      'FAIL',
      'apply() 没有经 ctx.get 探测 slots',
      `guard 语义下 Reflect.has 恒 false、直读抛错 —— 只有 ctx.get('slots') 是可选查找的正路。` +
        `getLog=${JSON.stringify(getLog)}`,
      { run: runLabel, getLog },
    ))
  }
  if (calls.inject.length === 0) {
    findings.push(makeFinding(
      'C6.no-registration-under-guard',
      'FAIL',
      'guard 语义下一次 slot 注册都没发生',
      '真 DSH 宿主的 apply() 收到的就是这种 facade。零注册 = 用户界面空白 —— ' +
        '正是 issue #100 的形状。多半是探测退回了 Reflect.has + 直读。',
      { run: runLabel, getLog, warns: calls.warn },
    ))
  }
  for (const rec of calls.inject) {
    if (rec.registers.length === 0 && !rec.factoryThrew) {
      findings.push(makeFinding(
        'C6.inject-without-register-under-guard',
        'FAIL',
        `guard 语义下 inject('${rec.slot}') 没有跟上 register`,
        '占了名额不贡献组件，界面上是空白。',
        { run: runLabel, slot: rec.slot },
      ))
    }
    for (const reg of rec.registers) {
      if (reg.componentIsNull) {
        findings.push(makeFinding(
          'C6.null-component-under-guard',
          'FAIL',
          `guard 语义下 register('${rec.slot}') 的组件是 null`,
          '占座不渲染 —— v2.0.0/v2.1.0 的形状。',
          { run: runLabel, slot: rec.slot },
        ))
      }
    }
  }
  return findings
}

// ── 主流程 ────────────────────────────────────────────────────────────────
function hr(line = '─') {
  return line.repeat(72)
}

const started = new Date().toISOString()
const report = {
  gate: 'release-ci-runtime-smoke',
  issue: 96,
  startedAt: started,
  repoRoot: REPO_ROOT,
  exitCode: 0,
  verdict: null,
  catalog: null,
  catalogDrift: null,
  artifact: null,
  runs: [],
  findings: [],
  summary: null,
  honestLimits: [
    '本 gate 证明 apply() 发出的调用落在 SDK 声明的座位上且组件非 null；不证明渲染正确。',
    '宿主是按 apply() 实际触碰的 Context 面构造的记录器，不是真 DSH web 宿主（需 DEEPSEEK_API_KEY，本机没有）。',
    '权威 slot catalog 来自 DSH SDK 的 CLIENT_SLOT_API，不是 pr-genius 内部任何表。',
    'C6 的 denyRead 语义宿主是真 guard（dynamicCordisContext）的复刻：直读未声明名抛、' +
      'Reflect.has 恒 false、ctx.get 可选查找。logger 也不放行（真 guard 的 CTX_VERBS ' +
      '不含它，且 LoggerService 不在 service store）—— 插件经 resolveLogger() 降级到 ' +
      'console 兜底，gate 在受控 console 上截获这些日志，而不是假装 facade 有 logger。',
    '真 DSH web 宿主的挂载与渲染仍未验证（需 DEEPSEEK_API_KEY，本机没有）——' +
      '见 issue #102 招募外部测试者。',
  ],
}

console.log(hr('═'))
console.log('pr-genius release runtime smoke gate  (issue #96)')
console.log(hr('═'))
console.log(`repo          : ${REPO_ROOT}`)
console.log(`catalog source: ${CATALOG_SOURCE}${CATALOG_FILE ? ` (${CATALOG_FILE})` : ''}`)

// 1. 权威 catalog ─────────────────────────────────────────────────────────
console.log(`\n[1/5] 取权威 slot catalog …`)
const catalogResult = await loadSlotCatalog({
  source: CATALOG_SOURCE,
  file: CATALOG_FILE,
  cwd: REPO_ROOT,
})
report.catalogAttempts = catalogResult.attempts
for (const a of catalogResult.attempts) {
  console.log(`      · ${a.source.padEnd(7)} ${a.ok ? `OK  ${a.count} keys` : `FAIL ${a.reason}`}`)
}

if (!catalogResult.ok) {
  // 铁律：取不到就明说取不到，绝不用替代品凑。
  report.exitCode = 2
  report.verdict = 'UNVERIFIABLE'
  report.catalog = { ok: false, error: catalogResult.error }
  report.findings.push(makeFinding(
    'C0.authoritative-catalog-unavailable',
    'FAIL',
    '权威 slot catalog 不可得 —— 无法验证 slot 名',
    `${catalogResult.error}\n` +
      `尝试过的来源：${catalogResult.attempts.map((a) => `${a.source}(${a.ok ? 'ok' : a.reason})`).join('; ')}\n` +
      `gate 不会用任何内置/猜测的 slot 列表代替：那只能确认错误，无法证伪。`,
    { attempts: catalogResult.attempts, upstream: UPSTREAM },
  ))
  writeFileSync(JSON_OUT, JSON.stringify(report, null, 2) + '\n')
  console.error('\n' + hr('═'))
  console.error('VERDICT: UNVERIFIABLE —— 权威 catalog 不可得，gate 不放行（exit 2）')
  console.error(report.findings[0].detail)
  console.error(`机器可读报告: ${JSON_OUT}`)
  process.exit(2)
}

const catalog = catalogResult.primary

// 铁律：catalog 出处必须是 DSH SDK 侧，不能是 pr-genius 自己写的表。
const ALLOWED_PROVENANCE = new Set([
  'installed-sdk-bundle',
  'upstream-source',
  'upstream-source-parsed-fallback',
  'local-snapshot',
])
if (!ALLOWED_PROVENANCE.has(catalog.provenance.kind)) {
  report.findings.push(makeFinding(
    'C0.catalog-provenance-not-external',
    'FAIL',
    `catalog 出处不是 DSH SDK 侧：${catalog.provenance.kind}`,
    'slot 名必须来自 SDK 自己声明的 CLIENT_SLOT_API。出处被换成内置/本地表即为循环验证。',
    catalog.provenance,
  ))
}

if (catalog.provenance.kind === 'local-snapshot') {
  report.findings.push(makeFinding(
    'C0.catalog-from-operator-snapshot',
    'WARN',
    'catalog 来自操作者提供的本地快照，不是 SDK 安装包/上游源码',
    '离线 CI 可以这么做，但快照有可能被改成「只含我要的 key」。' +
      '带这个 WARN 出的发版，应当有人核对快照出处与 SDK 版本的对应关系。',
    catalog.provenance,
  ))
}

report.catalog = {
  ok: true,
  source: catalog.source,
  provenance: catalog.provenance,
  keyCount: catalog.entries.length,
  keys: catalog.entries.map((e) => e.key).sort(),
}
console.log(`      → 采用 ${catalog.source}：${catalog.entries.length} 个 key`)
console.log(`        出处 ${catalog.provenance.kind}: ${catalog.provenance.package ?? catalog.provenance.repo ?? catalog.provenance.file}`)
if (catalog.provenance.packageVersion) console.log(`        版本 ${catalog.provenance.packageVersion}`)

if (catalogResult.crossCheck) {
  const drift = diffCatalogs(catalog, catalogResult.crossCheck)
  report.catalogDrift = drift
  console.log(`      → 交叉校验 ${catalogResult.crossCheck.source}：${catalogResult.crossCheck.entries.length} 个 key`)
  console.log(`        漂移：仅本侧 ${drift.onlyInA.length}，仅上游 ${drift.onlyInB.length}，kind/scope 变了 ${drift.kindOrScopeChanged.length}`)
  if (drift.onlyInA.length || drift.onlyInB.length || drift.kindOrScopeChanged.length) {
    report.findings.push(makeFinding(
      'C0.catalog-drift',
      'WARN',
      `钉住的 SDK catalog 与上游源码漂移（${drift.aCount} vs ${drift.bCount} keys）`,
      `仅钉住版有：${drift.onlyInA.join(', ') || '（无）'}\n` +
        `仅上游有：${drift.onlyInB.slice(0, 20).join(', ')}${drift.onlyInB.length > 20 ? ` …共 ${drift.onlyInB.length}` : ''}\n` +
        `kind/scope 变更：${drift.kindOrScopeChanged.map((c) => `${c.key} ${c.a}→${c.b}`).join('; ') || '（无）'}\n` +
        `gate 以**钉住版**（用户装到的那一份）为准。发版声明若按上游写，会在用户的宿主上落空。`,
      drift,
    ))
    console.log(`        ⚠ 漂移已记入 findings（发版声明必须按钉住版写，不是按上游写）`)
  }
} else {
  // 交叉校验缺席本身就是一条 WARN（issue #149 的第三条建议）。
  //
  // 为什么不能只改进 reason 就收工：主源（钉住的 npm 包）成功时，本 gate 此前
  // **一声不吭** —— 交叉校验失败被折叠进 attempts 日志，VERDICT 照样是 PASS。
  // 于是「CI 取不到上游」和「CI 一切正常」从结论上看不见区别，SDK 漂移在 CI 里
  // 就完全不可见。#145 能红那么久而没人发现依赖过期，根子就在这。
  //
  // 判据：权威仅来自钉住的包时，必须在 VERDICT 里说出来 —— 不是失败（钉住版本
  // 就是用户装到的那份，以它为准并不为错），但也不是「已交叉核对」。
  const ghAttempt = catalogResult.attempts.find((a) => a.source === 'github')
  // 「没尝试」和「试了没取到」是两件事，别混成一句：
  // `--catalog npm` 会跳过 github，那是我们自己关的，不是网络/认证问题。
  const neverTried = !ghAttempt
  const howAbsent = neverTried
    ? '本次运行被指定只用该来源，上游交叉校验**没有尝试**'
    : `上游源码交叉校验试了但没取到${ghAttempt.reason ? `（${ghAttempt.reason}）` : ''}`
  report.catalogCrossCheck = {
    ok: false,
    attempted: !neverTried,
    reason: ghAttempt ? ghAttempt.reason : 'not-attempted',
  }
  report.findings.push(makeFinding(
    'C0.catalog-crosscheck-absent',
    'WARN',
    '交叉校验缺席 —— 权威仅来自钉住的包，SDK 漂移未被核对',
    `本次 gate 的权威 slot catalog 只有 ${catalog.provenance.kind} 一个来源；${howAbsent}。\n` +
      `这不代表结论错了 —— 钉住版就是用户装到的那一份，以它为准是设计如此。` +
      `但它意味着**没人在核对钉住版与上游是否已经漂开**：上游改了 key 而我们没跟，` +
      `这里不会报。\n` +
      `若这条 WARN 长期存在，先查 CI 有没有给 gh 一个 token（#149 的第一条），` +
      `再查仓库名/路径是不是打错了。`,
    { attempts: catalogResult.attempts.map((a) => ({ source: a.source, ok: a.ok, reason: a.reason })) },
  ))
  console.log(`        ⚠ 交叉校验缺席已记入 findings（权威仅来自钉住的包）`)
}

// 1b. 反循环自检 —— gate 自己的源码里不得种 slot 名 ────────────────────────
console.log(`\n[1b] 反循环自检：gate 源码里不得硬编码 slot 名 …`)
{
  const selfFiles = [
    join(REPO_ROOT, 'scripts', 'release-smoke', 'slot-catalog.mjs'),
    join(REPO_ROOT, 'scripts', 'release-smoke', 'runtime-smoke-gate.mjs'),
  ].filter((p) => existsSync(p))
  const scan = assertNoHardcodedSlotKeys(
    selfFiles.map((p) => ({ file: p.slice(REPO_ROOT.length + 1), source: readFileSync(p, 'utf8') })),
    catalog.entries.map((e) => e.key),
  )
  if (!scan.ok) {
    report.findings.push(makeFinding(
      'C0.circular-validation',
      'FAIL',
      'gate 源码里硬编码了权威 catalog 的 slot 名 —— 循环验证',
      `以下字面量直接出现在代码里：${scan.offenders.map((o) => `${o.file}:${o.line} '${o.key}'`).join('; ')}\n` +
        `slot 名必须只来自 DSH SDK 的 CLIENT_SLOT_API。代码里写死 = 自己出题自己批卷：只能确认错误，无法证伪。`,
      scan,
    ))
  }
  console.log(`      · 扫描 ${selfFiles.length} 个 gate 源文件，命中 ${scan.offenders.length} 处` +
    (scan.ok ? '（干净）' : '（已记 FAIL）'))
  report.antiCircular = { filesScanned: selfFiles.map((p) => p.slice(REPO_ROOT.length + 1)), offenders: scan.offenders }
}

// 2. 打包 ─────────────────────────────────────────────────────────────────
console.log(`\n[2/5] 打包并解压真实 tarball …`)
const workDir = mkdtempSync(join(tmpdir(), 'pg-release-smoke-'))
let tarballPath = null
let extractRoot = null
let artifactEntry = null

if (SKIP_PACK) {
  artifactEntry = join(REPO_ROOT, 'dist', 'index.mjs')
  console.log(`      · --skip-pack：直接用工作树 dist/（${artifactEntry}）`)
} else {
  // dist/ 必须先存在：npm pack 打的是工作树里现有的 dist/，不替你编译。
  const distEntry = join(REPO_ROOT, 'dist', 'index.mjs')
  if (!existsSync(distEntry) || FORCE_BUILD) {
    console.log(`      · ${FORCE_BUILD ? '--build' : 'dist/ 缺失'}，先 npm run build …`)
    execSync('npm run build', { cwd: REPO_ROOT, stdio: 'pipe' })
    report.artifactBuiltByGate = true
  }
  const packOut = execFileSync('npm', ['pack', '--pack-destination', workDir, '--json'], {
    cwd: REPO_ROOT,
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe'],
    timeout: 180_000,
  })
  const packInfo = JSON.parse(packOut)
  const packed = packInfo[0] ?? packInfo
  tarballPath = join(workDir, packed.filename)
  if (!existsSync(tarballPath)) throw new Error(`npm pack 说打了 ${packed.filename}，但 ${tarballPath} 不存在`)
  console.log(`      · tarball: ${packed.filename}  (${packed.size} bytes, ${packed.entryCount} entries)`)

  extractRoot = join(workDir, 'extract')
  mkdirSync(extractRoot, { recursive: true })
  execFileSync('tar', ['-xzf', tarballPath, '-C', extractRoot], { stdio: 'pipe' })
  const pkgDir = join(extractRoot, 'package')
  // 宿主提供 peer 依赖（react / react-dom / cordis），所以产物把它们 external 了
  // —— 内联 React 会让带自己 React 的宿主 hooks 崩（issue #101）。gate 模拟宿主：
  // 把仓库 node_modules 链到解包目录，让 import 能解析到宿主侧的那些包。
  // 不是把 React 重新打进产物 —— 那正是 #101 的修法要避开的。
  const peersDir = join(pkgDir, 'node_modules')
  try {
    execFileSync('ln', ['-s', join(REPO_ROOT, 'node_modules'), peersDir], { stdio: 'pipe' })
    console.log(`      · host peers provided via symlink → node_modules (react external, issue #101)`)
  } catch (err) {
    console.log(`      · WARN: could not link host node_modules: ${err && err.message}`)
  }
  artifactEntry = join(pkgDir, 'dist', 'index.mjs')
  if (!existsSync(artifactEntry)) {
    throw new Error(`tarball 里没有 dist/index.mjs —— ` +
      `files 白名单或 build 有问题。包内容：${readdirSync(pkgDir).join(', ')}`)
  }
  const packedFiles = []
  const walk = (d, prefix = '') => {
    for (const e of readdirSync(d, { withFileTypes: true })) {
      const rel = prefix ? `${prefix}/${e.name}` : e.name
      if (e.isDirectory()) walk(join(d, e.name), rel)
      else packedFiles.push(rel)
    }
  }
  walk(pkgDir)
  report.artifact = {
    mode: 'npm-pack',
    tarball: packed.filename,
    tarballBytes: packed.size,
    entryCount: packed.entryCount,
    entry: 'dist/index.mjs',
    packedFileCount: packedFiles.length,
    packedHasClientBundle: packedFiles.some((f) => f.startsWith('src/client/') || f.includes('AdvisorPanel')),
    packedFilesSample: packedFiles.slice(0, 40),
  }
  console.log(`      · 解压到 ${pkgDir}`)
  console.log(`      · 入口 ${artifactEntry}`)
  console.log(`      · 包内含 src/client/ 或 AdvisorPanel: ${report.artifact.packedHasClientBundle}`)
}

const artifactUrl = pathToFileURL(artifactEntry).href

// 3. 调 apply()，带 slots 的宿主 ─────────────────────────────────────────
console.log(`\n[3/5] 调 apply() —— 宿主提供 slots 服务 …`)
const withSlots = makeRecordingHost({ withSlots: true })
let exportsBefore = []
let applyError = null
try {
  const r = await runApply(artifactUrl, withSlots)
  exportsBefore = r.exportsBefore
} catch (err) {
  applyError = String(err && err.stack ? err.stack : err)
  report.findings.push(makeFinding(
    'C0.apply-threw',
    'FAIL',
    '对 tarball 产物调 apply() 直接抛错',
    applyError,
    { entry: artifactEntry },
  ))
}
const regs = withSlots.calls.register
const injCalls = withSlots.calls.inject
console.log(`      · inject ${injCalls.length} 次, register ${regs.length} 次`)
for (const rec of injCalls) {
  const entry = catalog.entries.find((e) => e.key === rec.slot)
  const status = entry ? `${entry.kind}/${entry.scope}` : 'NOT-IN-CATALOG'
  const comp = rec.registers.map((r) => r.componentType).join(',') || '(no register)'
  console.log(`        ${rec.slot.padEnd(28)} ${status.padEnd(24)} component=${comp}`)
}

// 产物元数据：导出面 + inject 声明。inject 声明决定「期望有哪些 slot 可达」。
let injectDeclared = []
try {
  const mod = await import(artifactUrl)
  if (Array.isArray(mod.inject)) injectDeclared = [...mod.inject]
  report.artifact = {
    mode: SKIP_PACK ? 'dist-in-tree' : 'npm-pack',
    entry: 'dist/index.mjs',
    ...(report.artifact ?? {}),
    exports: Object.keys(mod).sort(),
    hasApply: typeof mod.apply === 'function',
    injectDeclared: Array.isArray(mod.inject) ? [...mod.inject] : null,
    provideServiceName: typeof mod.provide === 'string' ? mod.provide : null,
    pluginName: typeof mod.name === 'string' ? mod.name : null,
  }
} catch (err) {
  report.findings.push(makeFinding(
    'C0.artifact-import-failed',
    'FAIL',
    '产物 import 失败',
    String(err && err.stack ? err.stack : err),
    { entry: artifactEntry },
  ))
}
report.runs.push({
  label: 'with-slots',
  injects: injCalls.map((r) => ({ slot: r.slot, factoryCalled: r.factoryCalled, factoryThrew: r.factoryThrew ?? null, registers: r.registers })),
  warns: withSlots.calls.warn,
  infos: withSlots.calls.info,
  provides: withSlots.calls.provide,
  effects: withSlots.calls.effect,
})

// 4. 调 apply()，没有 slots 的宿主（保守降级）─────────────────────────────
console.log(`\n[4/5] 调 apply() —— 宿主没有 slots 服务（保守降级探测）…`)
const noSlots = makeRecordingHost({ withSlots: false })
let degradeError = null
try {
  await runApply(artifactUrl, noSlots)
} catch (err) {
  degradeError = String(err && err.message ? err.message : err)
  report.findings.push(makeFinding(
    'C5.degrade-threw',
    'FAIL',
    '宿主没有 slots 服务时 apply() 抛错（应当保守降级，不是崩）',
    degradeError,
    { entry: artifactEntry },
  ))
}
console.log(`      · inject ${noSlots.calls.inject.length}, register ${noSlots.calls.register.length}, warn ${noSlots.calls.warn.length}`)
for (const w of noSlots.calls.warn.slice(0, 6)) console.log(`        warn: ${w}`)
report.runs.push({
  label: 'without-slots',
  injects: [],
  registers: [],
  warns: noSlots.calls.warn,
  infos: noSlots.calls.info,
  degradeError,
})

// 4b. 调 apply()，denyRead 语义的宿主（真 guard 的复刻）────────────────────
console.log(`\n[4b/5] 调 apply() —— denyRead 语义宿主（真 guard 复刻）…`)
// slots 只进 services 表，**不**挂成 ctx 的字面量属性 —— 旧 mock 正是靠字面量绕开 guard 的。
const guarded = makeGuardedHost()
// 必须**就地**填 serviceTable —— `guarded.services = {...}` 会把属性换成新对象，
// 闭包里的 serviceTable 仍是空表，get('slots') 就永远拿不到（C6 曾因此假红）。
guarded.services.slots = {
  inject: (slot, factory) => {
    const rec = { slot, factoryCalled: false, registers: [] }
    guarded.calls.inject.push(rec)
    try {
      const out = typeof factory === 'function' ? factory() : undefined
      rec.factoryCalled = true
      rec.factoryReturn = out === undefined ? 'undefined' : typeof out
    } catch (err) {
      rec.factoryThrew = String(err && err.message ? err.message : err)
    }
    return () => { rec.disposed = true }
  },
  register: (opts, component) => {
    const rec = {
      opts: opts === null ? null : typeof opts === 'object' ? JSON.parse(JSON.stringify(opts, (k, v) => (typeof v === 'function' ? '[function]' : v))) : String(opts),
      componentType: component === null ? 'null' : component === undefined ? 'undefined' : typeof component,
      componentIsNull: component === null || component === undefined,
    }
    const last = guarded.calls.inject[guarded.calls.inject.length - 1]
    if (last) last.registers.push(rec)
    guarded.calls.register.push(rec)
    return () => { rec.disposed = true }
  },
}
let guardedError = null
// 真 guard facade 上没有 logger，插件降级到 console 兜底 —— 把 console 截获到
// calls 里，否则降级日志（"ctx.slots unavailable…"）在报告里凭空消失。
const consoleCapture = {
  info: (...a) => guarded.calls.info.push(a.map(String).join(' ')),
  warn: (...a) => guarded.calls.warn.push(a.map(String).join(' ')),
  error: (...a) => guarded.calls.error.push(a.map(String).join(' ')),
}
const realConsole = { info: console.info, warn: console.warn, error: console.error }
Object.assign(console, consoleCapture)
try {
  await runApply(artifactUrl, guarded)
} catch (err) {
  guardedError = String(err && err.message ? err.message : err)
  report.findings.push(makeFinding(
    'C6.guarded-apply-threw',
    'FAIL',
    '在 denyRead 语义宿主上 apply() 抛错',
    `真 DSH 宿主就是这种 facade，抛错 = 用户装完插件直接失败。${guardedError}`,
    { entry: artifactEntry, error: guardedError },
  ))
} finally {
  Object.assign(console, realConsole)
}
console.log(`      · get 探测: ${JSON.stringify(guarded.getLog)}`)
console.log(`      · inject ${guarded.calls.inject.length} 次, register ${guarded.calls.register.length}`)
for (const rec of guarded.calls.inject) {
  const comp = rec.registers.map((r) => r.componentType).join(',') || '(no register)'
  console.log(`        ${rec.slot.padEnd(28)} component=${comp}`)
}
report.runs.push({
  label: 'guarded-denyread',
  injects: guarded.calls.inject.map((r) => ({ slot: r.slot, factoryCalled: r.factoryCalled, factoryThrew: r.factoryThrew ?? null, registers: r.registers })),
  registers: guarded.calls.register,
  warns: guarded.calls.warn,
  infos: guarded.calls.info,
  getLog: guarded.getLog,
  guardedError,
})

// 5. 判定 ─────────────────────────────────────────────────────────────────
console.log(`\n[5/5] 判定 …`)
if (!applyError) {
  report.findings.push(...validate({ calls: withSlots.calls, catalog, injectDeclared, runLabel: 'with-slots' }))
  report.findings.push(...validateDegradation({ calls: noSlots.calls, runLabel: 'without-slots' }))
}
if (!guardedError) {
  report.findings.push(...validateGuarded({
    calls: guarded.calls,
    getLog: guarded.getLog,
    runLabel: 'guarded-denyread',
  }))
}

const fails = report.findings.filter((f) => f.severity === 'FAIL')
const warns = report.findings.filter((f) => f.severity === 'WARN')
const pass = fails.length === 0
report.exitCode = applyError ? 1 : pass ? 0 : 1
report.verdict = applyError ? 'FAIL' : pass ? (warns.length ? 'PASS_WITH_WARNINGS' : 'PASS') : 'FAIL'
report.summary = {
  catalogKeys: catalog.entries.length,
  catalogSource: catalog.source,
  injects: injCalls.length,
  registers: regs.length,
  guardedInjects: guarded.calls.inject.length,
  guardedRegisters: guarded.calls.register.length,
  failCount: fails.length,
  warnCount: warns.length,
  exitCode: report.exitCode,
}

// 人类可读输出 ────────────────────────────────────────────────────────────
console.log('\n' + hr('═'))
console.log('FINDINGS')
console.log(hr('═'))
if (report.findings.length === 0) {
  console.log('（无）')
}
for (const f of report.findings) {
  const badge = f.severity === 'FAIL' ? '✗ FAIL' : f.severity === 'WARN' ? '! WARN' : '· INFO'
  console.log(`\n${badge}  [${f.id}] ${f.title}`)
  console.log(`      ${f.detail.split('\n').join('\n      ')}`)
}

console.log('\n' + hr('═'))
console.log('REGISTRATION LEDGER  (apply() 实际发出的调用 × 权威 catalog)')
console.log(hr('═'))
console.log(`catalog: ${catalog.source} · ${catalog.provenance.kind} · ${catalog.entries.length} keys` +
  (catalog.provenance.packageVersion ? ` · ${catalog.provenance.package} ${catalog.provenance.packageVersion}` : ''))
console.log(`         ${catalog.provenance.upstreamModule ?? catalog.provenance.repo ?? ''}`)
const ledger = injCalls.map((rec) => {
  const entry = catalog.entries.find((e) => e.key === rec.slot)
  return {
    slot: rec.slot,
    inCatalog: !!entry,
    kind: entry?.kind ?? null,
    scope: entry?.scope ?? null,
    components: rec.registers.map((r) => r.componentType),
    required: entry ? entry.registerOptions.filter((o) => o.requirement === 'required').map((o) => o.name) : [],
    passed: rec.registers.map((r) => r.opts),
  }
})
for (const row of ledger) {
  console.log(`  ${row.inCatalog ? '✓' : '✗'} ${row.slot.padEnd(28)} ${String(row.kind ?? '—').padEnd(8)} ${String(row.scope ?? '—').padEnd(14)} comp=${row.components.join(',') || '—'} required=[${row.required.join(',')}] passed=${JSON.stringify(row.passed)}`)
}
report.ledger = ledger

console.log('\n' + hr('═'))
console.log(`VERDICT: ${report.verdict}   (exit ${report.exitCode})`)
console.log(hr('═'))
console.log(`catalog keys=${report.summary.catalogKeys} source=${report.summary.catalogSource}  injects=${report.summary.injects} registers=${report.summary.registers}`)
console.log(`guarded(denyRead) injects=${report.summary.guardedInjects} registers=${report.summary.guardedRegisters}`)
console.log(`FAIL=${fails.length}  WARN=${warns.length}`)
console.log('\n诚实边界：')
for (const l of report.honestLimits) console.log(`  · ${l}`)
console.log(`\n机器可读报告: ${JSON_OUT}`)

mkdirSync(dirname(JSON_OUT), { recursive: true })
writeFileSync(JSON_OUT, JSON.stringify(report, null, 2) + '\n')

if (!KEEP_WORK && workDir) {
  try {
    rmSync(workDir, { recursive: true, force: true })
  } catch { /* 清不掉不影响判定 */ }
} else if (workDir) {
  console.log(`工作目录保留: ${workDir}`)
}

process.exit(report.exitCode)
