# Editorial Rules

Use these rules when AI performs final selection and writing.

## Collection vs. Editorial Judgment

Scripts may:

- inspect local WeRSS data;
- filter by date/source/theme keywords;
- mark full-text readiness;
- generate candidate and repair-target lists;
- render validated structured data.

AI should:

- read full text;
- perform final relevance selection;
- merge duplicates;
- assign sections;
- write summaries;
- extract key facts;
- propose visual information blocks;
- identify general compliance or risk observations when appropriate.
- write the final `validated_items.json` structure described in `render_contract.md`.

Scripts should not pretend that keyword scoring is final editorial selection.

## Full Text Requirement

Formal report items should have usable full text. If full text is missing:

- do not write a formal summary;
- do not infer facts from a title alone;
- do not render it into the formal report body;
- record it as a missing-fulltext or repair-target item.

## Summary Style

Summaries should be factual news briefs, not AI reasoning traces.

Avoid:

- "结合……等信息";
- "后续可重点观察";
- "对……而言，后续重点在于";
- "值得关注" as a substitute for concrete information;
- claims that are not grounded in the article.

## Visual Blocks

"Infographic" means information hierarchy, not decoration. Prefer:

- numbers;
- timelines;
- project facts;
- policy obligations;
- market signals;
- risk/compliance checklists.

## Template Fit

Adapt the editorial output to the selected template:

- Timeline templates need clear dates, sequence, and event progression.
- Magazine-grid templates need a lead story, stronger hierarchy, punchier key facts, and shorter cards for secondary items.
- Conservative starter templates should keep copy neutral and easy to migrate.

If the selected template contains placeholder instructions, treat them as template-local editorial guidance unless they conflict with these safety and full-text rules.

## Compliance Notes

Only write general issue-spotting. Do not provide case-specific legal advice or service-result promises. Do not add compliance notes to pure promotional, award, recruitment, or event items unless the user explicitly asks for an internal risk review.
