# Contributing

Contributions are welcome if they keep the package generic and privacy-clean.

## Rules

- Do not commit real WeRSS databases, article exports, internal reports, contacts, client names, cookies, tokens, or private public-account IDs.
- Keep scripts standard-library only unless there is a strong reason to add a dependency.
- Keep `SKILL.md` concise. Put details in `references/`.
- Add or update a reference file when changing workflow, template behavior, or render schema.
- Validate with:

```powershell
python scripts\industryctl.py --help
python scripts\industryctl.py templates
python -m py_compile scripts\industryctl.py
```

## Pull Requests

Please explain:

- what workflow gap the change fixes;
- how privacy boundaries are preserved;
- what command or sample was used to verify the change.
