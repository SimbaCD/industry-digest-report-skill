# Industry Digest Report Skill

Configurable Codex skill and helper scripts for building public-account industry digest reports from a local WeRSS full-text pool.

This is an early `v0.1` package. Expect small breaking changes while the render contract and templates stabilize.

The workflow is intentionally local-first:

1. WeRSS collects public-account metadata and full text.
2. `industryctl.py` inspects local WeRSS data and exports repair targets or ready candidates.
3. An AI agent or human editor creates `validated_items.json`.
4. `industryctl.py render` turns validated structured data into an HTML report.

## Requirements

- Python 3.11+
- Docker and Docker Compose, if you want this package to create/run WeRSS locally
- A working WeRSS instance and user-managed public-account subscriptions

Docker and WeRSS are not installed silently. Run `doctor` first and follow the setup guidance in `references/setup_werss.md`.

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

Open WeRSS, add/update your public-account sources, and let WeRSS cache article full text. Then:

```powershell
python ..\industry-digest-report-skill\scripts\industryctl.py stats --project . --period 2026-04
python ..\industry-digest-report-skill\scripts\industryctl.py targets --project . --period 2026-04
python ..\industry-digest-report-skill\scripts\industryctl.py candidates --project . --period 2026-04
```

`stats` reports full-text readiness. `targets` writes a missing-fulltext repair list for refreshing WeRSS; `candidates` writes ready full-text articles for AI or human editorial review.

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

Render a fictional sample without WeRSS:

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
