---
type: PR Case Study
title: honcho PR #801 - queue purge endpoint for stranded work units
description: zsxh1990 在 honcho 提的 queue purge PR，含 FastAPI DB session 陷阱复盘
pr_number: 801
pr_url: https://github.com/plastic-labs/honcho/pull/801
repo: plastic-labs/honcho
author: zsxh1990
status: open
opened_at: 2026-06-12
last_activity: 2026-06-20
tags:
  - pr-case-study
  - open
  - fastapi-trap
  - sqlalchemy-async
  - coderabbit-reviewed
related:
  - ../index.md
related_issues:
  - https://github.com/plastic-labs/honcho/issues/799
---

# honcho PR #801: feat: add queue purge endpoint for stranded work units

> zsxh1990 在 [plastic-labs/honcho#801](https://github.com/plastic-labs/honcho/pull/801) 的 queue purge PR 案例深读。  
> **状态**：🟢 open（19 天）  
> **核心价值**：暴露了 FastAPI + SQLAlchemy 异步注入陷阱，已被 MEMORY.md §8 收录。

---

## PR 内容

**问题**：[#799](https://github.com/plastic-labs/honcho/issues/799) - stranded work units（stranded = 队列里卡住的工作单元）无清理机制  
**方案**：新增 `/queue/purge` 端点 + 列出 stranded items 的 GET 端点  
**规模**：+283 lines / 3 files

---

## 关键 Bug 复盘（CodeRabbit 抓的）

### 🐛 Bug 1: FastAPI default value = module 陷阱

**错的代码**：
```python
from src import db, models  # ❌ 这里 db 是 module！

@router.post("/queue/purge")
async def purge_queue(db: AsyncSession = db):  # ❌ 不是 Depends(get_db)
```

**为什么错**：
- `from src import db` 的 `db` 是 `src/db.py` module 对象
- `db: AsyncSession = db` 实际等价于 `db: AsyncSession = src.db`（module）
- FastAPI 拿到的是 module，不是 `AsyncSession`
- 运行时 type check 通过（mypy 不查 default value 类型），但 `db.execute(...)` 调 module 属性会炸

**修法（zsxh1990 commit `7ac3afe`）**：
```python
from src.dependencies import db  # ✅ Depends(get_db) 的代理

@router.post("/queue/purge")
async def purge_queue(db: AsyncSession = Depends(db)):  # ✅
```

### 🐛 Bug 2: select().scalars().all() 模式

**错的代码**：
```python
count = len(db.execute(select(WorkUnit)).scalars().all())
```

**问题**：
- 拉所有行到 Python 端只为 count
- 大表 OOM 风险
- CodeRabbit 必抓

**修法（一行）**：
```python
count = db.execute(select(func.count()).select_from(WorkUnit)).scalar_one()
```

---

## zsxh1990 第 2 轮 amend 后的状态

- ✅ Bug 1 修复
- ⚠️ Bug 2 已修但 CodeRabbit 6/20 又提 1 个新 finding（细节未深读）
- 🟢 CodeRabbit 反馈整体已解决
- ❌ **maintainer 真实 review 未开始**（19 天等待）

---

## 下一步行动（候选）

**A. 主动 close**  
理由：等 19 天无 maintainer 回应，参考 OpenClaw ClawSweeper 7 天优雅退出原则。  
但是 honcho 没有自动 close bot，**主动 close 比挂着好**（释放注意力）。

**B. 再 amend + check-in**  
zsxh1990 在 7/1 发条："Friendly check-in — addressed all CodeRabbit findings. Happy to make any adjustments."  
风险：撞到 Plastic Labs 维护者忙期，回复慢。

**C. 等待维护者主动 review**  
被动等，参考 RailtownAI/railtracks#1190 模式（6/15 承诺 review 但 6/30 未到）。

**建议**：先 B（再 check-in），等 7 天无回应就 A（close）。

---

## 关联文档

- [honcho 仓 Profile](../index.md)
- [OKF bundle 根入口](../index.md)
- [MEMORY.md §8 PR 默认参数陷阱](../../../MEMORY.md)
- [MEMORY.md §9 select().scalars().all() ORM anti-pattern](../../../MEMORY.md)