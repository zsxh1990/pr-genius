#!/usr/bin/env node
/**
 * 拉上游 DSH slot-catalog，跑 slot 对齐验证（issue #97）。
 *
 * 用法：
 *   node scripts/verify-slot-keys.mjs            # gh api 拉上游 main 的 catalog
 *   node scripts/verify-slot-keys.mjs <file.ts>  # 用给定的 catalog 文件
 *   node scripts/verify-slot-keys.mjs             # 默认只读：报漂移，不写盘
 *   node scripts/verify-slot-keys.mjs --refresh   # 显式刷新 fixture 与 src/ 生成物
 *   node scripts/verify-slot-keys.mjs --check     # 与默认等价（旧写法，保留）
 *   exit 0=一致  2=内容不满足  3=检查没跑起来
 *
 * 做三件事：
 *   1. 取到权威 catalog（唯一真相源），列全部 key 与数量
 *   2. 与 test/fixtures/dsh-slot-catalog.ts 快照对比（新鲜度）
 *   3. 跑 test/slot-catalog.test.ts —— allowed 集合由该 catalog 的 bytes 解析而来，
 *      调 apply() 打印实际注入的 key 并逐个对照
 *
 * 绝不用替代品凑：取不到就退出并说明「权威 catalog 不可得」。
 */
