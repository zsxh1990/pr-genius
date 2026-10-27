/**
 * 权威 slot catalog 加载器 —— 发版 smoke gate 的唯一 slot 名来源。
 *
 * ── 反循环纪律（issue #96 的核心）────────────────────────────────────────
 * slot 名**绝不**写在 pr-genius 里。本模块只做一件事：从 DSH SDK 取出它自己
 * 声明的 slot 表，并把「从哪取的、哪个版本、什么时候取的」一并交出来。
 * 取不到就返回 `{ ok: false }`，调用方必须报告「无法验证」并以非 0 退出——
 * **不得**退回到任何内置列表。内置列表 = 自己出题自己批卷，只能确认错误，
 * 无法证伪（v2.1.2 那次「模拟 host」就是这么假通过的）。
 *
 * ── 权威来源与优先级 ────────────────────────────────────────────────────
 * 1. `npm`（默认首选）—— 解析已安装的
 *      `@deepseek-ai/dsh-cordis-client-runner` 包里的 `lib/client.js`，
 *    静态切出 `CLIENT_SLOT_API` 数组字面量后求值。
 *    这是 `packages/extensions/cordis-client-runner/src/client/slot-catalog.ts`
 *    编译后的产物，且**版本被 package.json 钉死**（pr-genius 声明的就是
 *    它要兼容的 SDK 版本，用户装到的也是这一份）。
 *    不 import 包本身：`lib/client.js` 顶层有浏览器副作用
 *    （`window.__ModuleLoader__.load(...)`），node 下直接 import 会炸。
 *
 * 2. `github`（交叉校验 / 离线兜底）—— `gh api` 只读取
 *      deepseek-ai/deepseek-harness@<ref>
 *        /packages/extensions/cordis-client-runner/src/client/slot-catalog.ts
 *    同一份源码的**当前上游**形态。与 npm 版本可能漂移，漂移本身要报告，
 *    不能拿上游覆盖钉死的版本。
 *    注意仓库名是 `deepseek-harness`、默认分支是 `master`
 *    （不是 `deepseek-harness-sdk` / `main` —— 那两个 404）。
 *
 * 3. `file` —— `--catalog-file <path>` 指定的 JSON 快照（离线 CI 用）。
 *
 * 两个来源都取不到 ⇒ `ok: false`，无第三条路。
 *
 * ── 诚实边界 ────────────────────────────────────────────────────────────
 * 本模块只负责「取出表」。表里的 key 是否真的能渲染，要真 DSH 宿主才知道；
 * 本机没有 DEEPSEEK_API_KEY，从没在真宿主里加载过。gate 能证明的是
 * 「注册的 key 落在 SDK 自己声明的表内、组件不是 null」，不是「渲染出来了」。
 */
import { readFileSync, existsSync } from 'node:fs'
import { createRequire } from 'node:module'
import { dirname, join, resolve as resolvePath } from 'node:path'
import { execFileSync } from 'node:child_process'

/** 上游权威源码路径 —— 唯一事实，不要散落各处。 */
export const UPSTREAM = {
  repo: 'deepseek-ai/deepseek-harness',
  ref: 'master',
  path: 'packages/extensions/cordis-client-runner/src/client/slot-catalog.ts',
  /** 编译后落在这个 npm 包里。 */
  npmPackage: '@deepseek-ai/dsh-cordis-client-runner',
}

/**
 * 从 JS 源码里静态切出 `const NAME = <array literal>` 的字面量并求值。
 * 不执行模块（模块有浏览器副作用），只对字面量本身求值。
 */
export function extractArrayLiteral(source, marker) {
  const at = source.indexOf(marker)
  if (at < 0) throw new Error(`marker not found in source: ${marker}`)
  // 用 marker 自己的最后一个 '[' 作数组开括号 —— marker 里可能带类型标注
  // （如 `ClientSlotEntry[]`），第一个 '[' 会命中那对空方括号而不是字面量。
  const openInMarker = marker.lastIndexOf('[')
  const i = openInMarker >= 0 ? at + openInMarker : source.indexOf('[', at + marker.length)
  if (i < 0 || source[i] !== '[') throw new Error(`marker has no array opener: ${marker}`)
  let depth = 0
  let end = -1
  for (let j = i; j < source.length; j++) {
    const c = source[j]
    if (c === '[') depth++
    else if (c === ']') {
      depth--
      if (depth === 0) {
        end = j
        break
      }
    }
  }
  if (end < 0) throw new Error(`unbalanced brackets after marker: ${marker}`)
  // 字面量是生成器产出的纯数据（字符串 / 数字 / 布尔 / 嵌套数组对象），无标识符引用。
  const literal = source.slice(i, end + 1)
  return new Function(`return ${literal}`)()
}

