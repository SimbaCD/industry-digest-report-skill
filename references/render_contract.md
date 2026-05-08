# Render Contract

This skill keeps AI editing outside the deterministic script by default, but the handoff must be explicit.

## Candidate Input

Generate ready full-text candidates:

```powershell
python scripts\industryctl.py candidates --project .\my-digest-project --period 2026-04
```

Default output:

```text
outputs/2026-04/candidates.json
```

This file contains ready full text and is intended for AI/editorial review.

To keep the file usable in AI context windows, `content_text` is capped at 8,000 characters per article. Use `content_len`, `content_truncated`, and the source URL/DB record if a full article needs deeper review.

## Validated Items

AI or a human editor should create:

```text
outputs/2026-04/validated_items.json
```

Minimal structure:

```json
{
  "meta": {
    "title": "Industry Digest",
    "subtitle": "Monthly Intelligence Review",
    "organization": "",
    "issue": "1",
    "source_label": "WeRSS local full text",
    "start_date": "2026-04-01",
    "end_date": "2026-04-30"
  },
  "guide": [
    "A short monthly guide paragraph."
  ],
  "sections": [
    "Domestic Updates",
    "International Updates"
  ],
  "articles": [
    {
      "section": "Domestic Updates",
      "title": "Article title",
      "url": "https://example.com/article",
      "source": "Source name",
      "pub_date": "2026-04-01",
      "summary": "A factual summary based on full text.",
      "key_facts": [
        {"label": "Investment", "value": "100M", "context": "Project amount"}
      ],
      "visual_blocks": [
        {"type": "Policy", "title": "Key points", "items": ["Point 1", "Point 2"]}
      ],
      "note": "Optional general issue-spotting note."
    }
  ],
  "about": [
    "Optional publication description."
  ],
  "contacts": []
}
```

## Render

Render HTML:

```powershell
python scripts\industryctl.py render --project .\my-digest-project --period 2026-04
```

Default output:

```text
outputs/2026-04/report.html
```

Use `--input` and `--output` to override paths.

## Sample

A fictional sample is included at:

```text
examples/sample_validated_items.json
```

Copy it to `outputs/<period>/validated_items.json` to test `render` without WeRSS data.
