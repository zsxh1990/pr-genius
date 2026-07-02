---
type: Anti-Pattern
key: honcho-default-db-module-trap
symptom: "FastAPI route 默认参数 `db: AsyncSession = db` 在生产环境报 'coroutine expected' 或 'no attribute execute'"
root_cause: "Python import 命名冲突：`from src import db` 的 `db` 是 module 本身（无 AsyncSession），而 `from src.dependencies import db` 的 `db` 才是 Depends(get_db) 代理。两者同名，default value 默默选中前者"
trigger_keywords:
  - "AsyncSession"
  - "coroutine expected"
  - "no attribute execute"
  - "default value"
  - "Depends(get_db)"
  - "select().scalars().all()"
fix_action: "1) 用 basedpyright 验证 default value 类型匹配；2) 改用 Annotated[AsyncSession, Depends(get_db)] 显式声明；3) 改 ORM count 写法 select(func.count())"
fix_command: "basedpyright src/routers/<file>.py && git diff"
source_pr: plastic-labs/honcho#801
prevention: "提 PR 前必用 basedpyright 验证；或参考仓里其他 router 的同模式（搜 'AsyncSession = Depends' 看正确写法）"
learned_at: 2026-07-02
---

# honcho-default-db-module-trap

## 现象

提 PR 到 plastic-labs/honcho（FastAPI + SQLAlchemy 2.0 async），CodeRabbit 自动审发现：

```
L16: db: AsyncSession = db  # 默认值类型不匹配
```

PR 实际运行时也会撞：
- `TypeError: object AsyncSession can't be used in 'await' expression`
- `AttributeError: module 'src.db' has no attribute 'execute'`

## 根本原因

Python import 命名冲突：

```python
# 错误（看起来对，实际错）
from src import db, models  # ❌ 这里的 db 是 module，不是 Depends 代理

def endpoint(db: AsyncSession = db):  # 默认值拿到的是 src.db module
    ...
```

```python
# 正确
from src.dependencies import db  # ✅ 这里的 db 是 Depends(get_db) 代理

def endpoint(db: AsyncSession = db):  # 默认值是 FastAPI Depends 包装
    ...
```

**两者同名 = 灾难**。Python 不会报错，类型检查不严的话也发现不了，直到生产调用。

## 自愈脚本

### 修复 1：default 参数写法

```python
# 旧（错）
def endpoint(db: AsyncSession = db):

# 新（Python 3.9+ 推荐写法）
from typing import Annotated
from fastapi import Depends
from src.dependencies import get_db

def endpoint(db: Annotated[AsyncSession, Depends(get_db)]):
```

### 修复 2：ORM count anti-pattern

```python
# 旧（错）
total = len(db.execute(select(Model)).scalars().all())

# 新（对）
from sqlalchemy import func
total = db.execute(select(func.count()).select_from(Model)).scalar_one()
```

## 预防

提 PR 前**必跑**：

```bash
# 1. 类型检查（基于 pyright）
basedpyright src/

# 2. 搜仓里其他 router 的正确模式
grep -rn "AsyncSession = Depends" src/
```

## 教训来源

- [plastic-labs/honcho#801 (queue purge endpoint)](../plastic-labs-honcho/pr-801-queue-purge.md)
- CodeRabbit 2026-06-12 第 1 轮 review 命中
- zsxh1990 2026-06-20 自报修复
- MEMORY.md §8 已内化

## 相关反模式

- 无（FastAPI + SQLAlchemy 2.0 特定）