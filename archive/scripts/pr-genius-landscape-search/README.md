---
type: Research Report
title: pr-genius Landscape Search — PR 同类仓调研脚本集
description: 一次性研究脚本归档（克莱恩 2026-07-19 00:11 GMT+8 拍板沉淀，按 7/2 归档策略）。用于扫 PR 相关同类仓（PR coach / OKF bundle / good-first-issue / vibe-coding 类）。
version: 1.0.0
created: 2026-07-19
---

# pr-genius-landscape-search

> 一次性研究脚本归档：扫 PR 相关同类仓的可复用工具集。
> 克莱恩 2026-07-19 00:11 GMT+8 拍板沉淀（按 7/2 归档策略）。

## 用途

扫 pr-genius 的潜在同类仓（PR coach / OKF bundle / good-first-issue / vibe-coding 类），用于回答「pr-genius 在赛道里相对定位是什么」、「要不要做教程分册 / 互链」这类问题。

## 调用方法

### 单跑任一搜索

```bash
cd /path/to/pr-genius/archive/scripts/pr-genius-landscape-search/

# 1. PR coach / advisor / analyzer
./search_pr_coach.sh

# 2. vibe-coding / AI-assisted PR
./search_vibe_coding.sh

# 3. OKF bundle / agent-first markdown knowledge
./search_okf_bundle.sh

# 4. good-first-issue / first contribution（撞 rate limit 时会 sleep 30 自动重试）
./search_good_first_issue.sh

# 5. 抓单仓完整 profile（topics + meta + README 头 2000 字）
./fetch_repo_profile.sh owner/repo           # 默认抓 topics + meta + README
./fetch_repo_profile.sh owner/repo HALL_OF_FAME.md   # 抓任意路径文件（绕 raw.githubusercontent.com timeout）
```

### 自定义

```bash
PER_PAGE=30 ./search_pr_coach.sh
RETRY=0 ./search_good_first_issue.sh   # 撞 rate limit 不重试
```

## 设计要点

- **零依赖**：纯 bash + python3 stdlib
- **零 token**：全部走 GitHub 匿名 API（限速 search 10/min + core 60/h，够调研用）
- **零副作用**：纯只读 curl，不写仓、不发评论、不动 PR
- **撞 rate limit 自动 sleep**：Q5（good-first-issue）命中前撞过 1 次 reset，所以加了 RETRY_SLEEP 默认值
- **README 抓核心 API**：避开 `raw.githubusercontent.com` 的偶发 15s timeout（多次验证过）
- **topics 字段顺藤摸瓜**：Q3 OKF 跑出的 `agenticnotetaking/arscontexta` + `1st1/lat.md` 是核心同形候选，靠 topics 字段识别

## 调研执行历史（半诚实交底）

| 时间 | 状态 |
|---|---|
| 2026-07-18 23:55 GMT+8 | 克莱恩指令触发 |
| 2026-07-18 23:55 - 2026-07-19 00:10 GMT+8 | 跑 19 个 search 角度 + 5 个 README core API 抓取 |
| 2026-07-19 00:10 GMT+8 | 写完 `D:\MD\pr-genius\landscape.md`（v1） |
| 2026-07-19 00:13 GMT+8 | 克莱恩拍板 A+C（沉淀脚本 + 抓 ContribAI HALL_OF_FAME 补 v2） |
| 2026-07-19 00:16 GMT+8 | 5 个脚本归档完成 |
| 2026-07-19 00:18 GMT+8 | v2 report 写入 `D:\MD\pr-genius\landscape-v2.md` |

## 网络/PAT 限制（拍板前提）

- ❌ ikalus1988 PAT 401 失效
- ❌ zsxh1990 PAT 没本地副本（飞书消息过期未存盘）
- ❌ web_search 没 provider
- ❌ web_fetch HTML 抓取 15s timeout
- ❌ Clash 7890 已死（按 MEMORY 7/7 验证）
- ✅ GitHub 匿名 API 直连（0.5-0.6s）
- ✅ 匿名 core API 60/h 够调研
- ✅ 匿名 search API 10/min，撞 1-2 次 reset 不影响

## 已知撞坑（避免下次再撞）

1. **`good-first-issue` query** 撞 rate limit 时直接返 0 / `total_count: None`，不要立即判定「无同类」——`RETRY_SLEEP=30` 后再跑
2. **`raw.githubusercontent.com` 偶发 15s timeout**—— 走 core API `/contents/<path>` 更稳
3. **不要 `*.sh` 通配符 chmod**——文件路径含空格时通配符展开顺序不稳，逐个 chmod 或 `find ... -exec chmod`
4. **不要相信 search top 命中**——很多 noise（terminal / file manager / CRM），必须读 README 验证「是不是真同类」

## 输出协议

5 个脚本全部 stdout 输出，按 `<stars> <full_name> <description>` 三列格式。适合 `| grep`、`| sort`、`| column -t` 后处理。

```bash
# 实战：所有 search 结果合一去重
for s in search_*.sh; do
  echo "=== $s ==="
  bash "$s"
done > /tmp/all_hits.txt
grep -v "^===" /tmp/all_hits.txt | awk '{print $2}' | sort -u
```

## 关联

- `D:\MD\pr-genius\landscape.md` — v1 报告（5 类相似仓 + 维度对位 + 3 个值得跟的方向）
- `D:\MD\pr-genius\landscape-v2.md` — v2 报告（v1 + arscontexta / lat.md / OKF Conformance / ContribAI 完整数据）
- `D:\MD\pr-genius\README.md` — 目录入口
- `MEMORY.md` §归档策略 — 克莱恩 2026-06-26 拍板
- `MEMORY.md` §pr-genius 沉淀 — 克莱恩 2026-07-02 拍板