# Transia

[中文](README.md) | [English](README.en.md)

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Build: Nuitka](https://img.shields.io/badge/build-native_binary-orange.svg)](https://nuitka.net/)

Transia 是一个面向阅读场景的 AI 书籍翻译工具，支持 EPUB / SRT。

## 项目目的

这个项目想解决两个现实问题：

1. 读者在跨语言阅读时，尽量不被译者风格“二次加工”干扰，更直接理解原文信息。  
2. 一些书在传统翻译出版中会因为审核因素出现删减。遇到这类内容时，找到原文并用本项目翻译，通常更接近原始信息。

## 核心能力

- 自进化术语表：自动学习并统一术语，减少同一本书里前后译法漂移。
- 分治重试：当模型漏译或分段不齐时自动拆分重试，提高完整度。
- 断点续跑：基于缓存避免重复翻译，长书中断后可继续。
- 上下文增强：支持背景搜索与滚动摘要，改善长文本一致性。
- 输出安全：CLI 会校验输入/输出格式，避免生成错误后缀文件。

## 快速开始

```bash
# 1) 安装
pip install -e .

# 2) 添加一个引擎配置（以 OpenAI 兼容接口为例）
transia config add mimo --engine openai --model mimo-v2-flash --api-key YOUR_KEY --endpoint https://api.xiaomimimo.com/v1

# 3) 翻译 EPUB（双语）
transia translate input.epub output.epub --profile mimo --bilingual --search --summarize

# 4) 翻译 SRT（仅译文）
transia translate input.srt output.srt --profile mimo --single
```

## 常用参数

- `--target` / `-t`：目标语言代码（如 `zh`, `en`, `ja`）
- `--profile` / `-p`：使用 `config.json` 中的引擎配置
- `--single`：只输出译文（默认双语）
- `--search`：启用背景信息搜索
- `--summarize`：启用滚动摘要增强
- `--concurrency` / `-c`：并发数（默认 5）

## 质量检查（发布前）

```bash
pytest -q
mypy src/transia
```

## 发布二进制

```bash
./build_release.sh
```

构建产物在 `dist/` 目录。

## License

[AGPL-3.0](LICENSE)
