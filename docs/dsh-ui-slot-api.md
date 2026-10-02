---
type: Reference
title: DSH UI slot / 侧边栏 / 设置面 API — 权威速查
tags: [dsh, cordis, ui-slots, sidebar, reference]
description: "从 dshfind 官方教程抽取的 UI slot 清单、注册 API 形态、设置面与宿主通信契约；供插件 UI 层实现与复核使用"
created: 2026-10-02
updated: 2026-10-02
confidence: high
---

# DSH UI slot / 侧边栏 / 设置面 API 速查

> 来源：dshfind 官方学习中心 `core/12-web-ui`、`dev/02-write-tool`、`dev/03-write-service`、
> `dev/05-config-publish`、`core/11-plugin-anatomy`、`plugin/03-how-to-build`。
> 本机无 `DEEPSEEK_API_KEY`，**未在运行时验证**；下列为契约摘录，实现时按此对齐，
> 运行时行为需在真 DSH 环境另行确认。

## 1. 插件本体契约

在 `src/index.ts` 导出三件东西，框架 `ctx.use` 实例化为带生命周期的 fiber——
**加载即生效、卸载即还原**（注册都是 effect、自动清理）。

```ts
import type { Context } from 'cordis'
import Schema from 'schemastery'

export const name = 'pr-genius'

export interface Config {
  /* 可调参数 —— 每个都要过「能否在 cordis.yml 里改而不动代码」这道检验 */
}

export const Config: Schema<Config> = Schema.object({
  /* 字段 + .default(...)；类型与 schema 必须同名 */
})

export const inject = [/* 我需要什么 */]

export function apply(ctx: Context, config: Config) {
  /* 我贡献什么 */
}
```

⚠️ 不要导普通对象当 `Config`——不满足 Cordis 的 Standard Schema 接口，插件无法校验。

### 两条设计原则（官方原文）

| 原则 | 检验标准 |
|---|---|
| **无硬编码可调参数** | 「能否在 `cordis.yml` 中改变这个值，而不需要修改代码？」不能就提成配置字段 |
| **配置错误要响亮** | schema 在**加载时**校验；配置不合法 → **加载失败并给明确错误**，不带病运行 |

配置变更 → 触发该插件**增量热替换**（卸旧装新），不需要重启。只有被改的那个插件重装配。

## 2. UI slot 清单（页面上的空位）

**界面 = 空位（slot）+ 填进来的插件。** 插件被组合掉，界面就消失，其余毫发无损。

| slot | 它是页面上的什么空位 | 谁往里填 |
|---|---|---|
| `root` | 整个应用的根 | `ui-layout`（三栏 AppFrame） |
| `conversation.chat.node` | 聊天流里的一行节点 | `ui-conversation`、`ui-tool` 及一切 Chat 节点插件 |
| `conversation.input.dock` | 输入区上方的卡片栈 | `ui-conversation`（TodoDock）、`ui-goal`（GoalBar）、Queue |
| **`conversation.view`** | **会话视图的标签页** | 聊天视图、`ui-trajectory` 等 |

> **`conversation.view` 就是 dsh-context「Context tab」的落点** —— 我们的「顾问 Tab」应挂在这里。

### 注册 API 形态

```ts
ctx.slots.inject('conversation.chat.node', () => ctx.slots.register({
  name, children?, store?, inject?, ...kind
}, Component))
```

- 声明 = 渲染授权 = 运行时规范，三者共用一张表
- `SlotsService` 包装 slot 注册表，为 renderer 提供数据源
- 前端插件卸载时，其贡献的组件、注册的 slot 条目、挂的 store **一并递归撤销**
  （`ui-slots` 的 disposer 会递归移除其声明的子 slot）

## 3. 设置面（Preferences / Configuration 的落点）

| 包 | 职责 |
|---|---|
| `ui-sidebar` | Workspace 与会话导航 |
| `ui-settings` | 设置总入口 |
| `ui-settings-general` | 通用设置 |
| `ui-settings-models` | 模型设置 |
| **`ui-settings-plugins`** | **插件设置** ← dsh-context 的 Preferences 卡落点 |
| **`ui-settings-plugin-inventory`** | 当前 Loader 条目的只读投影 |

