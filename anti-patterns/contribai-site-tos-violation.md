---
type: Anti-Pattern
key: contribai-site-tos-violation
symptom: |
  改动违反目标站点的服务条款 (ToS), 例如 bypass rate limit / scrape forbidden pages / automated login。Close 关键词: "violates site ToS", "this is illegal scraping", "we don't bypass rate limits"
root_cause: 未读目标站点 ToS / robots.txt, 改动违反 API 使用规范。
trigger_keywords:
  - "violates site ToS"
  - "this is illegal scraping"
  - "we don't bypass rate limits"
  - "robots.txt forbids this"
  - "automated login not allowed"
fix_action: |
  1) 读目标站点 ToS / robots.txt / API docs
  2) 避免 bypass rate limit / captcha / auth
  3) 用官方 API 而非 scraping
  4) User-Agent 标明 bot 身份
source_pr: "KnugiHK/WhatsApp-Chat-Exporter ~15% close 是 ToS, soxoj/maigret ~30%"
prevention: |
  提 PR 前:
  - 读目标站点 ToS
  - 查 robots.txt
  - 用官方 API (避免 scraping)
  - 不 bypass rate limit / captcha / auth
  - User-Agent 标明 bot
learned_at: 2026-07-19
---

## ContribAI 实证 close 数据

- WhatsApp-Chat-Exporter: ~15% close 是 ToS
- maigret: ~30% close 是 site ToS
- 反爬绕过 PR: 几乎必拒 (GitHub DMCA + 法律风险)
- 大型社交平台 (Twitter / Reddit / LinkedIn): 几乎所有 scraping PR 拒

## 反模式特征

1. **未读 ToS** — 直接爬, 不查 robots.txt
2. **Bypass rate limit** — 多线程 + retry storm
3. **Bypass auth** — 用 cookie 池
4. **反 captcha** — OCR / 第三方服务
5. **未用官方 API** — 直接 scrape

## 自检清单

提 PR 前:
- [ ] 读目标站点 ToS
- [ ] 查 robots.txt
- [ ] 用官方 API (有的话)
- [ ] 不 bypass rate limit
- [ ] 不 bypass captcha / auth
- [ ] User-Agent 标明 bot 身份

## 关联

- KnugiHK/WhatsApp-Chat-Exporter profile
- soxoj/maigret profile
