# Theme Configuration

Use a theme file to make the skill reusable across industries.

Default location:

```text
themes/default.json
```

Example:

```json
{
  "name": "default",
  "display_name": "Industry Digest",
  "description": "A configurable public-account industry digest.",
  "keywords": ["industry", "policy", "market"],
  "strong_keywords": ["regulation", "project", "investment"],
  "negative_keywords": ["recruitment", "training", "livestream"],
  "sections": [
    "Domestic Updates",
    "Regional Updates",
    "International Updates",
    "Policy and Regulation",
    "Professional Updates"
  ],
  "summary_chars": [160, 240],
  "max_final_items": 100
}
```

## Rules

- Keep the file generic and user-editable.
- Do not commit private public-account IDs, personal contacts, credentials, or internal organization names in a published theme.
- Prefer keyword lists that help prefilter, not keyword lists that pretend to replace editorial judgment.
- AI performs final selection after full text is available.

## Source Configuration

Source account IDs belong in `config/config.json`, not in this public skill package. The generated example uses an empty list:

```json
"tracked_mp_ids": []
```

Users should fill in their own WeRSS feed/account IDs locally.

## Template Configuration

The selected template also belongs in `config/config.json`:

```json
"template": "chronicle",
"templates_dir": "templates"
```

Theme and template are separate:

- theme controls topic, keywords, sections, and editorial relevance;
- template controls visual hierarchy and writing emphasis.

For example, the same "mining" or "healthcare" theme can use either a chronological template or a magazine-grid template depending on the publication goal.