/** 归一化：两个来源的条目形状略有差异，收敛到 gate 需要的最小面。 */
function normalize(entry) {
  return {
    key: String(entry.key),
    kind: String(entry.kind),
    scope: String(entry.scope),
    registerOptions: (entry.registerOptions ?? []).map((o) => ({
      name: String(o.name),
      requirement: String(o.requirement),
    })),
    replaceRisk: entry.replaceRisk ? String(entry.replaceRisk) : null,
    declaredBy: entry.declaredBy ? String(entry.declaredBy) : null,
    occupants: (entry.occupants ?? []).map(String),
    source: entry.source ? String(entry.source) : null,
    summary: entry.summary ? String(entry.summary) : null,
  }
}

/** 来源 1：已安装 SDK 包的编译产物（版本被 package.json 钉死）。 */
function loadFromNpm(cwd) {
  const require = createRequire(join(cwd, 'package.json'))
  let pkgJsonPath
  try {
    pkgJsonPath = require.resolve(`${UPSTREAM.npmPackage}/package.json`)
  } catch {
    return { ok: false, source: 'npm', reason: `${UPSTREAM.npmPackage} 未安装（resolve 失败）` }
  }
  const pkgDir = dirname(pkgJsonPath)
  const pkg = JSON.parse(readFileSync(pkgJsonPath, 'utf8'))
  const bundlePath = join(pkgDir, 'lib', 'client.js')
  if (!existsSync(bundlePath)) {
    return { ok: false, source: 'npm', reason: `包里没有 lib/client.js：${bundlePath}` }
  }
  try {
    const js = readFileSync(bundlePath, 'utf8')
    const raw = extractArrayLiteral(js, 'const CLIENT_SLOT_API = [')
    if (!Array.isArray(raw) || raw.length === 0) {
      return { ok: false, source: 'npm', reason: 'CLIENT_SLOT_API 解析为空' }
    }
    return {
      ok: true,
      source: 'npm',
      provenance: {
        kind: 'installed-sdk-bundle',
        package: pkg.name,
        packageVersion: pkg.version,
        packageDir: pkgDir,
        file: 'lib/client.js',
        exportName: 'CLIENT_SLOT_API',
        upstreamModule: `${UPSTREAM.repo}@${UPSTREAM.ref}:${UPSTREAM.path}`,
        note: '已安装 SDK 包的编译产物；package.json 钉住了版本，即用户装到的那一份。',
      },
      entries: raw.map(normalize),
    }
  } catch (err) {
    return { ok: false, source: 'npm', reason: `解析 lib/client.js 失败：${err.message}` }
  }
}

/**
 * 把 `execFileSync('gh', …)` 的失败压成一句**可分诊**的 reason（issue #149）。
 *
 * 这里曾经只回声 `err.message`，而它恒等于 `Command failed: gh api …` ——
 * 限流(403)、仓库名打错(404)、没认证(401)、gh 不在 PATH、超时，五种完全不同的
 * 事故在 reason 里长得一模一样。CI 里 `gh api` 交叉校验因此从未被人当回事，
 * SDK 漂移就一直不可见。
 *
 * 判据：**退出码、信号、stderr 首行（gh 把 HTTP 码打在那）必须在场**，
 * 且「gh 压根没起来」要和「gh 跑了但失败」分得开 —— 后者才有 HTTP 码，前者没有，
 * 不要替它编一个。
 *
 * 分支顺序是判据的一部分，不是实现细节。Node 的 `execFileSync` 超时错误形状是
 * `{code:'ETIMEDOUT', syscall:'spawnSync …', status:null, signal:'SIGTERM'}`
 * —— **没有 `killed` 属性**（实测 Node 26，CI 的 Node 22 同一条 spawn_sync 路径）。
 * 所以超时必须排在「`status == null && syscall` ⇒ 没起来」之前判断，否则真实超时
 * 会被误报成「gh 不可执行（ETIMEDOUT）」，而超时分支永远走不到。
 */
