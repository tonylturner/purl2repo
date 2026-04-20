# purl2repo

`purl2repo` resolves Package URLs (PURLs) to canonical source repositories and, when a
version is present, a best-effort release, tag, or source link. It is designed for
automation where the answer needs to include evidence, confidence, and alternatives.

## Features

- Parses and validates Package URLs without requiring a version.
- Resolves repositories for PyPI, npm, Cargo, and Maven packages.
- Normalizes GitHub, GitLab, Bitbucket, SSH, `git+https`, and generic git URLs.
- Produces typed Python models and stable JSON output.
- Scores every repository candidate with human-readable reasons.
- Includes evidence, warnings, metadata sources, and confidence in every result.
- Optionally verifies inferred release links with cached host checks.
- Uses bounded HTML scraping only as a strict fallback when structured metadata
  does not yield a usable repository candidate.
- Provides both a Python API and a Typer-based CLI.

## Supported Ecosystems And Hosts

Supported ecosystems:

- PyPI via the PyPI JSON API
- npm via the npm registry API
- Cargo via crates.io
- Maven via Maven Central POM and metadata files

Recognized hosts:

- GitHub
- GitLab
- Bitbucket
- Generic git hosts for conservative repository normalization

Future ecosystem extension points are prepared for NuGet, Go modules, RubyGems,
Packagist, and Hex.

## Installation

```bash
pip install purl2repo
```

For local development:

```bash
python3.14 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
```

## Quickstart

```python
from purl2repo import resolve

result = resolve("pkg:pypi/requests@2.31.0")
print(result.repository_url)
print(result.release_link.url if result.release_link else None)
print(result.confidence)
print(result.evidence)
```

## Python API

```python
from purl2repo import Resolver, parse_purl, resolve_repository

parsed = parse_purl("pkg:npm/%40types/node")
print(parsed.namespace, parsed.name)

repo_result = resolve_repository("pkg:cargo/rand")
print(repo_result.repository_url)

resolver = Resolver(timeout=15.0, use_cache=True, strict=False)
results = list(
    resolver.resolve_many(
        [
            "pkg:pypi/requests@2.31.0",
            "pkg:npm/react@18.2.0",
        ]
    )
)
resolver.close()
```

Release links are inferred by default. To require a lightweight host check before
returning an inferred release URL:

```python
from purl2repo import resolve

result = resolve("pkg:pypi/requests@2.31.0", verify_release_links=True)
print(result.release_link)
```

Stable top-level functions:

- `parse_purl(purl)`
- `resolve_repository(purl, **kwargs)`
- `resolve_release(purl, **kwargs)`
- `resolve(purl, **kwargs)`
- `Resolver(...).resolve_many(iterable)`

## CLI Examples

```bash
purl2repo parse pkg:pypi/requests@2.31.0
purl2repo resolve pkg:pypi/requests@2.31.0
purl2repo repo pkg:npm/react
purl2repo release pkg:cargo/rand@0.8.5
purl2repo supports
purl2repo version
```

JSON output:

```bash
purl2repo resolve pkg:pypi/requests@2.31.0 --json --pretty
```

Trace candidate scoring:

```bash
purl2repo resolve pkg:npm/react@18.2.0 --trace
```

Useful flags:

- `--strict / --no-strict`
- `--timeout`
- `--no-cache`
- `--cache-dir`
- `--verbose`
- `--trace`
- `--no-network`
- `--verify-release-links / --no-verify-release-links`

CLI exit codes:

- `0`: success
- `2`: invalid input
- `3`: unsupported ecosystem
- `4`: resolution failure
- `5`: network or metadata failure

## Output Format

All API results are `ResolutionResult` dataclasses and can be serialized with
`to_dict()`.

```json
{
  "repository_url": "https://github.com/psf/requests",
  "repository_type": "github",
  "confidence": "high",
  "evidence": [
    "Fetched package metadata from pypi-json",
    "Selected highest scoring repository candidate",
    "Resolved version-specific release link"
  ],
  "warnings": []
}
```

Confidence is mapped from the highest repository candidate score:

- `high`: score >= 90
- `medium`: 65 to 89
- `low`: 35 to 64
- `none`: below 35

## Versionless PURLs

Versionless PURLs are valid. Repository resolution still runs, but release-link
resolution is skipped and the result includes:

```text
Version not supplied; skipped version-specific release resolution
```

## Limitations

- Release links are best-effort and conservative. A missing release link does not
  mean the repository is wrong.
- Release-link verification is opt-in because it adds host HTTP calls. When
  enabled, the resolver checks candidate release, tag, and source URLs in order
  and returns the first reachable URL.
- The resolver uses structured registry metadata first. HTML scraping is a strict
  fallback only, limited to package/project pages and metadata-provided homepage
  URLs. It is not a crawler, and scraped candidates are capped below clean
  structured metadata.
- Generic git hosts are normalized, but tag and release URLs are not fabricated.
- `--no-network` requires cached metadata; otherwise non-strict calls return a
  partial result with warnings.

## Development

```bash
python3.14 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy
.venv/bin/pytest
.venv/bin/python -m build
tmpdir="$(mktemp -d)"
python3.14 -m venv "$tmpdir/venv"
"$tmpdir/venv/bin/python" -m pip install dist/purl2repo-2.0.0-py3-none-any.whl
"$tmpdir/venv/bin/purl2repo" version
```

Live integration tests are separate:

```bash
.venv/bin/pytest tests/integration -m integration
```

## Release Overview

1. Update `src/purl2repo/version.py` and `pyproject.toml`.
2. Update `CHANGELOG.md`.
3. Run lint, typecheck, tests, and build.
4. Install the built wheel in a fresh virtual environment and smoke-test the CLI.
5. Publish to TestPyPI with the release workflow.
6. Tag `v2.0.0` or publish a GitHub release to trigger PyPI publishing.

## Migration From v1

v2 is a clean break from the prototype API:

- Loose dict output is replaced by typed dataclasses.
- `get_source_repo_and_release()` is replaced by `resolve()`,
  `resolve_repository()`, and `resolve_release()`.
- `github_repo` and `vcs_repo` are replaced by the consistent
  `repository_url` field.
- CLI usage is now command-based: `purl2repo resolve <PURL>`.
- Versionless PURLs are supported.
- Every result includes confidence, evidence, warnings, candidates, and metadata
  source information.

## License

Apache-2.0. See `LICENSE`.
