---
type: Schema Reference
title: Lesson Source Credibility Scoring
description: 4 维度评分系统 — 源可信度 + 细节质量 + 通用化 + 脱敏度
version: 0.1.0
created: 2026-07-03
---

# Lesson Source Credibility Scoring v0.1

> 克莱恩 2026-07-03 00:57 拍板：lesson **不要求真实**，但要求 **置信度评分**。
> 评分判断"过程描述是否详尽 / 细节是否值得推敲 / 源是否权威"。

## 4 维度（100 分）

### 1. 源可信度（30 分）

| 等级 | 分值 | 标准 |
|---|---|---|
| **S (25-30)** | 自己亲历 / 自己的 git log / 自己的 install log | 可在 git log / memory / agent 输出中复现 |
| **A (20-24)** | 权威仓库 issue / 官方 docs / 知名维护者回复 | GitHub 官方仓 / 公司技术博客 / 知名工程师 |
| **B (15-19)** | 高赞论坛帖 / 多回复讨论 | V2EX ≥50 reply / HN ≥50 upvote / Reddit ≥100 upvote |
| **C (10-14)** | 中等讨论 / 个人博客 | 单人经验文 / Stack Overflow 中等赞同 |
| **D (0-9)** | 营销文 / AI 生成 / 未知源 | 不接受进 lesson |

**减分项**：
- 帖中含 `AI` 标签 / `bot:ai-policy-comment` 类自动评论 → -5
- 帖已被删除 / 链接 404 → -10
- 帖年龄 > 2 年 → -3（除非主题稳定）
- 单一作者 / 单一赞 → -5

### 2. 细节质量（25 分）

| 项 | 分值 | 标准 |
|---|---|---|
| 有具体场景/复现步骤 | 5 | 写得出"我做了 X，撞了 Y 错误" |
| 有可粘贴的命令/代码 | 8 | 命令、配置、SQL、JSON |
| 有具体错误信息/日志 | 5 | 真实报错文本或日志片段 |
| 解释 *为什么* 而不只是 *怎么做* | 4 | Root Cause 段 |
| 有横向对比 / 备选方案 | 3 | 表格或列举 |

### 3. 通用化（25 分）

| 项 | 分值 | 标准 |
|---|---|---|
| 可被**其他 Agent** 复用 | 10 | 不绑死特定人/特定公司 |
| 不绑死特定版本/特定日期 | 5 | 抽象出原理，而非时间快照 |
| 有可类比 / 可推广场景 | 5 | 同一原理在不同栈适用 |
| 不重复 misakanet 已收录 lesson | 5 | grep `lessons/contrib` 无重叠 |

**减分项**：
- 含"我们公司"、"我们项目"类内部措辞 → -5
- 含组织名（小米 / 阿里 / 字节等）→ -5

### 4. 脱敏度（20 分）

| 项 | 分值 | 标准 |
|---|---|---|
| 无 API key / PAT / token | 8 | 完整检查 |
| 无真实域名/IP | 5 | 替换为 `example.com` / 占位符 |
| 无真实邮箱/手机号 | 4 | 替换为 `user@example.com` |
| 无内部 codename / 项目代号 | 3 | 替换为通用描述 |

**自动扣分**：
- 含 `ghp_*` / `sk_*` / `AKIA*` / `AIza*` 模式字符串 → -10
- 含真实中国手机号 (1[3-9]\d{9}) → -10
- 含真实邮箱 → -5
- 含私域域名 (.internal / .corp / .local) → -5

## 评级标准

| 等级 | 总分 | 处理 |
|---|---|---|
| **A** | ≥ 85 | 直接入库候选，可推送 misakanet |
| **B** | 75-84 | 入库候选，可推送（如细节可补 → 升级 A）|
| **C** | 60-74 | 留 pr-genius，不推送 misakanet |
| **D** | < 60 | 拒收 |

## 自动评分脚本（v0.1）