export function describeGhFailure(err, { repo, ref, path }) {
  const target = `${repo}@${ref}:${path}`
  const parts = [`gh api 取不到 ${target}`]

  // 超时 / 被杀 —— 不是「取不到」。必须排在 spawn 分支之前：
  // 真实超时同样带 syscall 且 status 为 null，会先被下面那条吃掉。
  // 判据取自真实形状：`code === 'ETIMEDOUT'`、`killed`（仅被显式 kill 时有）、
  // 或有信号却无退出码。不假设 `killed` 一定存在 —— 超时路径上它不存在。
  const timedOut = err?.code === 'ETIMEDOUT' || err?.killed === true
  const signalledNoStatus = Boolean(err?.signal) && (err.status === null || err.status === undefined)
  if (timedOut || signalledNoStatus) {
    parts.push(`超时或被杀（code=${err?.code ?? 'n/a'} signal=${err?.signal ?? 'n/a'}）`)
    return parts.join(' —— ')
  }

  // spawn 没起来 —— 环境问题（gh 不在 PATH / 权限），不是「取不到」。
  if (err?.code === 'ENOENT' || (err?.status == null && err?.syscall)) {
    parts.push(`gh 不可执行（${err.code ?? err.syscall}）`)
    return parts.join(' —— ')
  }

  if (typeof err?.status === 'number') parts.push(`exit=${err.status}`)
  if (err?.signal) parts.push(`signal=${err.signal}`)

  const stderr = String(err?.stderr ?? '').trim()
  const firstLine = stderr.split('\n').find((l) => l.trim()) ?? ''
  if (firstLine) {
    parts.push(firstLine.trim())
  } else if (err?.message) {
    // stderr 空了才退回 err.message —— 但那句 "Command failed" 单独出现
    // 正是本函数要消灭的形状，所以永远不作为唯一内容。
    parts.push(err.message)
  }
  return parts.join(' —— ')
}

/** 来源 2：上游源码（gh api 只读）。 */
function loadFromGithub({ repo, ref, path }) {
  let payload
  try {
    payload = execFileSync(
      'gh',
      ['api', `repos/${repo}/contents/${path}?ref=${ref}`, '--jq', '.content'],
      { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'], timeout: 60_000 },
    )
  } catch (err) {
    return { ok: false, source: 'github', reason: describeGhFailure(err, { repo, ref, path }) }
  }
  let ts
  try {
    ts = Buffer.from(payload.trim(), 'base64').toString('utf8')
  } catch (err) {
    return { ok: false, source: 'github', reason: `base64 解码失败：${err.message}` }
  }
  if (!ts.includes('CLIENT_SLOT_API') && !ts.includes('key:')) {
    return { ok: false, source: 'github', reason: '取回的内容不像 slot-catalog（缺 key 声明）' }
  }
  try {
    let raw = null
    let lastErr = null
    for (const marker of [
      'export const CLIENT_SLOT_API: readonly ClientSlotEntry[] = [',
      'const CLIENT_SLOT_API: readonly ClientSlotEntry[] = [',
      'const CLIENT_SLOT_API = [',
    ]) {
      try {
        raw = extractArrayLiteral(ts, marker)
        break
      } catch (err) {
        lastErr = err
      }
    }
    if (raw === null) throw lastErr ?? new Error('no marker matched')
    if (!Array.isArray(raw) || raw.length === 0) {
      return { ok: false, source: 'github', reason: 'CLIENT_SLOT_API 解析为空' }
    }
    return {
      ok: true,
      source: 'github',
      provenance: {
        kind: 'upstream-source',
        repo,
        ref,
        path,
        note: '上游仓库当前源码；可能与 pr-genius 钉住的 SDK 版本漂移，只作交叉校验。',
      },
      entries: raw.map(normalize),
    }
  } catch {
    // 源码里可能是 `const CLIENT_SLOT_API = [` 的不同书写；退回正则抽 key/kind/scope。
    const entries = []
    const re = /key:\s*'([^']+)',\s*\n\s*kind:\s*'([^']+)',\s*\n\s*scope:\s*'([^']+)'/g
    let m
    while ((m = re.exec(ts)) !== null) {
      entries.push(normalize({ key: m[1], kind: m[2], scope: m[3] }))
    }
    if (entries.length === 0) {
      return { ok: false, source: 'github', reason: '无法从上游源码解析出任何 slot 条目' }
    }
    return {
      ok: true,
      source: 'github',
      provenance: {
        kind: 'upstream-source-parsed-fallback',
        repo,
        ref,
        path,
        note: '正则降级解析（仅 key/kind/scope），完整字段不可得。',
      },
      entries,
    }
  }
}

/** 来源 3：本地 JSON 快照。 */
function loadFromFile(path) {
  const abs = resolvePath(path)
  if (!existsSync(abs)) return { ok: false, source: 'file', reason: `快照不存在：${abs}` }
  try {
    const doc = JSON.parse(readFileSync(abs, 'utf8'))
    const raw = Array.isArray(doc) ? doc : doc.entries
    if (!Array.isArray(raw) || raw.length === 0) {
      return { ok: false, source: 'file', reason: '快照里没有 entries' }
    }
    return {
      ok: true,
      source: 'file',
      provenance: { kind: 'local-snapshot', file: abs, note: doc.provenance?.note ?? '本地快照。' },
      entries: raw.map(normalize),
    }
  } catch (err) {
    return { ok: false, source: 'file', reason: `快照解析失败：${err.message}` }
  }
}

/**
 * 取权威 catalog。
 *
 * @param {object} opts
 * @param {'auto'|'npm'|'github'|'file'} [opts.source]  取法；auto = npm 优先，github 交叉校验。
 * @param {string} [opts.cwd]                            解析 node_modules 的起点（默认 process.cwd()）。
 * @param {string} [opts.file]                           source='file' 时的快照路径。
 * @returns {Promise<object>}  `{ ok, primary, crossCheck?, attempts[] }`
 */