import { execFileSync } from 'node:child_process'
import { readFileSync, writeFileSync, existsSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { createHash } from 'node:crypto'
import { createRequire } from 'node:module'

const HERE = dirname(fileURLToPath(import.meta.url))
const ROOT = resolve(HERE, '..')
const FIXTURE = join(ROOT, 'test', 'fixtures', 'dsh-slot-catalog.ts')
const UPSTREAM_REPO = 'deepseek-ai/deepseek-harness'
const UPSTREAM_PATH = 'packages/extensions/cordis-client-runner/src/client/slot-catalog.ts'

// 两种失败必须分得开（issue #143）：
//   2 = 内容不满足（快照过期 / catalog 不一致）
//   3 = 检查没跑起来（缺依赖、取不到上游）
// 同一个 exit code 承载两者，门禁就会把环境问题报成内容问题。
const EXIT_OUT_OF_STEP = 2
const EXIT_COULD_NOT_RUN = 3

function fail(msg, code = EXIT_OUT_OF_STEP) {
  console.error(`verify-slot-keys: ${msg}`)
  process.exit(code)
}

function fetchUpstream() {
  const out = execFileSync(
    'gh',
    ['api', `repos/${UPSTREAM_REPO}/contents/${UPSTREAM_PATH}`, '--jq', '.content'],
    { encoding: 'utf8' },
  ).trim()
  if (!out || out.startsWith('{"message"')) fail(`权威 catalog 不可得（gh api 失败）：${out.slice(0, 200)}`, EXIT_COULD_NOT_RUN)
  return Buffer.from(out, 'base64').toString('utf8')
}

function parseKeys(text) {
  return [...text.matchAll(/^\s*key: '([^']+)'/gm)].map((m) => m[1])
}

// 默认**只读**（issue #143）。一个叫 verify-* 的脚本不该默认改写它正在检查的东西 ——
// 会自我修复的门等于把漂移藏起来，还会把被检文件的重生成结果混进下一次 commit。
// 写盘是显式的第二个动作：`--refresh`。`--check` 保留为默认的同义词，向后兼容。
const REFRESH = process.argv.includes('--refresh')
const CHECK_ONLY = !REFRESH
const argPath = process.argv.slice(2).find((a) => !a.startsWith('--'))
let catalogText
let source
if (argPath) {
  if (!existsSync(argPath)) fail(`找不到 catalog 文件：${argPath}`)
  catalogText = readFileSync(argPath, 'utf8')
  source = argPath
} else {
  console.log(`fetching ${UPSTREAM_REPO}:${UPSTREAM_PATH} ...`)
  try {
    catalogText = fetchUpstream()
  } catch (err) {
    fail(
      `权威 catalog 不可得 —— 不做替代验证。\n` +
        `  原因：${String(err)}\n` +
        `  手工取法：gh api repos/${UPSTREAM_REPO}/contents/${UPSTREAM_PATH}`,
      EXIT_COULD_NOT_RUN,
    )
  }
  source = `${UPSTREAM_REPO}:${UPSTREAM_PATH} (live)`
}

const keys = parseKeys(catalogText)
if (keys.length === 0) fail('catalog 里一个 key 都没解析出来 —— 文件形状不对，拒绝继续')
const sha = createHash('sha256').update(catalogText).digest('hex').slice(0, 16)

console.log(`\nsource : ${source}`)
console.log(`sha256 : ${sha}`)
console.log(`keys   : ${keys.length}`)
console.log('--- authoritative slot keys ---')
for (const k of keys) console.log(`  ${k}`)

// 与快照对比
if (existsSync(FIXTURE)) {
  const snap = readFileSync(FIXTURE, 'utf8')
  const snapSha = createHash('sha256').update(snap).digest('hex').slice(0, 16)
  if (snapSha === sha) {
    console.log(`\nsnapshot: up to date (${snapSha})`)
  } else {
    const snapKeys = parseKeys(snap)
    const added = keys.filter((k) => !snapKeys.includes(k))
    const removed = snapKeys.filter((k) => !keys.includes(k))
    console.log(`\nsnapshot: STALE (snapshot ${snapSha} vs live ${sha})`)
    console.log(`  keys only in live   (${added.length}): ${added.join(', ') || '-'}`)
    console.log(`  keys only in snapshot(${removed.length}): ${removed.join(', ') || '-'}`)
    if (CHECK_ONLY) {
      fail(
        `fixture is stale (snapshot ${snapSha} vs live ${sha}) — ` +
          `${added.length} key(s) only in live, ${removed.length} only in snapshot. ` +
          `Run node scripts/verify-slot-keys.mjs --refresh to refresh.`,
      )
    }
    if (!argPath) {
      writeFileSync(FIXTURE, catalogText)
      console.log('  snapshot refreshed from upstream.')
    }
  }
} else if (!argPath && !CHECK_ONLY) {
  writeFileSync(FIXTURE, catalogText)
  console.log(`\nsnapshot written to ${FIXTURE}`)
} else if (CHECK_ONLY && !existsSync(FIXTURE)) {
  fail('fixture is missing and --check will not write it')
}

// ── regenerate src/ui/slot-catalog.ts from the same parse (issue #139) ────────
// 两份产物（fixture 与 src 的 CONFIRMED_SLOT_KEYS）曾经分开生成，于是 src 落后了
// 8 个 key 而没人发现（92 vs 100）。现在它们出自同一次 parse：keys 数为 N，两边
// 就都是 N，`CATALOG_PROVENANCE.keyCount` 也写 N —— 数字再对不上就没有来源了。
const SRC = join(ROOT, 'src', 'ui', 'slot-catalog.ts')
function regenerateSource(keys, shaHex, srcText) {
  // 用索引定位而不是正则：声明行里的 `readonly string[]` 含 `[]`，当正则用会
  // 被当成字符类（第一版就是这么没匹配上的）。
  const head = 'export const CONFIRMED_SLOT_KEYS: readonly string[] = ['
  const at = srcText.indexOf(head)
  if (at < 0) return { ok: false, why: 'CONFIRMED_SLOT_KEYS declaration not found' }
  const close = srcText.indexOf('\n]', at)
  if (close < 0) return { ok: false, why: 'CONFIRMED_SLOT_KEYS block is not closed' }
  const sorted = [...keys].sort()
  const body = sorted.map((k) => `  '${k}',`).join('\n')
  let out = srcText.slice(0, at) + head + '\n' + body + srcText.slice(close)
  const now = new Date().toISOString().slice(0, 10)
  out = out
    .replace(/blobSha: '[^']*'/, `blobSha: '${shaHex}'`)
    .replace(/keyCount: \d+/, `keyCount: ${keys.length}`)
    .replace(/fetchedAt: '[^']*'/, `fetchedAt: '${now}'`)
  return { ok: true, text: out, count: keys.length }
}

if (existsSync(SRC)) {
  const srcText = readFileSync(SRC, 'utf8')
  const regen = regenerateSource(keys, sha, srcText)
  if (!regen.ok) fail(`无法重新生成 src/ui/slot-catalog.ts：${regen.why}`)
  const before = (srcText.match(/^  '[^']+',$/gm) || []).length
  if (regen.text !== srcText) {
    if (CHECK_ONLY) {
      const keyDiff =
        before === regen.count
          ? `both have ${before} keys, so the drift is in the provenance block (keyCount / blobSha / fetchedAt)`
          : `${before} key(s) in the snapshot vs ${regen.count} parsed`
      fail(`src/ui/slot-catalog.ts is out of step with the authority — ${keyDiff}. Run node scripts/verify-slot-keys.mjs --refresh to regenerate.`)
    }
    if (!argPath) {
      writeFileSync(SRC, regen.text)
      console.log(`\nsrc/ui/slot-catalog.ts: regenerated ${before} -> ${regen.count} keys (keyCount=${regen.count})`)
    } else {
      console.log(`\nsrc/ui/slot-catalog.ts: would regenerate ${before} -> ${regen.count} keys (dry run, --file mode)`)
    }
  } else {
    console.log(`\nsrc/ui/slot-catalog.ts: already in step (${regen.count} keys)`)
  }
}

console.log('\n--- running non-circular alignment test (apply() vs parsed authority) ---')
const vitestBin = join(ROOT, 'node_modules', '.bin', 'vitest')
const testFile = join(ROOT, 'test', 'slot-catalog.test.ts')
if (!existsSync(vitestBin)) {
  // 缺依赖不是「快照过期」。门禁必须能把这两件事分开报（issue #143）。
  fail(
    `alignment test could not run — vitest not found at ${vitestBin}. ` +
      `Run \`pnpm install\` first. This is an environment problem, not a catalog mismatch.`,
    EXIT_COULD_NOT_RUN,
  )
}
// vitest 二进制在、但模块解析不了（没跑 pnpm install 时 react 不在）——那不是
// catalog 的结论，是环境没准备好。第一版只查了二进制，于是 import 失败仍被归到
// exit 2，一个干净 checkout 的人会照着「快照与权威不一致」去找不存在的 bug。
// （PR #146 复核指出的漏点。）
try {
  createRequire(import.meta.url).resolve('react')
} catch {
  fail(
    'alignment test could not run — react is not installed. ' +
      'Run `pnpm install` first. This is an environment problem, not a catalog mismatch.',
    EXIT_COULD_NOT_RUN,
  )
}

let vitestOut = ''
try {
  vitestOut = execFileSync(vitestBin, ['run', testFile, '--reporter=verbose'], {
    cwd: ROOT,
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe'],
  })
} catch (err) {
  vitestOut = String(err.stdout ?? '') + String(err.stderr ?? '')
  // 收集期失败（import / 模块解析 / 转译）与断言失败是两件事。前者归 3，后者归 2 ——
  // 否则「测试跑不起来」会被读成「快照不对」，把人支去改 catalog。
  const collectionFailure =
    /Failed to resolve entry|Cannot find module|Failed Suites|ERR_MODULE_NOT_FOUND|Transform failed/i.test(
      vitestOut,
    )
  console.error(vitestOut.split('\n').slice(-12).join('\n'))
  if (collectionFailure) {
    fail(
      'alignment test could not run — the test module failed to load. ' +
        'This is an environment problem, not a catalog mismatch.',
      EXIT_COULD_NOT_RUN,
    )
  }
  fail('alignment test FAILED — the injected keys do not all exist in the authority')
}
console.log(vitestOut.split('\n').filter((l) => /Tests |Test Files |passed|failed/.test(l)).join('\n'))
console.log('\nverify-slot-keys: OK — every injected key exists in the authority.')
