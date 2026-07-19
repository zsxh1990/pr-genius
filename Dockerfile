# Dockerfile for pr-genius MCP server — v1.3.0 Glama private deploy
# 克莱恩 2026-07-19 M4 指示

FROM python:3.12-slim

# 标签 — 给 Glama 目录展示用
LABEL maintainer="zsxh1990 <445655361@qq.com>"
LABEL project="pr-genius"
LABEL version="1.3.0"
LABEL description="Evidence-backed PR contribution advisor MCP — local-only, read-only, OKF v0.1 compliant"
LABEL license="MIT"

# 安全 + 体积优化
RUN groupadd -r prgenius && useradd -r -g prgenius prgenius && \
    apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. 装 prgenius-core（std-only 主包）
COPY prgenius/ ./prgenius/
COPY pyproject.toml README.md CHANGELOG.md LICENSE ./

# 2. 装 stdlib-only 主包
RUN pip install --no-cache-dir ./prgenius

# 3. 装 MCP extras (可选, prgenius-core[mcp])
RUN pip install --no-cache-dir "mcp>=1.0"

# 4. 复制知识包数据 (OKF bundle — markdown 仓画像 + case study + anti-pattern)
COPY index.md validate.py ./
COPY anti-patterns/ ./anti-patterns/
COPY success-patterns/ ./success-patterns/
COPY docs/ ./docs/
COPY *.md ./*.md ./ 2>/dev/null || true
COPY [A-Z]*-*/ [a-z]*-*/ 2>/dev/null || true
COPY Ikalus1988-MisakaNet/ ./Ikalus1988-MisakaNet/ 2>/dev/null || true
COPY NousResearch-hermes-agent/ ./NousResearch-hermes-agent/ 2>/dev/null || true
COPY pallets-flask/ pandas-dev-pandas/ marimo-team-marimo/ astral-sh-ty/ \
     koala73-worldmonitor/ soxoj-maigret/ HolmesGPT-holmesgpt/ \
     KnugiHK-WhatsApp-Chat-Exporter/ PharMolix-OpenBioMed/ vugu-vugu/ \
     openclaw-openclaw/ ./ 2>/dev/null || true

# 5. 安全 + 只读
USER prgenius

# 6. 健康检查 (--help 应该秒回)
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -m prgenius --version || exit 1

# 7. 入口: stdio MCP server
ENTRYPOINT ["python", "-m", "prgenius", "mcp", "serve"]

# Glama 部署: stdio transport (Claude Code / Cursor / Cline 默认)
# 验证: docker run --rm -i pr-genius:latest < /dev/null 应该返回 MCP handshake
