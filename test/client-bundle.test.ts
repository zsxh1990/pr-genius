/**
 * 验收判据 1（issue #159）：`npm pack` 的 tarball 里必须有浏览器端 client 产物。
 *
 * 为什么这条判据不需要真 DSH 宿主就能挡下八个 bug：八次「空壳安装」
 * （#86 #90 #95 #97 #98 #100 #101 #117）全都是**装到真 web 宿主里四个面不出现**，
 * 而根因是 `package.json` 声明了 `dsh.client` 却没有 `exports["./client"]` ——
 * DSH 的 `client-modules` 会静默把插件从 client graph 里丢掉。
 *
 * 「声明了但没发货」这件事**在打包时就看得见**，不需要任何人的眼睛进宿主。
 * 所以判据放在 tarball 上，不放在渲染上。
 */
import assert from 'node:assert/strict'
import { execFileSync } from 'node:child_process'
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { describe, it } from 'vitest'

const HERE = dirname(fileURLToPath(import.meta.url))
const REPO_ROOT = join(HERE, '..')

function pkg(): Record<string, any> {
  return JSON.parse(readFileSync(join(REPO_ROOT, 'package.json'), 'utf8'))
}

describe('package.json declares the client half', () => {
  it('exports a "./client" entry', () => {
    const exports = pkg().exports ?? {}
    assert.ok(
      exports['./client'],
      'dsh.client is declared but exports has no "./client" — DSH will silently drop ' +
        'the plugin from the client graph (issue #159)',
    )
  })

  it('the ./client export points at a real file, not just a key', () => {
    const spec = pkg().exports['./client']
    const target = typeof spec === 'string' ? spec : (spec?.default ?? spec?.browser)
    assert.ok(typeof target === 'string' && target.startsWith('./'),
      `./client must resolve to a relative path, got ${JSON.stringify(spec)}`)
  })

  it('dsh.client and ./client agree — declaring one without the other is the bug', () => {
    const p = pkg()
    const declaresClient = Boolean(p.dsh?.client && p.dsh.client.platform === 'web')
    const shipsClient = Boolean(p.exports?.['./client'])
    assert.equal(declaresClient, shipsClient,
      'dsh.client (platform: web) and exports["./client"] must come as a pair. ' +
        `declared=${declaresClient} shipped=${shipsClient}`)
  })
})

describe('the shipped client artifact matches what DSH loads', () => {
  // 这条真的 build + pack，慢一点但它是判据本身。DSH 的 client bundle 形态是
  // `window.__ModuleLoader__.load({ id, factory })`，**不是**标准 IIFE 也不是裸 ESM：
  // factory 内部是 CJS（`var module = {exports:{}}` / `require()` / `return module.exports`）。
  // 照这个形状发，宿主才认。
  it('npm pack contains a client artifact wrapped for __ModuleLoader__', () => {
    const out = execFileSync('npm', ['pack', '--dry-run', '--json'], {
      cwd: REPO_ROOT,
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'pipe'],
      timeout: 180_000,
      env: { ...process.env, npm_config_ignore_scripts: 'true' },
    })
    const report = JSON.parse(out)
    const files: string[] = (report[0]?.files ?? []).map((f: { path: string }) => f.path)

    const client = files.find((f) => /(^|\/)client.*\.(m?js|cjs)$/.test(f) && !f.includes('.map'))
    assert.ok(client, `tarball has no client bundle. files=${files.filter(f => f.endsWith('.js') || f.endsWith('.mjs')).join(', ')}`)

    // 形状判据：必须是 __ModuleLoader__ 的 factory 形态。
    const body = readFileSync(join(REPO_ROOT, client), 'utf8')
    assert.match(body, /window\.__ModuleLoader__\.load\(\s*\{/,
      'DSH client bundles are wrapped in window.__ModuleLoader__.load({id, factory}) — a bare ESM or IIFE will not be loaded')
    assert.match(body, /factory:\s*\(require\)\s*=>/,
      'the factory receives `require` so host-provided deps (react, cordis) resolve at runtime')
    assert.match(body, /id:\s*["'][^"']+["']/, 'the loader needs the package id')

    // 不能把 node 专属依赖拖进来 —— 那正是 #159 说「不是换个 target 就行」的原因。
    assert.doesNotMatch(body, /require\(["']node:/,
      'the client bundle must not require node: built-ins — kb.ts / mcp-client.ts are node-only')
    assert.doesNotMatch(body, /from\s+["']node:/,
      'the client bundle must not import node: built-ins')
  }, 200_000)
})
