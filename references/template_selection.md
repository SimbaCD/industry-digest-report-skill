# Template Selection

Use this reference when the user is choosing report style or when AI must adapt writing to a selected HTML template.

List templates:

```powershell
python scripts\industryctl.py templates
```

Select a template for a project:

```powershell
python scripts\industryctl.py select-template --project .\my-digest-project --template chronicle
```

Initialize a project with a template:

```powershell
python scripts\industryctl.py init --project .\my-digest-project --template nocturne
```

## Available Built-In Templates

### `starter`

Minimal conservative HTML starter. Use when the user has not chosen a visual direction or wants to bring their own template.

Writing style:

- neutral;
- compact;
- easy to paste into another layout.

### `chronicle`

Timeline/chronicle layout. Best for:

- policy and regulatory monitoring;
- research digests;
- text-heavy professional updates;
- date-order narratives.

Writing style:

- emphasize chronology and sequence;
- make dates and event progression clear;
- keep item summaries concise but contextual;
- prefer "what changed, when, and why it matters".

### `nocturne`

Magazine-grid layout with a strong lead story. Best for:

- business, finance, legal, or market reviews;
- reports with one or two dominant monthly themes;
- executive-facing H5 outputs.

Writing style:

- select a strong lead article or special report;
- make the monthly guide sharper and more thesis-driven;
- use stronger hierarchy: lead story, featured cards, normal cards;
- key facts should be numeric and visually punchy when available.

## AI Adaptation Rule

Do not write the same JSON/editorial copy blindly for every template. Before AI editing, inspect or select the template and adapt:

- number of lead/special items;
- summary length;
- key-fact density;
- section balance;
- whether a chronological narrative or magazine hierarchy is more appropriate.

The template choice belongs in `config/config.json`:

```json
"template": "chronicle"
```

Templates are copied into the user's project at:

```text
templates/report.html
```

Built-in templates are stored in the package directory:

```text
templates/template-chronicle.html
templates/template-nocturne.html
```