```python
def score_lesson_source(source_url, content):
    """Score a lesson's source credibility. Returns dict."""
    score = 0
    breakdown = {}

    # 1. 源可信度 (30)
    source_score = 0
    if source_url.startswith("file://") or source_url.startswith("git://"):
        source_score = 28  # own experience
    elif "github.com" in source_url and "/issues/" in source_url:
        source_score = 24  # GitHub issue
    elif "github.com" in source_url and "/discussions/" in source_url:
        source_score = 22  # GitHub discussion
    elif "github.com" in source_url and is_official_maintainer_author(source_url):
        source_score = 25  # Maintainer reply
    elif "v2ex.com" in source_url or "news.ycombinator.com" in source_url:
        reply_count = get_post_replies(source_url)
        if reply_count >= 50: source_score = 18
        elif reply_count >= 20: source_score = 15
        elif reply_count >= 5: source_score = 10
        else: source_score = 5
    else:
        source_score = 8  # Unknown source

    # Auto deductions
    if contains_ai_label(content): source_score -= 5
    if is_deleted(source_url): source_score -= 10

    breakdown["source"] = min(source_score, 30)
    score += breakdown["source"]

    # 2. 细节质量 (25)
    detail_score = 0
    if re.search(r'(error|fail|exception|crash|timeout|traceback)', content, re.I):
        detail_score += 5
    if has_code_block(content): detail_score += 8
    if has_specific_log(content): detail_score += 5
    if has_root_cause_explanation(content): detail_score += 4
    if has_comparison_table(content): detail_score += 3

    breakdown["detail"] = min(detail_score, 25)
    score += breakdown["detail"]

    # 3. 通用化 (25)
    general_score = 25  # Start full
    if contains_org_name(content, ["小米", "阿里", "字节"]):
        general_score -= 5
    if contains_internal_pronouns(content, ["我们公司", "我们项目"]):
        general_score -= 5
    if is_duplicate_of_existing(content):
        general_score = 0  # Duplicate fails completely

    breakdown["general"] = max(general_score, 0)
    score += breakdown["general"]

    # 4. 脱敏度 (20)
    sensitive_score = 20
    if re.search(r'ghp_[a-zA-Z0-9]{20,}', content):
        sensitive_score -= 10
    if re.search(r'sk-[a-zA-Z0-9]{20,}', content):
        sensitive_score -= 10
    if re.search(r'1[3-9]\d{9}', content):  # Chinese phone
        sensitive_score -= 10
    if re.search(r'[\w.]+@[\w.]+\.[a-z]{2,}', content):  # email
        sensitive_score -= 5
    if re.search(r'\.(internal|corp|local)', content):
        sensitive_score -= 5

    breakdown["sensitive"] = max(sensitive_score, 0)
    score += breakdown["sensitive"]

    return {
        "score": score,
        "breakdown": breakdown,
        "grade": "A" if score >= 85 else "B" if score >= 75 else "C" if score >= 60 else "D"
    }
```

## 已用本体系重评分（v0.3.0）

| Lesson | 源分 | 细节 | 通用 | 脱敏 | 总分 | 评级 |
|---|---|---|---|---|---|---|
| 06 git push 403 | 28 (own-git) | 23 | 25 | 20 | **96** | A |
| 07 uv venv --seed | 28 (own-install) | 25 | 25 | 20 | **98** | A |
| 08 pip HTTPS_PROXY | 28 (own-install) | 22 | 25 | 20 | **95** | A |
| 09 V2EX show.json | 18 (forum-50reply) | 22 | 25 | 20 | **85** | A |
| 10 doctor baseline | 22 (own-test+doc) | 18 | 22 | 20 | **82** | B |
| 01 vibe coding team | 18 (forum-93reply) | 22 | 22 | 20 | **82** | B |
| 02 AI code review | 18 (forum-68reply) | 22 | 22 | 20 | **82** | B |
| 03 AI cost baseline | 18 (forum-130reply) | 20 | 15 | 20 | **73** | C (主题外) |
| 04 API relay risk | 22 (forum+own) | 23 | 22 | 16 | **83** | B |
| 05 vless reality blocked | 22 (forum+own) | 23 | 22 | 16 | **83** | B |

## v0.1 待办

- 自动评分脚本（score_lesson_source）未实装到 .py —— 标记为下一步
- 已用人工对照估分（按上述规则）
- v0.2 加入 `is_duplicate_of_existing` 检查（扫 misakanet lessons/contrib）

## 节奏守则

克莱恩 00:57：
- "过程描述详尽 + 细节值得推敲" = 评分核心
- "权威开源仓库推荐" = 源可信度关键加分
- 主题类似 misakanet + 75+ 评分门槛 + 可复用 + 泛化 + 脱敏