# Staged Workflow

The user-facing experience can be one request:

```text
Please make the April 2026 industry digest for this theme.
```

Internally, run checkpoints:

1. Confirm period and theme.
2. Confirm or select an HTML template. Read `template_selection.md` when needed.
3. Run `industryctl doctor`.
4. If Docker/WeRSS is missing, read `setup_werss.md`.
5. Ask the user to refresh/update public accounts in WeRSS.
6. Run `industryctl stats`.
7. If ready full text is too sparse, run `industryctl targets` and ask the user to repair/cache those targets in WeRSS.
8. When ready full text is enough, run `industryctl candidates`.
9. AI or a human editor creates `validated_items.json`; read `render_contract.md` when needed.
10. Render the report using the user's chosen template.
11. Prepare H5/download/QR publishing assets.

## User Action Checkpoints

Pause and ask the user when:

- Docker installation requires admin approval.
- WeRSS requires QR authorization, login, captcha, or account selection.
- The public-account list is missing or ambiguous.
- The user has not selected a template and multiple templates are available.
- Full-text readiness is too low for a formal digest.
- The user must approve a theme, source list, or final item count.

## Context Control

Do not load every article into context. Use scripts to write:

- stats;
- target lists;
- candidates;
- validated item schema;
- run state;
- QA reports.

Read only the current manifest, target summaries, and selected full-text items needed for AI editorial work.

## Minimal Closed Loop

The script-supported closed loop is:

```text
doctor -> stats -> targets if needed -> candidates -> validated_items.json -> render
```

`validated_items.json` is intentionally the AI/human editorial handoff. This keeps the package vendor-neutral and usable inside Codex or other agent environments without hard-coding a specific model API.
