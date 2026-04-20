# Development

## Setup

```bash
python3.14 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
```

## Tests

Unit tests are deterministic and run without network:

```bash
.venv/bin/pytest
```

After building, install the wheel into a fresh virtual environment before
release:

```bash
.venv/bin/python -m build
tmpdir="$(mktemp -d)"
python3.14 -m venv "$tmpdir/venv"
"$tmpdir/venv/bin/python" -m pip install dist/purl2repo-2.0.0-py3-none-any.whl
"$tmpdir/venv/bin/purl2repo" parse pkg:pypi/requests
```

Live tests are separate:

```bash
.venv/bin/pytest tests/integration -m integration
```

## Fixtures

Fixtures live under `tests/fixtures`. Keep them small, readable, and focused on
metadata fields used by adapters.

## Adding Ecosystems Or Hosts

Add one adapter, register it in `resolution/engine.py`, update tests, and update
the docs. Avoid changes to the public model contract unless preparing a major
version.

For ecosystem adapters, expose fallback scraping targets with
`fallback_scrape_pages()` only when the pages are package/project pages or URLs
already present in structured metadata. Do not add recursive crawling or broad
domain scraping.
