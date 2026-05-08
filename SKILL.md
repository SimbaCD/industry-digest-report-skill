---
name: industry-digest-report
description: Build configurable industry-digest reports from a local WeRSS full-text pool. Use when a user wants to set up WeRSS/Docker, configure public-account sources and a topic, refresh article full text, screen articles by date/theme, generate an industry-digest report, or prepare H5/HTML publishing assets without hard-coding a private project.
---

# Industry Digest Report

Use this skill to build configurable industry-digest reports from local, user-controlled sources. It is a general version of a monthly public-account digest workflow: WeRSS prepares article metadata and full text; scripts inspect and prefilter local data; AI performs final editorial selection and writing; templates render the final report.

This package must stay privacy-clean. Do not add real private account IDs, user names, phone numbers, email addresses, client names, internal project paths, tokens, cookies, or historical outputs.

## Default Workflow

If the user gives a target period and topic, proceed. If not, ask for:

- target date range, usually `YYYY-MM`;
- topic or theme file;
- public-account source list or WeRSS feed IDs, if not already configured.
- output template, if the project has not already selected one.

Then run the workflow in stages:

1. **Doctor**: check Python, Docker, Docker Compose, project config, and local WeRSS DB.
2. **Setup**: if WeRSS is not installed, guide Docker installation and create a WeRSS compose file.
3. **Refresh**: ask the user to update/cache the relevant public-account articles in WeRSS. Use browser/Web Access only to operate WeRSS UI or inspect state; do not bypass login, QR, captcha, cookies, tokens, or anti-crawl controls.
4. **Stats**: inspect local WeRSS DB for the target period and report full-text readiness.
5. **Targets**: if full text is sparse, generate title-screened repair targets from local WeRSS metadata.
6. **Candidates**: export ready full-text candidates for AI review.
7. **AI Edit**: after enough ready full text exists, AI writes `validated_items.json`. Candidate `content_text` is capped for context safety; use the original source if a specific article needs full re-reading.
8. **Template Fit**: adapt editorial structure to the selected HTML template.
9. **Render/Publish**: render H5/HTML and prepare publishing notes or download assets.

## Commands

From this skill folder or a copied project folder:

```powershell
python scripts\industryctl.py init --project .\my-digest-project
python scripts\industryctl.py templates
python scripts\industryctl.py select-template --project .\my-digest-project --template chronicle
python scripts\industryctl.py doctor --project .\my-digest-project
python scripts\industryctl.py write-werss-compose --project .\my-digest-project
python scripts\industryctl.py stats --project .\my-digest-project --period 2026-04
python scripts\industryctl.py targets --project .\my-digest-project --period 2026-04
python scripts\industryctl.py candidates --project .\my-digest-project --period 2026-04
python scripts\industryctl.py render --project .\my-digest-project --period 2026-04
```

Read references only when needed:

- `references/setup_werss.md`: Docker/WeRSS setup and upgrade guidance.
- `references/theme_config.md`: public, configurable theme format.
- `references/template_selection.md`: choosing and writing for available HTML templates.
- `references/render_contract.md`: structure of `candidates.json` and `validated_items.json`.
- `references/workflow.md`: staged workflow and user-action checkpoints.
- `references/editorial_rules.md`: AI editorial contract.
- `references/privacy_safety.md`: privacy, auth, and anti-crawl boundaries.
- `references/publishing.md`: H5, QR code, download, and WeChat publishing patterns.
- `examples/sample_validated_items.json`: fictional data for testing `render` without WeRSS.

## Safety Boundary

Only use local/self-hosted inputs by default: WeRSS DB/RSS exports, CSV/JSON/Markdown files provided by the user, and project files.

Do not directly scrape WeChat article pages as a hidden default. If the user explicitly requests browser assistance, use Web Access transparently, pause for login/QR/captcha, and never extract, print, reuse, or bypass tokens, cookies, or access controls.

Missing full text is not an AI-writing problem. If there is not enough full text, stop at diagnostics, create repair targets, and ask the user to refresh WeRSS.

## Progressive Disclosure

Keep `SKILL.md` short. Use scripts for deterministic checks and use references for setup/theme/publishing details. Do not load all references for a normal monthly run.
