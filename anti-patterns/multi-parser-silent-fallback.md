---
type: Anti-Pattern
key: multi-parser-silent-fallback
tags: [parsing, error-handling, robustness, multi-format]
description: "多格式解析器静默返回空结果而非异常，导致 fail-fast 链永远停在第一步"
symptom: "try-first-parser pattern returns empty results instead of falling through to other parsers"
trigger_keywords:
  - "parse_google"
  - "parse_numpy"
  - "parse_sphinx"
  - "multi-format"
  - "best-match"
  - "silent return"
  - "empty result"
fix_action: "1) 不要用 fail-fast (try/except) 链；2) 试所有解析器，取返回结果最多的；3) 用 best-match 策略替代 first-match"
source_pr: "modelcontextprotocol/python-sdk#3350"
severity: medium
evidence:
  - "python-sdk #226: griffe parse_google 在非 Google 格式上静默返回空，numpy/sphinx 永远不会被尝试"
created: 2026-08-18
learned_at: 2026-08-18
source_url: https://github.com/modelcontextprotocol/python-sdk/pull/3350
confidence: high

---

## 反模式说明

很多解析库（docstring 解析器、配置解析器、序列化器等）采用"尽力解析"哲学：输入不匹配时返回空结果，而不是抛异常。

### 错误模式

```python
# ❌ fail-fast 链：永远停在第一步
def parse_multi_format(text):
    for parser in [parse_format_a, parse_format_b, parse_format_c]:
        try:
            return parser(text)  # 格式A不匹配时返回 {}，不会抛异常
        except Exception:
            continue
    return {}
```

### 正确模式

```python
# ✅ best-match：试所有，取最好的
def parse_multi_format(text):
    best = {}
    for parser in [parse_format_a, parse_format_b, parse_format_c]:
        result = parser(text)
        if len(result) > len(best):
            best = result
    return best
```

### 触发条件

- 解析器设计哲学是"尽力而为"而非"严格校验"
- 输入格式不确定，可能是多种格式之一
- 使用 try/except 作为格式检测手段

### 影响

- 功能静默降级：只解析第一种格式，其他格式的输入被当作"无数据"
- 难以发现：没有异常，没有日志，只是结果为空
- 测试盲区：如果测试只用第一种格式，永远发现不了

### 扩展

适用于任何"多格式输入 + 尽力解析"场景：
- 配置文件解析（YAML/TOML/JSON）
- 序列化格式检测
- 多语言文档解析
- 模板引擎回退链