export async function loadSlotCatalog(opts = {}) {
  const source = opts.source ?? 'auto'
  const cwd = opts.cwd ?? process.cwd()
  const attempts = []
  const up = { repo: UPSTREAM.repo, ref: UPSTREAM.ref, path: UPSTREAM.path }

  const tryOne = (fn) => {
    const r = fn()
    attempts.push({ source: r.source, ok: r.ok, reason: r.reason ?? null, count: r.ok ? r.entries.length : 0 })
    return r
  }

  if (source === 'file') {
    const r = tryOne(() => loadFromFile(opts.file))
    return { ok: r.ok, primary: r.ok ? r : null, attempts, crossCheck: null, error: r.reason ?? null }
  }

  if (source === 'github') {
    const r = tryOne(() => loadFromGithub(up))
    return { ok: r.ok, primary: r.ok ? r : null, attempts, crossCheck: null, error: r.reason ?? null }
  }

  if (source === 'npm') {
    const r = tryOne(() => loadFromNpm(cwd))
    return { ok: r.ok, primary: r.ok ? r : null, attempts, crossCheck: null, error: r.reason ?? null }
  }

  // auto：npm 优先（版本钉死的那份是发版要负责的），github 作交叉校验。
  const npm = tryOne(() => loadFromNpm(cwd))
  const gh = tryOne(() => loadFromGithub(up))

  const primary = npm.ok ? npm : gh.ok ? gh : null
  const crossCheck = npm.ok && gh.ok ? gh : null

  return {
    ok: primary !== null,
    primary,
    crossCheck,
    attempts,
    error: primary === null
      ? '权威 catalog 不可得：npm 包与上游源码都取不到 —— 无法验证 slot 名，gate 不得放行。'
      : null,
  }
}

/** 两个 catalog 的漂移报告（同一份源码的两个版本形态）。 */
export function diffCatalogs(a, b) {
  const am = new Map(a.entries.map((e) => [e.key, e]))
  const bm = new Map(b.entries.map((e) => [e.key, e]))
  const onlyA = [...am.keys()].filter((k) => !bm.has(k)).sort()
  const onlyB = [...bm.keys()].filter((k) => !am.has(k)).sort()
  const kindChanged = []
  for (const [k, ea] of am) {
    const eb = bm.get(k)
    if (eb && (ea.kind !== eb.kind || ea.scope !== eb.scope)) {
      kindChanged.push({ key: k, a: `${ea.kind}/${ea.scope}`, b: `${eb.kind}/${eb.scope}` })
    }
  }
  return {
    aSource: a.provenance,
    bSource: b.provenance,
    aCount: a.entries.length,
    bCount: b.entries.length,
    onlyInA: onlyA,
    onlyInB: onlyB,
    kindOrScopeChanged: kindChanged,
  }
}

/**
 * 反循环自检（issue #96 的核心纪律，做成可执行的）。
 *
 * 问题：如果 gate 的 slot 列表是代码里写死的，那就是自己出题自己批卷——
 * 只能确认错误，无法证伪。v2.1.2 那次「模拟 host 只接受真实 key」就是这么假通过的：
 * 那个 catalog 是自己编的，里面就放了自己要的 key。
 *
 * 做法：把 gate 自己的源码去掉注释，找出里面所有字符串字面量；
 * 任何一个字面量**恰好等于**权威 catalog 里的某个 slot key，就说明有人把 slot 名
 * 种进了代码。非 slot 的字符串（'npm' / 'auto' / 'lib/client.js' …）不在 catalog 里，
 * 不会误报。
 *
 * @returns {{ ok: boolean, offenders: Array<{file: string, key: string, line: number}> }}
 */
export function assertNoHardcodedSlotKeys(fileSources, catalogKeys) {
  const keySet = new Set(catalogKeys)
  const offenders = []
  for (const { file, source } of fileSources) {
    // 去掉 /* */ 与 // 注释，避免文档里举例的 slot 名被算作「硬编码」。
    const stripped = source
      .replace(/\/\*[\s\S]*?\*\//g, (m) => m.replace(/[^\n]/g, ' '))
      .replace(/(^|[^:])\/\/[^\n]*/g, (m, p1) => p1 + ' '.repeat(m.length - p1.length))
    const lines = stripped.split('\n')
    lines.forEach((lineText, idx) => {
      for (const m of lineText.matchAll(/(['"])((?:\\.|[^\\])*?)\1/g)) {
        const lit = m[2]
        if (keySet.has(lit)) offenders.push({ file, key: lit, line: idx + 1 })
      }
    })
  }
  return { ok: offenders.length === 0, offenders }
}
