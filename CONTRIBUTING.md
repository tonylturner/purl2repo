# Contributing

## Local Setup

```bash
python3.14 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
```

Use the repository `.venv` for Python commands.

## Quality Checks

```bash
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy
.venv/bin/pytest
.venv/bin/python -m build
```

Normal unit tests must not use the network. Put live registry checks under
`tests/integration` and mark them with `@pytest.mark.integration`.

## Adding An Ecosystem

1. Add an adapter under `src/purl2repo/ecosystems/`.
2. Subclass `EcosystemResolver`.
3. Fetch structured metadata first.
4. Extract `RepositoryCandidate` objects with clear source labels.
5. Register the adapter in `resolution/engine.py`.
6. Add fixtures, unit tests, integration tests, and docs.

## Adding A Host Adapter

1. Add an adapter under `src/purl2repo/hosts/`.
2. Implement repository normalization and conservative release-link inference.
3. Register the host in `resolution/engine.py`.
4. Add URL normalization and release-link tests.

## Fixture Guidance

Fixtures should be small sanitized registry payloads. Include enough fields to
exercise repository extraction, ambiguity, and release-link behavior without
coupling tests to live services.

## Release Etiquette

- Keep version metadata in `pyproject.toml` and `src/purl2repo/version.py` in
  sync.
- Update `CHANGELOG.md` for every release.
- Run all local checks before tagging.
- Publish through the GitHub Actions workflows rather than long-lived tokens.
