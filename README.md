# purl2repo

[![CI](https://github.com/tonylturner/purl2repo/actions/workflows/ci.yml/badge.svg)](https://github.com/tonylturner/purl2repo/actions/workflows/ci.yml)
[![Integration](https://github.com/tonylturner/purl2repo/actions/workflows/integration.yml/badge.svg)](https://github.com/tonylturner/purl2repo/actions/workflows/integration.yml)
[![Release](https://img.shields.io/badge/release-v2.0.1-blue.svg)](https://github.com/tonylturner/purl2repo/blob/main/docs/releases/v2.0.1.md)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://github.com/tonylturner/purl2repo/blob/main/pyproject.toml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](https://github.com/tonylturner/purl2repo/blob/main/LICENSE)
[![Typed](https://img.shields.io/badge/typed-py.typed-blue.svg)](https://typing.python.org/en/latest/spec/distributing.html)
[![Trivy](https://img.shields.io/badge/trivy-no_high_or_critical_vulns-brightgreen.svg)](https://github.com/tonylturner/purl2repo/actions/workflows/ci.yml)

`purl2repo` resolves Package URLs (PURLs) to canonical repositories and optional
version references. It is built for automation that needs a clear answer plus
confidence, evidence, warnings, and candidate details.

Repositories are not assumed to be GitHub projects. A result can point to source
code, a VCS URL, a generic URL, or an artifact hub such as Hugging Face.

## Features

- Python API and `purl2repo` CLI.
- Typed dataclass results with stable JSON serialization.
- Evidence, warnings, confidence, and candidate scoring.
- Repository URL validation when network is available.
- Conservative release, tag, source, package, and revision links.
- Structured metadata first, deps.dev third-party fallback second, bounded HTML
  fallback only when needed.

## Supported PURL Types

Full metadata-backed resolution:

- `pkg:pypi`
- `pkg:npm`
- `pkg:cargo`
- `pkg:maven`
- `pkg:nuget`
- `pkg:golang`

Direct or explicit repository resolution:

- `pkg:github`
- `pkg:bitbucket`
- `pkg:generic`
- `pkg:huggingface`
- `pkg:mlflow`

See
[docs/ecosystems.md](https://github.com/tonylturner/purl2repo/blob/main/docs/ecosystems.md)
for exact behavior by ecosystem and PURL type.

## Installation

```bash
pip install purl2repo
```

Requires Python 3.11 or newer.

## Quickstart

```python
from purl2repo import resolve

result = resolve("pkg:pypi/requests@2.31.0")

print(result.repository_url)
print(result.repository_kind)
print(result.confidence)
print(result.evidence)
```

Reusable resolver:

```python
from purl2repo import Resolver

with Resolver(timeout=15.0, use_cache=True) as resolver:
    results = list(
        resolver.resolve_many(
            [
                "pkg:pypi/requests@2.31.0",
                "pkg:npm/react@18.2.0",
                "pkg:huggingface/distilbert-base-uncased@043235d6088ecd3dd5fb5ca3592b6913fd516027",
            ]
        )
    )
```

## CLI

```bash
purl2repo parse pkg:pypi/requests@2.31.0
purl2repo resolve pkg:pypi/requests@2.31.0
purl2repo resolve pkg:huggingface/distilbert-base-uncased@043235d6088ecd3dd5fb5ca3592b6913fd516027
purl2repo repo pkg:npm/react
purl2repo release pkg:cargo/rand@0.8.5
purl2repo supports
purl2repo version
```

JSON and trace output:

```bash
purl2repo resolve pkg:pypi/requests@2.31.0 --json --pretty
purl2repo resolve pkg:npm/react@18.2.0 --trace
```

See [docs/cli.md](https://github.com/tonylturner/purl2repo/blob/main/docs/cli.md)
for all commands, flags, and exit codes.

## Output

`resolve()` returns a `ResolutionResult`.

The main fields are:

- `canonical_repository`: full `RepositoryRef` with URL, kind, platform, host,
  namespace, name, confidence, and reasons.
- `repository_url`: convenience URL for the canonical repository.
- `repository_kind`: `source_code`, `artifact_hub`, `vcs`, `generic`, or related
  repository class.
- `version_reference`: verified or inferred version-specific link when available.
- `confidence`, `evidence`, `warnings`, and `repository_candidates`.

See [docs/api.md](https://github.com/tonylturner/purl2repo/blob/main/docs/api.md),
[docs/scoring.md](https://github.com/tonylturner/purl2repo/blob/main/docs/scoring.md),
and
[docs/architecture.md](https://github.com/tonylturner/purl2repo/blob/main/docs/architecture.md)
for the full contract.

## Examples

Hugging Face resolves to Hugging Face as the canonical artifact hub, even when a
PURL qualifier points elsewhere:

```bash
purl2repo resolve 'pkg:huggingface/microsoft/deberta-v3-base@559062ad13d311b87b2c455e67dcd5f1c8f65111?repository_url=https://hub-ci.huggingface.co'
```

Generic PURLs use explicit qualifiers:

```bash
purl2repo resolve 'pkg:generic/example@1.0.0?vcs_url=git+https://github.com/org/repo.git'
```

MLflow PURLs need an explicit registry or tracking endpoint:

```bash
purl2repo resolve 'pkg:mlflow/trafficsigns@10?repository_url=https://adb-5245952564735461.0.azuredatabricks.net/api/2.0/mlflow'
```

Versionless PURLs are valid:

```bash
purl2repo resolve pkg:pypi/requests
```

## Documentation

- [Architecture](https://github.com/tonylturner/purl2repo/blob/main/docs/architecture.md)
- [API](https://github.com/tonylturner/purl2repo/blob/main/docs/api.md)
- [CLI](https://github.com/tonylturner/purl2repo/blob/main/docs/cli.md)
- [Ecosystems](https://github.com/tonylturner/purl2repo/blob/main/docs/ecosystems.md)
- [PURL support](https://github.com/tonylturner/purl2repo/blob/main/docs/purls.md)
- [Scoring](https://github.com/tonylturner/purl2repo/blob/main/docs/scoring.md)
- [Migration from v1](https://github.com/tonylturner/purl2repo/blob/main/docs/migration.md)
- [Development](https://github.com/tonylturner/purl2repo/blob/main/docs/development.md)
- [Release process](https://github.com/tonylturner/purl2repo/blob/main/docs/release-process.md)

## Development

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy
.venv/bin/pytest
```

Live integration tests are separate:

```bash
.venv/bin/pytest tests/integration -m integration --no-cov
```

See
[CONTRIBUTING.md](https://github.com/tonylturner/purl2repo/blob/main/CONTRIBUTING.md)
and
[docs/development.md](https://github.com/tonylturner/purl2repo/blob/main/docs/development.md)
for contributor guidance.

## License

Apache-2.0. See
[LICENSE](https://github.com/tonylturner/purl2repo/blob/main/LICENSE).
