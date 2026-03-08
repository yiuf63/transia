#!/bin/bash
# Transia Professional Nuitka Build Script
set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Starting Transia Native Compilation (Nuitka)...${NC}"

# 1. 准备环境
source venv/bin/activate
pip install -U nuitka zstandard lxml httpx rich typer duckduckgo-search python-dotenv

# 2. 清理旧构建
rm -rf dist/*.build dist/*.onefile-build

# 3. 运行 Nuitka 编译
# --standalone: 独立运行环境
# --onefile: 真正的机器码单文件
# --plugin-enable=pylint-warnings: 代码质量分析
# --include-package=transia: 将整个 core 编译为 C
python3 -m nuitka \
    --standalone \
    --onefile \
    --include-package=transia \
    --follow-imports \
    --output-dir=dist \
    --output-filename=transia \
    --show-progress \
    src/transia/main.py

echo -e "${GREEN}✅ Build Complete!${NC}"
echo -e "${BLUE}📦 Binary Location: ${NC}dist/transia"
echo -e "${BLUE}⚡ Performance Note: ${NC}This binary is natively compiled. It starts instantly and executes faster than standard Python."
