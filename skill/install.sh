#!/bin/bash
# PR Genius Skill Installer
# 一键安装 pr-genius skill 到 Claude Code

set -e

echo "🔧 Installing PR Genius Skill..."

# 检查 Claude Code 是否安装
if ! command -v claude &> /dev/null; then
    echo "❌ Claude Code not found. Please install Claude Code first."
    exit 1
fi

# 创建 skills 目录（如果不存在）
SKILLS_DIR="$HOME/.claude/skills/pr-genius"
mkdir -p "$SKILLS_DIR"

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 复制文件
echo "📁 Copying files to $SKILLS_DIR..."
cp "$SCRIPT_DIR/pr_genius.py" "$SKILLS_DIR/"
cp "$SCRIPT_DIR/skill.md" "$SKILLS_DIR/SKILL.md"

# 复制知识库
KNOWLEDGE_BASE="$(dirname "$SCRIPT_DIR")"
if [ -d "$KNOWLEDGE_BASE/anti-patterns" ]; then
    echo "📚 Copying anti-patterns..."
    cp -r "$KNOWLEDGE_BASE/anti-patterns" "$SKILLS_DIR/"
fi

if [ -d "$KNOWLEDGE_BASE/success-patterns" ]; then
    echo "📚 Copying success patterns..."
    cp -r "$KNOWLEDGE_BASE/success-patterns" "$SKILLS_DIR/"
fi

# 创建符号链接到知识库（可选）
echo "🔗 Creating symlink to knowledge base..."
ln -sf "$KNOWLEDGE_BASE" "$SKILLS_DIR/knowledge-base"

echo ""
echo "✅ PR Genius Skill installed successfully!"
echo ""
echo "📖 Usage:"
echo "  /pr-genius eval \"feat: add error handler\" --repo vitejs/vite"
echo "  /pr-genius suggest \"feat: add error handler\" --repo vitejs/vite"
echo "  /pr-genius describe \"feat: add error handler\" --repo vitejs/vite --issue vitejs/vite#1234"
echo ""
echo "📚 Knowledge base: $KNOWLEDGE_BASE"
echo "📁 Skill location: $SKILLS_DIR"
