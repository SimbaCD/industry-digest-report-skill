# Industry Digest Report Skill / 行业动态报告 Skill

[![Release](https://img.shields.io/github/v/release/SimbaCD/industry-digest-report-skill?include_prereleases)](https://github.com/SimbaCD/industry-digest-report-skill/releases)
[![License: MIT](https://img.shields.io/github/license/SimbaCD/industry-digest-report-skill)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/SimbaCD/industry-digest-report-skill?style=social)](https://github.com/SimbaCD/industry-digest-report-skill/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/SimbaCD/industry-digest-report-skill?style=social)](https://github.com/SimbaCD/industry-digest-report-skill/forks)

English | [中文](#中文说明)

Configurable Codex skill and pure-stdlib Python CLI for building public-account industry digest reports from a local WeRSS full-text pool.

This is an early `v0.1` package. Expect small breaking changes while the render contract and templates stabilize.

## What It Does

The workflow is intentionally local-first:

1. WeRSS collects public-account metadata and full text.
2. `industryctl.py` inspects local WeRSS data and exports repair targets or ready candidates.
3. An AI agent or human editor creates `validated_items.json`.
4. `industryctl.py render` turns validated structured data into an HTML report.

Use it when you want a repeatable pipeline for monthly or periodic industry digests, especially when the source material is already cached in a self-hosted WeRSS database.

## Requirements

- Python 3.11+
- Docker and Docker Compose, if you want this package to create or run WeRSS locally
- A working WeRSS instance and user-managed public-account subscriptions

Docker and WeRSS are not installed silently. Run `doctor` first and follow `references/setup_werss.md`.

## Quick Start

```powershell
python scripts\industryctl.py init --project .\my-digest-project --template chronicle
python scripts\industryctl.py doctor --project .\my-digest-project
python scripts\industryctl.py write-werss-compose --project .\my-digest-project
```

Start WeRSS:

```powershell
cd .\my-digest-project
docker compose -f docker-compose.werss.yml up -d
```

Open WeRSS, add or update your public-account sources, and let WeRSS cache article full text. Then:

```powershell
python ..\industry-digest-report-skill\scripts\industryctl.py stats --project . --period 2026-04
python ..\industry-digest-report-skill\scripts\industryctl.py targets --project . --period 2026-04
python ..\industry-digest-report-skill\scripts\industryctl.py candidates --project . --period 2026-04
```

`stats` reports full-text readiness. `targets` writes a missing-fulltext repair list for refreshing WeRSS. `candidates` writes ready full-text articles for AI or human editorial review.

Create:

```text
outputs/2026-04/validated_items.json
```

Then render:

```powershell
python ..\industry-digest-report-skill\scripts\industryctl.py render --project . --period 2026-04
```

Output:

```text
outputs/2026-04/report.html
```

## First-Minute Render Demo

Render a fictional sample without WeRSS.

Windows PowerShell:

```powershell
python scripts\industryctl.py init --project .\demo-project --template chronicle
New-Item -ItemType Directory -Force .\demo-project\outputs\2026-04
Copy-Item .\examples\sample_validated_items.json .\demo-project\outputs\2026-04\validated_items.json
python scripts\industryctl.py render --project .\demo-project --period 2026-04
```

macOS/Linux bash or zsh:

```bash
python scripts/industryctl.py init --project ./demo-project --template chronicle
mkdir -p ./demo-project/outputs/2026-04
cp ./examples/sample_validated_items.json ./demo-project/outputs/2026-04/validated_items.json
python scripts/industryctl.py render --project ./demo-project --period 2026-04
```

Switch the same demo to another template:

```powershell
python scripts\industryctl.py select-template --project .\demo-project --template nocturne
python scripts\industryctl.py render --project .\demo-project --period 2026-04
```

For macOS/Linux, use forward slashes in the same commands.

## Templates

List built-in templates:

```powershell
python scripts\industryctl.py templates
```

Available templates:

- `starter`: minimal HTML starter.
- `chronicle`: timeline/chronicle layout for policy, research, and date-order digests.
- `nocturne`: magazine-grid layout for business, financial, legal, and executive-facing reports.

Switch a project:

```powershell
python scripts\industryctl.py select-template --project .\my-digest-project --template nocturne
```

## Star History

The chart below is provided by Star History and shows the repository's GitHub star trend. New repositories may show a mostly empty chart until they receive stars.

<p align="center">
  <a href="https://star-history.com/#SimbaCD/industry-digest-report-skill&Date">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=SimbaCD/industry-digest-report-skill&type=Date&theme=dark" />
      <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=SimbaCD/industry-digest-report-skill&type=Date" />
      <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=SimbaCD/industry-digest-report-skill&type=Date" />
    </picture>
  </a>
</p>

## Project Structure

```text
SKILL.md
README.md
LICENSE
CONTRIBUTING.md
references/
scripts/
templates/
examples/
```

Generated user projects contain their own `config/`, `themes/`, `templates/`, `outputs/`, and optional `werss-data/`.

## Privacy

Do not commit WeRSS data, generated outputs, private source lists, tokens, cookies, or internal report drafts. See `.gitignore` and `references/privacy_safety.md`.

## Scope

This package does not bypass WeChat access controls and does not scrape WeChat pages by default. If a browser is needed, operate only user-controlled WeRSS UI and pause for login, QR code, or captcha.

## 中文说明

[English](#industry-digest-report-skill--行业动态报告-skill) | 中文

这是一个可配置的 Codex Skill 和纯 Python 标准库 CLI，用于基于本地 WeRSS 正文池生成行业动态 HTML/H5 报告。

当前版本是早期 `v0.1`。在 `v1.0` 之前，`validated_items.json` 渲染协议和模板细节可能还会有小幅调整。

## 它能做什么

这个项目采用本地优先流程：

1. WeRSS 负责采集公众号文章元数据和正文缓存。
2. `industryctl.py` 读取本地 WeRSS 数据库，检查正文就绪情况，并导出缺正文修复清单或可编辑候选文章。
3. AI Agent 或人工编辑基于候选文章生成 `validated_items.json`。
4. `industryctl.py render` 按模板把结构化内容渲染成 HTML 报告。

它适合用于月度、季度或专题型行业动态报告，尤其适合已经使用自建 WeRSS 缓存公众号全文的场景。

## 环境要求

- Python 3.11+
- Docker 和 Docker Compose，如果需要由本项目辅助创建或运行 WeRSS
- 一个可用的 WeRSS 实例，以及由用户自行管理的公众号订阅源

本项目不会静默安装 Docker 或 WeRSS。请先运行 `doctor`，再按 `references/setup_werss.md` 完成环境检查和配置。

## 快速开始

```powershell
python scripts\industryctl.py init --project .\my-digest-project --template chronicle
python scripts\industryctl.py doctor --project .\my-digest-project
python scripts\industryctl.py write-werss-compose --project .\my-digest-project
```

启动 WeRSS：

```powershell
cd .\my-digest-project
docker compose -f docker-compose.werss.yml up -d
```

打开 WeRSS，添加或更新公众号来源，并等待 WeRSS 缓存文章正文。然后运行：

```powershell
python ..\industry-digest-report-skill\scripts\industryctl.py stats --project . --period 2026-04
python ..\industry-digest-report-skill\scripts\industryctl.py targets --project . --period 2026-04
python ..\industry-digest-report-skill\scripts\industryctl.py candidates --project . --period 2026-04
```

三个命令的作用不同：

- `stats`：查看指定月份的文章总量和正文就绪率。
- `targets`：输出缺少正文但标题相关的文章清单，用于回到 WeRSS 定向补缓存。
- `candidates`：输出已有正文的候选文章，供 AI 或人工编辑筛选、总结和结构化。

随后创建：

```text
outputs/2026-04/validated_items.json
```

再渲染：

```powershell
python ..\industry-digest-report-skill\scripts\industryctl.py render --project . --period 2026-04
```

输出文件：

```text
outputs/2026-04/report.html
```

## 一分钟渲染演示

不连接 WeRSS，也可以先用虚构样例测试模板渲染。

Windows PowerShell：

```powershell
python scripts\industryctl.py init --project .\demo-project --template chronicle
New-Item -ItemType Directory -Force .\demo-project\outputs\2026-04
Copy-Item .\examples\sample_validated_items.json .\demo-project\outputs\2026-04\validated_items.json
python scripts\industryctl.py render --project .\demo-project --period 2026-04
```

macOS/Linux bash 或 zsh：

```bash
python scripts/industryctl.py init --project ./demo-project --template chronicle
mkdir -p ./demo-project/outputs/2026-04
cp ./examples/sample_validated_items.json ./demo-project/outputs/2026-04/validated_items.json
python scripts/industryctl.py render --project ./demo-project --period 2026-04
```

切换模板：

```powershell
python scripts\industryctl.py select-template --project .\demo-project --template nocturne
python scripts\industryctl.py render --project .\demo-project --period 2026-04
```

macOS/Linux 用户使用同等的正斜杠路径即可。

## 模板

列出内置模板：

```powershell
python scripts\industryctl.py templates
```

当前内置模板：

- `starter`：最小 HTML 起步模板。
- `chronicle`：时间线/编年体版式，适合政策、研究、按时间顺序展开的行业动态。
- `nocturne`：杂志网格版式，适合商业、金融、法律、管理层阅读场景。

切换项目模板：

```powershell
python scripts\industryctl.py select-template --project .\my-digest-project --template nocturne
```

## Star 趋势

下面的图来自 Star History，用于展示本仓库 GitHub stars 随时间的变化。新仓库一开始图表可能比较空，等有 stars 后会自然显示曲线。Fork 数量可以看顶部 GitHub forks 徽章。

<p align="center">
  <a href="https://star-history.com/#SimbaCD/industry-digest-report-skill&Date">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=SimbaCD/industry-digest-report-skill&type=Date&theme=dark" />
      <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=SimbaCD/industry-digest-report-skill&type=Date" />
      <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=SimbaCD/industry-digest-report-skill&type=Date" />
    </picture>
  </a>
</p>

## 项目结构

```text
SKILL.md
README.md
LICENSE
CONTRIBUTING.md
references/
scripts/
templates/
examples/
```

用户生成的项目目录会包含自己的 `config/`、`themes/`、`templates/`、`outputs/`，以及可选的 `werss-data/`。

## 隐私

请不要提交真实 WeRSS 数据库、生成报告、私有公众号列表、token、cookie、内部报告草稿或客户资料。详见 `.gitignore` 和 `references/privacy_safety.md`。

## 范围边界

本项目默认不绕过微信访问控制，也不把直接抓取微信原文页面作为隐藏流程。如果确实需要浏览器辅助，只应透明地操作用户自有 WeRSS UI，并在登录、扫码、验证码等环节暂停交给用户处理。
