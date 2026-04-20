# Development

## Setup

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
```

## Tests

Unit tests are deterministic and run without network:

```bash
.venv/bin/pytest --cov=purl2repo --cov-report=term-missing --cov-fail-under=90
```

After building, install the wheel into a fresh virtual environment before
release:

```bash
.venv/bin/python -m build
.venv/bin/twine check dist/*
tmpdir="$(mktemp -d)"
python3.11 -m venv "$tmpdir/venv"
"$tmpdir/venv/bin/python" -m pip install dist/purl2repo-2.0.1-py3-none-any.whl
"$tmpdir/venv/bin/purl2repo" parse pkg:pypi/requests
```

Live tests are separate:

```bash
.venv/bin/pytest tests/integration -m integration
```

Integration runs intentionally do not enforce the unit-test coverage threshold.
They are live service checks, not coverage-measurement runs.

## Fixtures

Fixtures live under `tests/fixtures`. Keep them small, readable, and focused on
metadata fields used by adapters.

Official upstream PURL type examples for supported types live under
`tests/fixtures/purl_spec`. They are copied from the `package-url/purl-spec`
`tests/types` fixtures and are exercised by `tests/unit/test_purl_spec_examples.py`.
When adding a new supported PURL type, vendor that type's upstream fixture and
include it in `SUPPORTED_TYPE_FIXTURES`.

To compare those parser fixtures against live repository resolution, run:

```bash
.venv/bin/python scripts/purl_spec_resolution_report.py --verify-release-links
```

The report is informational and always exits successfully. Unresolved upstream
examples are expected because several fixtures are synthetic, stale, private, or
intended only to test PURL canonicalization.

## Adding Ecosystems Or Hosts

For Tier A registry or module ecosystems, add one adapter, register it in
`resolution/engine.py`, update tests, and update the docs. Avoid changes to the
public model contract unless preparing a major version.

For direct-host, generic, or artifact-hub PURL types, update the routing logic in
`ResolutionEngine` instead of forcing the type through an ecosystem adapter.
These types should produce a `RepositoryRef` directly when the PURL already
contains the canonical repository identity.

For ecosystem adapters, expose fallback scraping targets with
`fallback_scrape_pages()` only when the pages are package/project pages or URLs
already present in structured metadata. Do not add recursive crawling or broad
domain scraping.