dsh-context 的做法（照此实现）：

- **dsh 0.1.7+**：侧边栏 `Plugins` 条目 → 本插件 bundle 页 → 其 `Configuration` 段（由该条目的 live Config form 提供）
- **更早版本**：`Settings → Plugins → Plugin configuration` → 本插件的卡片
- 图内/卡内切换**只作用于当前视图，不覆盖已存偏好**

## 4. 其它注册面

| 能力 | API |
|---|---|
| 工具 | `ctx.tools.register(defineTool({ ... }))` —— 注册后 schema 自动流入系统提示词组装，模型下一轮可见 |
| 命令 | `ctx.command`（斜杠命令） |
| 聊天节点 | `ctx.conversationEvents.register(reviewDefinition)` + `ConversationNodeDefinition` + keyed renderer |
| LLM 适配器 | `ctx.llm.registerAdapter(模型名列表, adapter)` |

## 5. 宿主通信契约

- 浏览器「问一件事」→ **HTTP POST** 的 RPC（unary / respond）
- 宿主「推一件事」→ **两条只下行的 WebSocket**（`events.mux` 与 `events.host`）
- 宿主侧由 `ctx.agents` 驱动智能体，每步动作追加进 `session/event` 事件流，顺 WebSocket 推给浏览器
- **界面是插件的组合，日志是界面的数据源**

宿主侧包与 ctx 键：

| 包 | 职责 | ctx 键 |
|---|---|---|
| `apiproxy/` | 共享宿主 API 网关与协议约定 | `ctx.apiProxy` |
| `webserver/` | HTTP 路由载体 | `ctx.webServer` |
| `frontend-static/` | SPA dist 服务器（占 webserver 回退席位） | 消费 `ctx.webServer` |
| `directory-picker/` | 工作区目录选择 seam（native/browse/auto 三后端） | `ctx.directoryPicker` |
| `plugin-inventory/` | Loader 条目只读投影 | Remote `pluginInventory/list` |

### Typert API Gateway（类型安全地调宿主方法）

```ts
export class GoalService extends TypertRemoteService {
  constructor(ctx: Context) { super(ctx, 'goals') }
  @Remote('create')
  async createGoal(agent: Agent, request: CreateGoalRequest): Promise<CreateGoalResult> { /* … */ }
}
```

- 业务服务继承 `TypertRemoteService`，方法打 `@Remote('create')` / `@RemoteScope(key)`
- **只有被标记的方法**才进生成的 Client 类型与运行时贡献
- Host 侧拿 `ctx.typertGateway`，浏览器侧拿 `ctx.remote`，两边共用同一份 `InvocationDescriptor`
- 复杂宿主对象（如 `Agent`）不能直接过线 —— 用 `TypertLookupMap` 声明与线上身份的关联
  （Host 签名里名为 `agent` 的参数会生成 `agentId` 线上字段）

## 6. 开发环境

| 需要 | 版本 |
|---|---|
| Node.js | `^22.19` 或 `>= 24` |
| pnpm | 11（Corepack 启用） |
| API 密钥 | `DEEPSEEK_API_KEY` |
| 仓库 | `deepseek-ai/deepseek-harness-sdk` → `pnpm install && pnpm run build` |
| 启动 | `pnpm run dsh web` → `http://127.0.0.1:3080` |

改代码 → **热模块替换，无需重启**。

## 7. 发布

插件打包成标准**组合包**（`dsh.bundle` 指向 `cordis.patch.yml`），别人一条命令装上、在配置里装配：

```bash
dsh plugin --profile <你的profile> add pr-genius          # 安装
dsh plugin --profile <你的profile> update pr-genius@latest # 更新
```

或 Web 向导：`Add plugin` 搜索框输入 `pr-genius` → `Install`。

> **git 源码安装的坑**（pr-genius 当前就踩着）：pnpm ≥ 10 首次安装会拒跑 git 依赖的 `prepare`
> 脚本，需在该 profile 的 `pnpm-workspace.yaml` 里写 `allowBuilds` 授权——这等于允许该包的代码
> 在你机器上执行，建议同时用 `#commit` 锁版本。**发到 npm 后这句就该消失。**
