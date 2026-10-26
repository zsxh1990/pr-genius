/**
 * 类型声明 —— `slot-catalog.mjs` 的对外契约。
 *
 * 这个模块是发版 gate 的 slot 名唯一来源；签名写在这里，免得调用方靠猜。
 */

export interface SlotCatalogEntry {
  key: string
  kind: string
  scope: string
  registerOptions: Array<{ name: string; requirement: string }>
  replaceRisk: string | null
  declaredBy: string | null
  occupants: string[]
  source: string | null
  summary: string | null
}

export interface SlotCatalogProvenance {
  kind: 'installed-sdk-bundle' | 'upstream-source' | 'upstream-source-parsed-fallback' | 'local-snapshot'
  package?: string
  packageVersion?: string
  packageDir?: string
  file?: string
  exportName?: string
  upstreamModule?: string
  repo?: string
  ref?: string
  path?: string
  note?: string
}

export interface LoadedCatalog {
  ok: boolean
  source: 'npm' | 'github' | 'file'
  provenance: SlotCatalogProvenance
  entries: SlotCatalogEntry[]
  reason?: string
}

export interface CatalogAttempt {
  source: string
  ok: boolean
  reason: string | null
  count: number
}

export interface SlotCatalogResult {
  ok: boolean
  primary: LoadedCatalog | null
  crossCheck: LoadedCatalog | null
  attempts: CatalogAttempt[]
  error: string | null
}

export interface CatalogDiff {
  aSource: SlotCatalogProvenance
  bSource: SlotCatalogProvenance
  aCount: number
  bCount: number
  onlyInA: string[]
  onlyInB: string[]
  kindOrScopeChanged: Array<{ key: string; a: string; b: string }>
}

export interface HardcodeOffender {
  file: string
  key: string
  line: number
}

export declare const UPSTREAM: {
  repo: string
  ref: string
  path: string
  npmPackage: string
}

/** 从 JS/TS 源码静态切出 `const NAME = <array literal>` 并求值。 */
export declare function extractArrayLiteral(source: string, marker: string): unknown[]

/**
 * 把 `execFileSync('gh', …)` 的失败压成一句可分诊的 reason（issue #149）。
 *
 * 必须带退出码 / 信号 / stderr 首行（gh 把 HTTP 码打在那），且「gh 压根没起来」
 * 与「gh 跑了但失败」要分得开 —— 前者没有 HTTP 码，不替它编一个。
 */
export declare function describeGhFailure(
  err: unknown,
  target: { repo: string; ref: string; path: string },
): string

export declare function loadSlotCatalog(opts?: {
  source?: 'auto' | 'npm' | 'github' | 'file'
  cwd?: string
  file?: string
}): Promise<SlotCatalogResult>

export declare function diffCatalogs(a: LoadedCatalog, b: LoadedCatalog): CatalogDiff

/**
 * 反循环自检：gate 源码里不得出现权威 catalog 的 slot 名字面量。
 * 出现即 `ok: false` 并列出 `offenders`。
 */
export declare function assertNoHardcodedSlotKeys(
  fileSources: Array<{ file: string; source: string }>,
  catalogKeys: string[],
): { ok: boolean; offenders: HardcodeOffender[] }
