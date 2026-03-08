# Transia

[English](README.en.md) | [中文](README.md)

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Build: Nuitka](https://img.shields.io/badge/build-native_binary-orange.svg)](https://nuitka.net/)

Transia is an AI book translation tool for reading workflows, with support for EPUB and SRT.

## Project Goal

This project focuses on two practical goals:

1. Help readers understand books across languages with minimal stylistic distortion from translation choices.  
2. Some published translations are shortened due to censorship or review constraints. When that happens, translating the original text with this project can preserve more of the original information.

## Core Capabilities

- Self-evolving glossary: learns and unifies key terms across the whole book.
- Divide-and-retry: automatically splits and retries failed segments to improve completeness.
- Resume from cache: avoids paying twice for the same content and supports long-running jobs.
- Context enhancement: optional background search and rolling summaries for consistency.
- Output safety: CLI validates input/output formats to avoid wrong-extension outputs.

## Quick Start

```bash
# 1) Install
pip install -e .

# 2) Add an engine profile (OpenAI-compatible example)
transia config add mimo --engine openai --model mimo-v2-flash --api-key YOUR_KEY --endpoint https://api.xiaomimimo.com/v1

# 3) Translate EPUB (bilingual output)
transia translate input.epub output.epub --profile mimo --bilingual --search --summarize

# 4) Translate SRT (translation-only output)
transia translate input.srt output.srt --profile mimo --single
```

## Common Options

- `--target` / `-t`: target language code (e.g. `zh`, `en`, `ja`)
- `--profile` / `-p`: engine profile from `config.json`
- `--single`: translation-only output (default is bilingual)
- `--search`: enable background search
- `--summarize`: enable rolling-summary enhancement
- `--concurrency` / `-c`: concurrency level (default `5`)

## Quality Checks (Before Release)

```bash
pytest -q
mypy src/transia
```

## Build Native Binary

```bash
./build_release.sh
```

Artifacts are generated in `dist/`.

## License

[AGPL-3.0](LICENSE)
